# Speech Transcriber - 语音转录系统

基于阿里达摩院技术栈的多说话人语音识别系统。

## 技术栈

| 功能 | 模型 | 说明 |
|------|------|------|
| VAD | Silero VAD | 语音活动检测 |
| 声纹识别 | 3D-Speaker | 说话人嵌入 |
| ASR | FunASR | 语音识别 |
| 说话人分离 | EEND-OLA | 端到端神经 diarization |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置模型

编辑 `configs/config.yaml`：

```yaml
mode: online  # online 或 local
```

- `online`: 使用阿里云 API（无需 GPU）
- `local`: 使用本地模型（需要 GPU/Intel NPU）

### 3. 运行转录

```bash
python src/transcribe.py --input audio.wav --output output/result.txt
```

## 项目结构

```
speech-transcriber/
├── configs/
│   └── config.yaml      # 配置文件（切换在线/本地）
├── src/
│   ├── __init__.py
│   ├── vad.py           # 语音活动检测
│   ├── asr.py           # 语音识别
│   ├── speaker.py       # 说话人分离
│   └── transcribe.py    # 主入口
├── tests/
│   └── test_pipeline.py
├── output/              # 输出目录
├── requirements.txt
└── README.md
```

## 配置说明

### 在线模式（默认）

使用阿里云 FunASR 服务，无需本地算力：

```yaml
mode: online
funasr:
  api_key: "your-api-key"  # 可选，部分模型免费
```

### 本地模式

切换到本地模型部署：

```yaml
mode: local
device: cpu  # cpu / cuda / npu
models:
  vad: "damo/speech_fsmn_vad_zh-cn-16k-common-pytorch"
  asr: "damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn"
  speaker: "damo/speech_campplus_sv_zh-cn_16k-common"
```

## 输出格式

```
[00:00:00 - 00:00:05] 说话人 1: 你好，今天我们来讨论一下项目进度。
[00:00:05 - 00:00:10] 说话人 2: 好的，目前前端部分已经完成 80%。
[00:00:10 - 00:00:15] 说话人 1: 后端接口什么时候能好？
```

## 性能参考

| 模式 | 速度 | 准确率 | 硬件要求 |
|------|------|--------|----------|
| 在线 | 实时 | 98% | 无 |
| 本地-CPU | 0.5x RTF | 95% | 16GB RAM |
| 本地-GPU | 2x RTF | 98% | 4GB VRAM |
| 本地-NPU | 1.5x RTF | 95% | Intel Ultra |

## 待办

- [ ] 添加标点恢复
- [ ] 支持批量处理
- [ ] 添加 Web UI
- [ ] 输出 SRT 字幕格式

## License

MIT
