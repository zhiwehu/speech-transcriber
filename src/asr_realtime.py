#!/usr/bin/env python3
"""
实时语音识别 - 使用阿里云 FunASR API
支持本地文件上传后识别
"""
import sys
import os
from pathlib import Path
import json
import time

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from dashscope.audio.asr import Transcription
import dashscope
from http import HTTPStatus


def transcribe_file(audio_path: str, api_key: str) -> dict:
    """
    转录单个音频文件
    
    Args:
        audio_path: 音频文件路径
        api_key: 阿里云 API Key
        
    Returns:
        转录结果字典
    """
    # 设置 API Key
    dashscope.api_key = api_key
    dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    
    print(f"📁 文件：{audio_path}")
    print(f"📏 大小：{Path(audio_path).stat().st_size / 1024:.2f} KB")
    
    # 检查文件是否存在
    if not Path(audio_path).exists():
        print(f"❌ 文件不存在：{audio_path}")
        return None
    
    # 由于 API 需要公网 URL，我们需要先上传文件
    # 方案：使用阿里云 OSS 上传，或使用临时文件服务
    
    # 这里提供一个简化方案：
    # 1. 使用 dashscope 的文件上传功能（如果支持）
    # 2. 或者手动上传到 OSS
    
    print("\n⚠️  阿里云 FunASR API 需要公网可访问的文件 URL")
    print("📦 建议方案：")
    print("   1. 上传文件到阿里云 OSS")
    print("   2. 获取文件公网 URL")
    print("   3. 调用转录 API")
    print("\n💡 快速操作：")
    print(f"   ossutil cp {audio_path} oss://your-bucket/audio.wav")
    print("   然后使用返回的 URL 调用 API")
    
    return None


def transcribe_with_url(file_url: str, api_key: str) -> dict:
    """
    使用文件 URL 进行转录
    
    Args:
        file_url: 文件公网 URL
        api_key: 阿里云 API Key
        
    Returns:
        转录结果字典
    """
    dashscope.api_key = api_key
    dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    
    print(f"\n📡 提交任务：{file_url}")
    
    # 异步提交任务
    task_response = Transcription.async_call(
        model='fun-asr',
        file_urls=[file_url]
    )
    
    task_id = task_response.output.task_id
    print(f"🎯 任务 ID: {task_id}")
    
    # 轮询任务状态
    print("⏳ 等待任务完成...")
    while True:
        transcribe_response = Transcription.fetch(task=task_id)
        status = transcribe_response.output.task_status
        
        if status == 'SUCCEEDED' or status == 'FAILED':
            break
            
        print(f"   状态：{status}")
        time.sleep(2)
    
    if transcribe_response.status_code == HTTPStatus.OK:
        print("✅ 转录完成！")
        return transcribe_response.output
    else:
        print(f"❌ 任务失败：{transcribe_response.message}")
        return None


def format_result(output: dict) -> str:
    """格式化输出结果"""
    lines = []
    lines.append("# 语音转录结果")
    
    for result in output.get('results', []):
        for sentence in result.get('sentences', []):
            start = float(sentence.get('begin_time', 0)) / 1000.0
            end = float(sentence.get('end_time', 0)) / 1000.0
            text = sentence.get('text', '')
            confidence = sentence.get('confidence', 1.0)
            
            start_str = f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{int(start%60):02d}"
            end_str = f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{int(end%60):02d}"
            
            lines.append(f"[{start_str} - {end_str}] {text} (置信度：{confidence:.2f})")
    
    return '\n'.join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='阿里云 FunASR 语音识别')
    parser.add_argument('-i', '--input', help='输入音频文件路径')
    parser.add_argument('-u', '--url', help='音频文件公网 URL')
    parser.add_argument('-k', '--apikey', help='阿里云 API Key')
    parser.add_argument('-o', '--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    api_key = args.apikey or os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未提供 API Key")
        print("   使用 -k 参数指定，或设置环境变量 DASHSCOPE_API_KEY")
        sys.exit(1)
    
    if args.url:
        # 使用 URL 转录
        output = transcribe_with_url(args.url, api_key)
        if output:
            result = format_result(output)
            print("\n" + "="*50)
            print(result)
            print("="*50)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"\n✅ 结果已保存：{args.output}")
    else:
        # 文件转录（需要上传）
        transcribe_file(args.input, api_key)


if __name__ == '__main__':
    main()
