#!/usr/bin/env python3
"""
测试脚本 - 验证转录流程
"""
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.vad import VADProcessor
from src.asr import ASRProcessor
from src.speaker import SpeakerDiarizer


def test_config():
    """测试配置加载"""
    print("📋 测试配置加载...")
    config = get_config()
    print(f"   模式：{config.mode}")
    print(f"   配置路径：{config.config_path}")
    assert config.mode in ['online', 'local']
    print("   ✅ 通过\n")


def test_vad():
    """测试 VAD 模块"""
    print("🔍 测试 VAD...")
    vad = VADProcessor()
    print(f"   处理器：{vad}")
    # 模拟测试
    segments = vad._detect_online("test.wav")
    print(f"   检测到 {len(segments)} 个片段")
    print("   ✅ 通过\n")


def test_asr():
    """测试 ASR 模块"""
    print("📝 测试 ASR...")
    asr = ASRProcessor()
    print(f"   处理器：{asr}")
    # 模拟测试
    results = asr._transcribe_online("test.wav")
    print(f"   转录 {len(results)} 个结果")
    for r in results:
        print(f"      - {r.text}")
    print("   ✅ 通过\n")


def test_speaker():
    """测试说话人分离模块"""
    print("👥 测试说话人分离...")
    speaker = SpeakerDiarizer()
    print(f"   处理器：{speaker}")
    # 模拟测试
    segments = speaker._diarize_online("test.wav")
    print(f"   分离 {len(segments)} 个说话人片段")
    speakers = set(s.speaker_id for s in segments)
    print(f"   说话人：{speakers}")
    print("   ✅ 通过\n")


def main():
    print("="*50)
    print("🧪 Speech Transcriber 测试套件")
    print("="*50 + "\n")
    
    try:
        test_config()
        test_vad()
        test_asr()
        test_speaker()
        
        print("="*50)
        print("✅ 所有测试通过！")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
