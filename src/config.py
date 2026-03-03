"""
配置加载模块
支持 .env 文件和环境变量
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv, find_dotenv


class Config:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        # 加载 .env 文件（支持查找父目录）
        env_path = find_dotenv()
        if env_path:
            load_dotenv(env_path, override=True)
        
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
        
        # 用环境变量覆盖配置
        self._apply_env_overrides()
    
    def _apply_env_overrides(self):
        """使用环境变量覆盖配置"""
        # 运行模式
        if os.getenv('MODE'):
            self.config['mode'] = os.getenv('MODE', 'online')
        
        # 在线配置
        if os.getenv('DASHSCOPE_API_KEY'):
            self.config.setdefault('online', {})['api_key'] = os.getenv('DASHSCOPE_API_KEY')
        
        if os.getenv('OSS_BUCKET'):
            self.config.setdefault('online', {}).setdefault('storage', {})['oss_bucket'] = os.getenv('OSS_BUCKET')
        
        if os.getenv('OSS_ENDPOINT'):
            self.config.setdefault('online', {}).setdefault('storage', {})['oss_endpoint'] = os.getenv('OSS_ENDPOINT')
        
        if os.getenv('OSS_ACCESS_KEY'):
            self.config.setdefault('online', {}).setdefault('storage', {})['oss_access_key'] = os.getenv('OSS_ACCESS_KEY')
        
        if os.getenv('OSS_ACCESS_SECRET'):
            self.config.setdefault('online', {}).setdefault('storage', {})['oss_access_secret'] = os.getenv('OSS_ACCESS_SECRET')
        
        # 本地配置
        if os.getenv('LOCAL_DEVICE'):
            self.config.setdefault('local', {})['device'] = os.getenv('LOCAL_DEVICE', 'cpu')
    
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
