"""
阿里云 OSS 文件上传模块
"""
import oss2
from pathlib import Path
from typing import Optional
import uuid


class OSSUploader:
    """OSS 文件上传器"""
    
    def __init__(self, config: dict):
        """
        初始化上传器
        
        Args:
            config: OSS 配置字典
                - oss_bucket: Bucket 名称
                - oss_endpoint: OSS Endpoint
                - oss_access_key: AccessKey ID
                - oss_access_secret: AccessKey Secret
        """
        self.bucket_name = config.get('oss_bucket', '')
        self.endpoint = config.get('oss_endpoint', '')
        self.access_key = config.get('oss_access_key', '')
        self.access_secret = config.get('oss_access_secret', '')
        
        self.auth = None
        self.bucket = None
        
        if self.access_key and self.access_secret and self.endpoint:
            self.auth = oss2.Auth(self.access_key, self.access_secret)
            self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
    
    def upload(self, file_path: str, object_name: Optional[str] = None, use_signed_url: bool = True, expire_seconds: int = 86400) -> str:
        """
        上传文件到 OSS
        
        Args:
            file_path: 本地文件路径
            object_name: OSS 对象名称（可选，默认使用文件名）
            use_signed_url: 是否使用签名 URL（推荐，用于私有 Bucket）
            expire_seconds: 签名 URL 过期时间（秒），默认 24 小时
            
        Returns:
            文件公网 URL
        """
        if not self.bucket:
            raise Exception("OSS 未配置，请检查配置文件")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在：{file_path}")
        
        # 生成对象名称
        if object_name is None:
            object_name = f"audio/{file_path.name}"
        
        # 上传文件
        print(f"[OSS] 上传文件：{file_path} -> oss://{self.bucket_name}/{object_name}")
        
        try:
            # 上传
            self.bucket.put_object_from_file(object_name, str(file_path))
            print(f"[OSS] ✅ 上传成功")
            
            if use_signed_url:
                # 生成签名 URL
                url = self.bucket.sign_url('GET', object_name, expire_seconds)
                print(f"[OSS] 🔐 签名 URL（{expire_seconds//3600}小时有效）: {url}")
            else:
                # 普通公网 URL（需要 Bucket 是公共读）
                url = f"https://{self.bucket_name}.{self.endpoint}/{object_name}"
                print(f"[OSS] 📎 文件 URL: {url}")
            
            return url
            
        except oss2.exceptions.OssError as e:
            print(f"[OSS] ❌ 上传失败：{e}")
            raise
    
    def upload_with_public_url(self, file_path: str, object_name: Optional[str] = None) -> str:
        """
        上传文件并返回公网可访问 URL
        
        Args:
            file_path: 本地文件路径
            object_name: OSS 对象名称
            
        Returns:
            公网 URL
        """
        url = self.upload(file_path, object_name)
        
        # 如果 Bucket 是私有的，需要生成签名 URL
        # 这里假设 Bucket 是公共读或已配置 CDN
        # 如需签名 URL，使用：
        # url = self.bucket.sign_url('GET', object_name, 3600)  # 1 小时有效期
        
        return url


def upload_file(file_path: str, config: dict) -> str:
    """
    便捷函数：上传文件到 OSS
    
    Args:
        file_path: 文件路径
        config: OSS 配置
        
    Returns:
        文件 URL
    """
    uploader = OSSUploader(config)
    return uploader.upload(file_path)
