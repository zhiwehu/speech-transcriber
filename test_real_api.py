#!/usr/bin/env python3
"""
测试阿里云 FunASR 真实 API
上传文件到 OSS -> 转录 -> 输出结果
"""
import sys
import os
from pathlib import Path
import json
import time

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import get_config
from asr_realtime import transcribe_with_url, format_result


def upload_to_oss(file_path: str, config: dict) -> str:
    """
    上传文件到阿里云 OSS
    
    Args:
        file_path: 本地文件路径
        config: OSS 配置
        
    Returns:
        文件公网 URL
    """
    import oss2
    import uuid
    
    bucket = config.get('oss_bucket', '')
    endpoint = config.get('oss_endpoint', '')
    api_key = config.get('api_key', '')
    
    if not bucket or not endpoint:
        print("❌ 未配置 OSS Bucket 或 Endpoint")
        print("📝 请在 configs/config.yaml 中配置：")
        print("   online.storage.oss_bucket: your-bucket")
        print("   online.storage.oss_endpoint: oss-cn-beijing.aliyuncs.com")
        return None
    
    # 创建 Auth（使用 API Key 作为 AccessKey）
    # 注意：这里需要 OSS 的 AccessKey/Secret，不是 DashScope API Key
    # 简化方案：使用临时上传服务
    
    print("⚠️  需要配置 OSS AccessKey 和 Secret")
    print("💡 替代方案：")
    print("   1. 手动上传文件到任意图床/文件托管服务")
    print("   2. 使用本地 HTTP 服务器临时暴露文件")
    print("   3. 使用阿里云 OSS 控制台上传")
    
    return None


def start_local_http_server(file_path: str, port: int = 8888) -> str:
    """
    启动本地 HTTP 服务器暴露文件
    
    Args:
        file_path: 文件路径
        port: 端口号
        
    Returns:
        文件 URL
    """
    import threading
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    
    file_dir = str(Path(file_path).parent)
    file_name = Path(file_path).name
    
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=file_dir, **kwargs)
    
    # 在后台启动服务器
    server = HTTPServer(('localhost', port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    url = f"http://localhost:{port}/{file_name}"
    print(f"🌐 本地 HTTP 服务器已启动：{url}")
    
    return url


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='测试阿里云 FunASR API')
    parser.add_argument('-i', '--input', required=True, help='输入音频文件')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('--use-local', action='store_true', help='使用本地 HTTP 服务器（测试用）')
    parser.add_argument('--port', type=int, default=8888, help='本地 HTTP 服务器端口')
    
    args = parser.parse_args()
    
    # 加载配置
    config = get_config()
    api_key = config.online_config.get('api_key', '')
    
    if not api_key:
        print("❌ 未配置 API Key")
        sys.exit(1)
    
    print("🎙️  阿里云 FunASR 语音识别测试")
    print("="*50)
    
    # 获取文件 URL
    file_url = None
    
    if args.use_local:
        # 使用本地 HTTP 服务器
        print("\n📡 启动本地 HTTP 服务器...")
        file_url = start_local_http_server(args.input, args.port)
        print("⚠️  注意：本地服务器仅在本地网络可访问")
        print("   阿里云 API 无法访问本地 URL，此方案仅用于测试")
    else:
        # 需要上传到 OSS
        print("\n📦 需要上传文件到阿里云 OSS")
        oss_config = config.online_config.get('storage', {})
        oss_config['api_key'] = api_key
        file_url = upload_to_oss(args.input, oss_config)
    
    if not file_url:
        print("\n❌ 无法获取文件 URL")
        print("\n💡 建议操作步骤：")
        print("   1. 手动上传音频文件到阿里云 OSS 或其他文件托管服务")
        print("   2. 获取文件公网 URL")
        print("   3. 运行：python3 src/asr_realtime.py -u <URL> -k <API_KEY>")
        sys.exit(1)
    
    # 调用转录 API
    print("\n📝 开始转录...")
    output = transcribe_with_url(file_url, api_key)
    
    if output:
        result = format_result(output)
        print("\n" + "="*50)
        print(result)
        print("="*50)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\n✅ 结果已保存：{args.output}")


if __name__ == '__main__':
    main()
