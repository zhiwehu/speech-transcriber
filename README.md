# Speech Transcriber

[![GitHub stars](https://img.shields.io/github/stars/zhiwehu/speech-transcriber?style=social)](https://github.com/zhiwehu/speech-transcriber)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**多说话人语音识别系统** - 基于阿里达摩院 FunASR 和 3D-Speaker 技术栈

---

## 🚀 快速开始

### 1. 创建虚拟环境（推荐）

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

**方式 A：使用 .env 文件（推荐）**

复制 `.env.example` 为 `.env`，填写你的配置：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 API Key 等
```

**方式 B：编辑配置文件**

编辑 `configs/config.yaml`，或使用环境变量覆盖。

### 4. 运行

```bash
python3 run.py -i audio.wav -o result.txt
```

### 5. 查看结果

```txt
[00:00:00 - 00:00:05] 说话人 1: 你好，今天我们来讨论项目。
[00:00:05 - 00:00:10] 说话人 2: 好的，目前进度正常。
```

---

## 📦 本地部署（推荐）

在你的 **Intel Ultra5** 或其他机器上部署本地模型：

```bash
# 一键部署（自动下载模型，约 3GB）
./deploy_local.sh
```

部署后切换到本地模式：
```yaml
mode: local
```

---

## 🔧 功能特性

| 功能 | 在线模式 | 本地模式 |
|------|----------|----------|
| **语音识别** | ✅ FunASR | ✅ FunASR |
| **说话人分离** | ⚠️ 基础 | ✅ 3D-Speaker |
| **多语言** | ✅ 中英文混合 | ✅ 中英文混合 |
| **隐私** | 需上传 | 完全本地 |
| **成本** | 按量付费 | 免费 |

---

## 📁 项目结构

```
speech-transcriber/
├── configs/
│   └── config.yaml          # 配置文件
├── src/
│   ├── vad.py               # 语音活动检测
│   ├── asr.py               # 语音识别
│   ├── speaker.py           # 说话人分离
│   └── transcribe.py        # 主程序
├── tests/
│   └── test_pipeline.py     # 测试脚本
├── deploy_local.sh          # 一键部署脚本
├── requirements.txt         # Python 依赖
└── README.md                # 本文件
```

---

## 📖 文档

- **快速开始**: 本文档上方
- **详细部署**: 查看 `deploy_local.sh` 脚本注释
- **配置说明**: `configs/config.yaml` 中的注释
- **使用示例**: 运行 `python3 run.py --help`

---

## 🔑 获取 API Key

### 阿里云 DashScope（在线模式）

1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录
3. 创建 API Key
4. 免费额度：36,000 秒（10 小时）

### 阿里云 OSS（文件上传）

1. 访问 https://oss.console.aliyun.com/
2. 创建 Bucket
3. 获取 AccessKey ID 和 Secret

---

## 💡 常见问题

**Q: 第一次运行很慢？**  
A: 首次运行会自动下载模型（约 3GB），后续会使用缓存。

**Q: 说话人分离不准确？**  
A: 在线模式使用基础分离，建议使用本地模式（3D-Speaker）获得更好效果。

**Q: 支持哪些音频格式？**  
A: wav, mp3, m4a, flac, aac, ogg 等常见格式。

**Q: 如何提高识别准确率？**  
A: 使用高质量音频（16kHz 以上），减少背景噪音。

---

## 🛠️ 开发

### 测试

```bash
python3 tests/test_pipeline.py
```

### 批量处理

```bash
for file in audio/*.wav; do
    python3 run.py -i "$file" -o "output/$(basename "$file" .wav).txt"
done
```

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

---

## 👤 作者

**Jeffrey Hu**  
GitHub: [@zhiwehu](https://github.com/zhiwehu)  
Blog: [aicodeplayer.com](https://aicodeplayer.com)

---

## 🙏 致谢

- [FunASR](https://github.com/alibaba-damo-academy/FunASR) - 阿里达摩院语音识别
- [3D-Speaker](https://github.com/alibaba-damo-academy/3D-Speaker) - 阿里声纹识别
- [DashScope](https://dashscope.aliyun.com/) - 阿里云百炼平台
