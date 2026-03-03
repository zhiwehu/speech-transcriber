"""
Speaker Diarization - 说话人分离
支持在线和本地模式
"""
from typing import List, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass

from .config import get_config


@dataclass
class SpeakerSegment:
    """说话人片段"""
    speaker_id: str
    start_time: float
    end_time: float
    embedding: List[float] = None


class SpeakerDiarizer:
    """说话人分离处理器"""
    
    def __init__(self):
        self.config = get_config()
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载说话人分离模型"""
        if self.config.is_local:
            # 本地模式：加载 3D-Speaker + EEND-OLA
            try:
                print("[Speaker] 本地模式：加载 3D-Speaker + EEND-OLA...")
                # TODO: 加载阿里 3D-Speaker 模型
                # TODO: 加载 EEND-OLA 模型
                self.model = None  # 占位
            except Exception as e:
                print(f"[Speaker] 本地模型加载失败，使用在线模式：{e}")
                self.config.config['mode'] = 'online'
        else:
            # 在线模式
            print("[Speaker] 在线模式：使用阿里云说话人分离服务")
            self.model = "online"
    
    def diarize(self, audio_path: str, vad_segments: List[Tuple[float, float]] = None) -> List[SpeakerSegment]:
        """
        说话人分离
        
        Args:
            audio_path: 音频文件路径
            vad_segments: VAD 检测的语音片段
            
        Returns:
            SpeakerSegment 列表
        """
        if self.config.is_online:
            return self._diarize_online(audio_path, vad_segments)
        else:
            return self._diarize_local(audio_path, vad_segments)
    
    def _diarize_online(self, audio_path: str, vad_segments: List[Tuple[float, float]] = None) -> List[SpeakerSegment]:
        """在线说话人分离"""
        print(f"[Speaker] 在线分离：{audio_path}")
        print("[Speaker] ⚠️  当前在线模式不提供准确的说话人分离")
        print("[Speaker] 💡 建议使用本地模式（pyannote.audio）获得准确的说话人分离")
        
        # 返回空列表，让转录器使用统一标签
        return []
    
    def _diarize_local(self, audio_path: str, vad_segments: List[Tuple[float, float]] = None) -> List[SpeakerSegment]:
        """本地说话人分离 - 使用阿里 3D-Speaker"""
        print(f"[Speaker] 本地分离：{audio_path}")
        
        try:
            # 使用阿里 3D-Speaker 模型
            from funasr import AutoModel
            
            # 加载 3D-Speaker 模型
            print("[Speaker] 加载 3D-Speaker 模型...")
            # 模型会自动从 modelscope 下载
            model = AutoModel(model="damo/speech_campplus_sv_zh-cn_16k-common")
            
            # 运行声纹识别
            print("[Speaker] 运行说话人分离...")
            result = model.generate(input=audio_path)
            
            # 解析结果
            segments = []
            # 3D-Speaker 返回的是说话人嵌入和标签
            # 需要结合 VAD 结果生成时间戳
            if result:
                for item in result:
                    segments.append(SpeakerSegment(
                        speaker_id=f"说话人 {item.get('speaker_id', 1)}",
                        start_time=item.get('start_time', 0),
                        end_time=item.get('end_time', 0),
                        embedding=item.get('embedding', None),
                    ))
            
            print(f"[Speaker] ✅ 分离 {len(segments)} 个说话人片段")
            return segments
            
        except ImportError as e:
            print(f"[Speaker] ⚠️  依赖缺失：{e}")
            print("[Speaker] 3D-Speaker 需要 funasr 完整安装")
            return []
        except Exception as e:
            print(f"[Speaker] ❌ 分离失败：{e}")
            import traceback
            traceback.print_exc()
            return []
    
    def __repr__(self):
        return f"SpeakerDiarizer(mode={self.config.mode})"
