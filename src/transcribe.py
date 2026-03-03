#!/usr/bin/env python3
"""
语音转录主程序
多说话人语音识别 - 阿里达摩院技术栈
"""
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List

from .config import get_config, Config
from .vad import VADProcessor
from .asr import ASRProcessor, ASRResult
from .speaker import SpeakerDiarizer, SpeakerSegment


class SpeechTranscriber:
    """语音转录器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化转录器
        
        Args:
            config_path: 配置文件路径（可选）
        """
        self.config = get_config() if config_path is None else Config(config_path)
        
        print(f"🎙️  Speech Transcriber 初始化完成")
        print(f"   模式：{self.config.mode}")
        print(f"   配置：{self.config.config_path}")
        
        # 初始化各模块
        self.vad = VADProcessor()
        self.asr = ASRProcessor()
        self.speaker = SpeakerDiarizer()
    
    def transcribe(self, audio_path: str, output_path: str = None) -> str:
        """
        完整转录流程
        
        Args:
            audio_path: 输入音频文件路径
            output_path: 输出文件路径（可选）
            
        Returns:
            转录文本
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"音频文件不存在：{audio_path}")
        
        print(f"\n📁 处理文件：{audio_path}")
        print(f"   大小：{audio_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Step 1: VAD 语音活动检测
        print("\n[1/3] 🔍 语音活动检测...")
        vad_segments = self.vad.detect(str(audio_path))
        print(f"   检测到 {len(vad_segments)} 个语音片段")
        
        # Step 2: 说话人分离
        print("\n[2/3] 👥 说话人分离...")
        speaker_segments = self.speaker.diarize(str(audio_path), vad_segments)
        speakers = set(seg.speaker_id for seg in speaker_segments)
        print(f"   识别到 {len(speakers)} 个说话人：{', '.join(speakers)}")
        
        # Step 3: 语音识别
        print("\n[3/3] 📝 语音识别...")
        # 不传 VAD segments，让 ASR 处理完整音频
        asr_results = self.asr.transcribe(str(audio_path), None)
        print(f"   转录 {len(asr_results)} 个片段")
        
        # 合并结果（如果说话人分离有结果，使用说话人信息）
        if speaker_segments:
            result = self._merge_results(speaker_segments, asr_results)
        else:
            # 没有说话人信息，直接输出 ASR 结果
            result = []
            for asr in asr_results:
                result.append({
                    'speaker': '说话人',
                    'text': asr.text,
                    'start': asr.start_time,
                    'end': asr.end_time,
                })
        
        # 输出
        output_text = self._format_output(result)
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"\n✅ 输出已保存：{output_path}")
        
        return output_text
    
    def _merge_results(self, speaker_segments: List[SpeakerSegment], 
                       asr_results: List[ASRResult]) -> List[dict]:
        """合并说话人和 ASR 结果 - 基于时间戳匹配"""
        result = []
        
        for asr in asr_results:
            # 找到与 ASR 片段重叠最多的说话人片段
            best_speaker = "说话人"
            best_overlap = 0
            
            asr_start = asr.start_time
            asr_end = asr.end_time
            
            for speaker_seg in speaker_segments:
                # 计算重叠时间
                overlap_start = max(asr_start, speaker_seg.start_time)
                overlap_end = min(asr_end, speaker_seg.end_time)
                overlap = max(0, overlap_end - overlap_start)
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_speaker = speaker_seg.speaker_id
            
            # 如果没有找到重叠，使用最近的说话人
            if best_overlap == 0 and speaker_segments:
                # 找时间最接近的说话人片段
                min_distance = float('inf')
                for speaker_seg in speaker_segments:
                    distance = abs((speaker_seg.start_time + speaker_seg.end_time) / 2 - (asr_start + asr_end) / 2)
                    if distance < min_distance:
                        min_distance = distance
                        best_speaker = speaker_seg.speaker_id
            
            result.append({
                'speaker': best_speaker,
                'text': asr.text,
                'start': asr.start_time,
                'end': asr.end_time,
            })
        
        return result
    
    def _format_output(self, result: List[dict]) -> str:
        """格式化输出"""
        lines = []
        lines.append(f"# 语音转录结果")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"模式：{self.config.mode}")
        lines.append("")
        
        for item in result:
            start = self._format_time(item['start'])
            end = self._format_time(item['end'])
            lines.append(f"[{start} - {end}] {item['speaker']}: {item['text']}")
        
        return '\n'.join(lines)
    
    def _format_time(self, seconds: float) -> str:
        """秒数转为 HH:MM:SS 格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main():
    parser = argparse.ArgumentParser(
        description='语音转录系统 - 多说话人识别',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m src.transcribe -i meeting.wav -o result.txt
  python -m src.transcribe --input audio.mp3 --mode local
        """
    )
    
    parser.add_argument('-i', '--input', required=True, help='输入音频文件')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-m', '--mode', choices=['online', 'local'], help='运行模式')
    
    args = parser.parse_args()
    
    # 创建转录器
    transcriber = SpeechTranscriber(config_path=args.config)
    
    # 执行转录
    result = transcriber.transcribe(args.input, args.output)
    
    # 如果没有指定输出文件，打印到控制台
    if not args.output:
        print("\n" + "="*50)
        print(result)
        print("="*50)


if __name__ == '__main__':
    main()
