# 本地部署指南

适用于 **Intel Ultra5-225H + 32/64GB RAM** 环境

## 🚀 一键部署

### 步骤 1：传输项目文件

将项目文件夹复制到你的 Intel Ultra5 电脑：

```bash
# 方式 A：使用 scp
scp -r speech-transcriber jeff@your-computer:/home/jeff/projects/

# 方式 B：使用 git
git init
git add .
git commit -m "Initial commit"
# 然后推送到你的 Git 仓库
```

### 步骤 2：运行部署脚本

```bash
cd speech-transcriber
chmod +x deploy_local.sh
./deploy_local.sh
```

部署脚本会自动：
- ✅ 安装所有依赖
- ✅ 下载 3D-Speaker 模型（~500MB）
- ✅ 下载 FunASR 主模型（~2GB）
- ✅ 下载 VAD 模型（~100MB）
- ✅ 配置本地模式

### 步骤 3：测试运行

```bash
# 测试音频转录
python3 run.py -i test.wav -o result.txt

# 查看结果
cat result.txt
```

---

## 📋 手动部署（可选）

如果自动脚本失败，可以手动执行：

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
pip3 install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. 下载模型

```bash
# 3D-Speaker（声纹识别）
python3 -c "from modelscope import snapshot_download; snapshot_download('damo/speech_campplus_sv_zh-cn_16k-common')"

# FunASR Paraformer（语音识别）
python3 -c "from modelscope import snapshot_download; snapshot_download('damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn')"

# VAD（语音活动检测）
python3 -c "from modelscope import snapshot_download; snapshot_download('damo/speech_fsmn_vad_zh-cn-16k-common-pytorch')"
```

### 3. 修改配置

编辑 `configs/config.yaml`：

```yaml
mode: local  # 从 online 改为 local

local:
  device: cpu  # 或 npu（如果启用 OpenVINO）
  models:
    vad: "damo/speech_fsmn_vad_zh-cn-16k-common-pytorch"
    asr: "damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn"
    speaker: "damo/speech_campplus_sv_zh-cn_16k-common"
```

---

## ⚙️ 性能优化

### Intel OpenVINO 加速（推荐）

你的 Intel Ultra5 支持 NPU 加速：

```bash
# 安装 OpenVINO
pip3 install openvino optimum-intel

# 转换模型为 OpenVINO IR 格式
optimum-cli export openvino \
  --model damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn \
  ./models/paraformer-ov

# 修改配置启用 OpenVINO
# configs/config.yaml
local:
  inference:
    use_openvino: true
```

**性能提升：**
- CPU: ~1x RTF（实时因子）
- OpenVINO: ~2-3x RTF（2-3 倍加速）

### 批量处理

```bash
# 批量转录多个文件
for file in audio/*.wav; do
    python3 run.py -i "$file" -o "output/$(basename "$file" .wav).txt"
done
```

---

## 📊 性能预期

| 配置 | 速度 | 内存占用 | 准确率 |
|------|------|----------|--------|
| **CPU (i5 Ultra)** | ~1x RTF | 4GB | 95%+ |
| **OpenVINO** | ~2-3x RTF | 3GB | 95%+ |
| **GPU (如有)** | ~5x RTF | 6GB | 95%+ |

*RTF = Real Time Factor，1.0 表示 1 小时音频需 1 小时处理*

---

## 🔧 故障排查

### 问题 1：模型下载失败

```bash
# 检查网络连接
ping modelscope.cn

# 使用镜像
export MODELSCOPE_CACHE=~/.cache/modelscope
pip3 install modelscope -i https://mirrors.aliyun.com/pypi/simple/
```

### 问题 2：内存不足

```bash
# 减小 batch size
# configs/config.yaml
local:
  inference:
    batch_size: 1  # 降低为 1
```

### 问题 3：说话人分离不准确

```bash
# 安装 pyannote.audio（准确率更高）
pip3 install pyannote.audio

# 需要 HuggingFace token
# 访问 https://huggingface.co/pyannote/speaker-diarization-3.1 接受协议
# 然后设置环境变量
export HF_TOKEN=your_token
```

---

## 📁 目录结构

部署完成后：

```
speech-transcriber/
├── configs/
│   └── config.yaml          # 配置文件
├── src/
│   ├── vad.py               # 语音活动检测
│   ├── asr.py               # 语音识别
│   ├── speaker.py           # 说话人分离（3D-Speaker）
│   └── transcribe.py        # 主程序
├── output/                   # 输出目录
├── deploy_local.sh          # 部署脚本
├── requirements.txt         # 依赖列表
├── README.md                # 项目说明
└── LOCAL_DEPLOY.md          # 本文件
```

---

## 🎯 下一步

1. **运行部署脚本**：`./deploy_local.sh`
2. **测试音频**：上传测试音频验证效果
3. **性能调优**：根据实际效果调整参数
4. **集成应用**：将转录功能集成到你的业务系统

---

## 💡 使用技巧

### 实时转录

```bash
python3 src/asr_realtime.py -i audio.wav -o result.txt
```

### 输出 SRT 字幕

```bash
python3 run.py -i meeting.wav --format srt -o subtitles.srt
```

### 多语言混合

自动支持中英文混合，无需特殊配置。

---

**部署有问题？** 运行 `./deploy_local.sh --verbose` 查看详细日志。
