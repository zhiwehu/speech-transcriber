"""
ASR - 语音识别
支持在线（阿里云 FunASR）和本地模式
"""
from typing import List, Dict
from pathlib import Path
from dataclasses import dataclass
import os
import json

from .config import get_config


@dataclass
class ASRResult:
    """ASR 识别结果"""
    text: str
    start_time: float
    end_time: float
    confidence: float = 1.0
    speaker: str = ""


class ASRProcessor:
    """语音识别处理器"""
    
    def __init__(self):
        self.config = get_config()
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载 ASR 模型"""
        if self.config.is_local:
            # 本地模式：加载 FunASR
            try:
                print("[ASR] 本地模式：加载 FunASR 模型...")
                # TODO: from funasr import AutoModel
                # self.model = AutoModel(model=self.config.get_model_path('asr'))
                self.model = None  # 占位
            except Exception as e:
                print(f"[ASR] 本地模型加载失败，使用在线模式：{e}")
                self.config.config['mode'] = 'online'
        else:
            # 在线模式：使用阿里云 DashScope SDK
            print("[ASR] 在线模式：使用阿里云 FunASR 服务")
            self.model = "online"
    
    def transcribe(self, audio_path: str, segments: List[tuple] = None) -> List[ASRResult]:
        """
        转录音频
        
        Args:
            audio_path: 音频文件路径
            segments: 可选的语音片段列表 [(start, end), ...]
            
        Returns:
            ASRResult 列表
        """
        if self.config.is_online:
            return self._transcribe_online(audio_path, segments)
        else:
            return self._transcribe_local(audio_path, segments)
    
    def _transcribe_online(self, audio_path: str, segments: List[tuple] = None) -> List[ASRResult]:
        """在线转录 - 调用阿里云 DashScope API"""
        print(f"[ASR] 在线转录：{audio_path}")
        
        api_key = self.config.online_config.get('api_key', '')
        if not api_key:
            print("[ASR] ⚠️ 未配置 API Key，使用模拟数据")
            print("[ASR] 请在 configs/config.yaml 中配置 online.api_key")
            return self._get_mock_results()
        
        try:
            # 1. 上传文件到 OSS
            storage_config = self.config.online_config.get('storage', {})
            if not storage_config.get('oss_bucket'):
                print("[ASR] ⚠️ 未配置 OSS，无法上传文件")
                print("[ASR] 请在 configs/config.yaml 中配置 online.storage")
                return self._get_mock_results()
            
            from .oss_uploader import OSSUploader
            uploader = OSSUploader(storage_config)
            file_url = uploader.upload(audio_path)
            
            # 2. 调用转录 API
            return self._transcribe_with_url(file_url, api_key)
            
        except Exception as e:
            print(f"[ASR] 处理失败：{e}")
            import traceback
            traceback.print_exc()
            return self._get_mock_results()
    
    def _transcribe_with_url(self, file_url: str, api_key: str, max_retries: int = 3) -> List[ASRResult]:
        """使用文件 URL 进行转录（带重试机制）"""
        import time
        from dashscope.audio.asr import Transcription
        import dashscope
        from http import HTTPStatus
        
        dashscope.api_key = api_key
        dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
        
        for attempt in range(max_retries):
            try:
                print(f"[ASR] 📡 提交任务：{file_url} (尝试 {attempt + 1}/{max_retries})")
                
                # 异步提交任务
                task_response = Transcription.async_call(
                    model='fun-asr',
                    file_urls=[file_url]
                )
                
                task_id = task_response.output.task_id
                print(f"[ASR] 🎯 任务 ID: {task_id}")
                
                # 同步等待任务完成
                print("[ASR] ⏳ 等待任务完成...")
                while True:
                    transcribe_response = Transcription.fetch(task=task_id)
                    status = transcribe_response.output.task_status
                    
                    if status == 'SUCCEEDED' or status == 'FAILED':
                        break
                        
                    print(f"   状态：{status}")
                    time.sleep(2)
                
                if transcribe_response.status_code == HTTPStatus.OK:
                    print("[ASR] ✅ 转录完成！")
                    return self._parse_result(transcribe_response.output)
                else:
                    print(f"[ASR] ❌ 任务失败：{transcribe_response.message}")
                    if attempt < max_retries - 1:
                        print(f"[ASR] 重试中...")
                        time.sleep(2 ** attempt)  # 指数退避
                        continue
                    return self._get_mock_results()
                    
            except Exception as e:
                print(f"[ASR] 调用失败（尝试 {attempt + 1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    print(f"[ASR] 重试中...")
                    time.sleep(2 ** attempt)
                else:
                    import traceback
                    traceback.print_exc()
                    return self._get_mock_results()
        
        return self._get_mock_results()
    
    def _parse_result(self, output) -> List[ASRResult]:
        """解析 API 返回结果"""
        results = []
        try:
            import requests
            
            # 获取 transcription_url 并下载结果
            for result_item in output.get('results', []):
                trans_url = result_item.get('transcription_url', '')
                if trans_url:
                    # 下载转录结果
                    trans_response = requests.get(trans_url)
                    if trans_response.status_code == 200:
                        trans_data = trans_response.json()
                        # 解析 transcripts -> sentences
                        for transcript in trans_data.get('transcripts', []):
                            for sentence in transcript.get('sentences', []):
                                results.append(ASRResult(
                                    text=sentence.get('text', ''),
                                    start_time=float(sentence.get('begin_time', 0)) / 1000.0,
                                    end_time=float(sentence.get('end_time', 0)) / 1000.0,
                                ))
        except Exception as e:
            print(f"[ASR] 解析结果失败：{e}")
            import traceback
            traceback.print_exc()
        return results
    
    def _transcribe_local(self, audio_path: str, segments: List[tuple] = None) -> List[ASRResult]:
        """本地转录"""
        print(f"[ASR] 本地转录：{audio_path}")
        # TODO: 实现本地 FunASR 推理
        return []
    
    def _get_mock_results(self) -> List[ASRResult]:
        """返回模拟数据（用于测试）"""
        return [
            ASRResult(text="[模拟数据] 未配置 API Key 或文件未上传到公网 URL", start_time=0.0, end_time=5.0),
            ASRResult(text="[提示] 需要将音频文件上传到阿里云 OSS 或其他公网可访问的存储", start_time=6.0, end_time=10.0),
        ]
    
    def __repr__(self):
        return f"ASRProcessor(mode={self.config.mode})"
