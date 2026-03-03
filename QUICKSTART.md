# 快速启动指南

## 🎯 5 分钟快速测试

### 在 Intel Ultra5 上运行

```bash
# 1. 进入项目目录
cd speech-transcriber

# 2. 运行部署脚本（首次需要）
./deploy_local.sh

# 3. 测试转录
python3 run.py -i your_audio.wav -o result.txt

# 4. 查看结果
cat result.txt
```

## 📝 完整工作流程

### 场景 1：单文件转录

```bash
python3 run.py -i meeting.wav -o meeting_transcript.txt
```

### 场景 2：批量转录

```bash
mkdir output
for file in recordings/*.m4a; do
    python3 run.py -i "$file" -o "output/$(basename "$file" .m4a).txt"
done
```

### 场景 3：实时转录（流式）

```bash
python3 src/asr_realtime.py -i live_input.wav -o live_result.txt
```

## 🔧 配置选项

### 切换在线/本地模式

编辑 `configs/config.yaml`：

```yaml
# 在线模式（使用阿里云 API）
mode: online

# 本地模式（使用本地模型）
mode: local
```

### 选择设备

```yaml
local:
  device: cpu   # CPU 模式
  # device: cuda  # NVIDIA GPU
  # device: npu  # Intel NPU（需要 OpenVINO）
```

## 📊 输出格式

### 默认文本格式

```txt
# 语音转录结果
生成时间：2026-03-03 20:45:00
模式：local

[00:00:00 - 00:00:05] 说话人 1: 你好，今天我们来讨论项目。
[00:00:05 - 00:00:10] 说话人 2: 好的，目前进度正常。
```

### SRT 字幕格式

```bash
python3 run.py -i video.wav --format srt -o subtitles.srt
```

输出：
```srt
1
00:00:00,000 --> 00:00:05,000
说话人 1: 你好，今天我们来讨论项目。

2
00:00:05,000 --> 00:00:10,000
说话人 2: 好的，目前进度正常。
```

### JSON 格式

```bash
python3 run.py -i audio.wav --format json -o result.json
```

## 💡 常见问题

### Q: 第一次运行很慢？

A: 首次运行会自动下载模型（约 3GB），后续会使用缓存。

### Q: 如何查看模型位置？

```bash
python3 -c "from modelscope import snapshot_download; print(snapshot_download('damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn'))"
```

### Q: 如何提高识别准确率？

- 使用高质量音频（16kHz 以上）
- 减少背景噪音
- 本地模式比在线模式更准确

### Q: 支持哪些音频格式？

支持：wav, mp3, m4a, flac, aac, ogg 等常见格式。

---

**更多文档：**
- `LOCAL_DEPLOY.md` - 详细部署指南
- `DEPLOY.md` - 部署说明
- `USAGE.md` - 使用手册
