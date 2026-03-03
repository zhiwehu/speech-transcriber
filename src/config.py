"""
配置加载模块
"""
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    @property
    def mode(self) -> str:
        """运行模式：online 或 local"""
        return self.config.get('mode', 'online')
    
    @property
    def is_online(self) -> bool:
        return self.mode == 'online'
    
    @property
    def is_local(self) -> bool:
        return self.mode == 'local'
    
    @property
    def online_config(self) -> Dict[str, Any]:
        return self.config.get('online', {})
    
    @property
    def local_config(self) -> Dict[str, Any]:
        return self.config.get('local', {})
    
    @property
    def common_config(self) -> Dict[str, Any]:
        return self.config.get('common', {})
    
    def get_model_path(self, model_type: str) -> str:
        """获取模型路径"""
        if self.is_local:
            return self.local_config.get('models', {}).get(model_type, '')
        return ''
    
    def __repr__(self):
        return f"Config(mode={self.mode}, path={self.config_path})"


# 全局配置实例
_default_config: Config = None


def get_config() -> Config:
    """获取全局配置"""
    global _default_config
    if _default_config is None:
        _default_config = Config()
    return _default_config
