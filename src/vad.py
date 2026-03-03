"""
VAD - 语音活动检测
支持在线和本地两种模式
"""
from typing import List, Tuple
from pathlib import Path
import numpy as np

from .config import get_config


class VADProcessor:
    """语音活动检测处理器"""
    
    def __init__(self):
        self.config = get_config()
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载 VAD 模型"""
        if self.config.is_local:
            # 本地模式：加载 Silero VAD
            try:
                # TODO: 实现本地 Silero VAD 加载
                # model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
                print("[VAD] 本地模式：加载 Silero VAD 模型...")
                self.model = None  # 占位，待实现
            except Exception as e:
                print(f"[VAD] 本地模型加载失败，使用在线模式：{e}")
                self.config.config['mode'] = 'online'
        else:
            # 在线模式：使用阿里云 VAD
            print("[VAD] 在线模式：使用阿里云 VAD 服务")
            self.model = "online"
    
    def detect(self, audio_path: str) -> List[Tuple[float, float]]:
        """
        检测语音活动
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            [(start_time, end_time), ...] 语音片段列表（秒）
        """
        if self.config.is_online:
            return self._detect_online(audio_path)
        else:
            return self._detect_local(audio_path)
    
    def _detect_online(self, audio_path: str) -> List[Tuple[float, float]]:
        """在线 VAD 检测（模拟结果）"""
        print(f"[VAD] 在线检测：{audio_path}")
        # TODO: 调用阿里云 VAD API
        # 这里返回模拟数据用于 MVP 测试
        return [
            (0.0, 5.0),
            (6.0, 12.0),
            (13.0, 20.0),
        ]
    
    def _detect_local(self, audio_path: str) -> List[Tuple[float, float]]:
        """本地 VAD 检测"""
        print(f"[VAD] 本地检测：{audio_path}")
        # TODO: 实现本地 Silero VAD 推理
        return []
    
    def __repr__(self):
        return f"VADProcessor(mode={self.config.mode})"
