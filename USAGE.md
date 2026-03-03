# 使用指南 - 阿里云 FunASR 在线识别

## 前提条件

1. ✅ 已安装依赖：`pip install -r requirements.txt`
2. ✅ 已配置 API Key：`configs/config.yaml` 中的 `online.api_key`
3. ⚠️  需要文件存储：音频文件需要上传到公网可访问的 URL

## 方案一：使用阿里云 OSS（推荐）

### 1. 配置 OSS

编辑 `configs/config.yaml`：

```yaml
online:
  api_key: "sk-xxx"
  storage:
    type: "oss"
    oss_bucket: "your-bucket-name"
    oss_endpoint: "oss-cn-beijing.aliyuncs.com"
    oss_access_key: "your-access-key"
    oss_access_secret: "your-access-secret"
```

### 2. 上传文件并转录

```bash
# 自动上传 + 转录
python3 test_real_api.py -i audio.wav -o result.txt

# 或手动上传到 OSS，然后使用 URL 转录
python3 src/asr_realtime.py -u https://your-bucket.oss-cn-beijing.aliyuncs.com/audio.wav -k sk-xxx -o result.txt
```

## 方案二：手动上传文件

### 1. 上传到任意图床/文件托管

推荐服务：
- 阿里云 OSS：https://oss.console.aliyun.com/
- 腾讯云 COS：https://console.cloud.tencent.com/cos
- 七牛云：https://portal.qiniu.com/
- 临时文件托管：https://catbox.moe/（免费，无需注册）

### 2. 获取文件 URL

上传后获取公网 URL，例如：
```
https://your-bucket.oss-cn-beijing.aliyuncs.com/audio.wav
```

### 3. 调用转录 API

```bash
python3 src/asr_realtime.py \
  -u "https://your-bucket.oss-cn-beijing.aliyuncs.com/audio.wav" \
  -k "sk-952dd49431814843a16ce254eae34c4e" \
  -o result.txt
```

## 方案三：本地部署（最终方案）

在你的 **Intel Ultra5-225H** 电脑上运行本地模型，无需 API 和上传。

### 1. 安装本地模型

```bash
cd projects/speech-transcriber

# 安装 modelscope
pip install modelscope

# 下载模型（约 2GB）
python -c "from modelscope import snapshot_download; snapshot_download('damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn')"
```

### 2. 切换到本地模式

编辑 `configs/config.yaml`：

```yaml
mode: local  # 从 online 改为 local

local:
  device: cpu  # cpu | cuda | npu
  models:
    asr: "damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn"
    vad: "damo/speech_fsmn_vad_zh-cn-16k-common-pytorch"
    speaker: "damo/speech_campplus_sv_zh-cn_16k-common"
```

### 3. 运行本地转录

```bash
python3 run.py -i audio.wav -o result.txt
```

## 价格说明

阿里云 FunASR 计费（中国内地）：
- **单价**: 0.00022 元/秒（约 0.22 元/小时）
- **免费额度**: 36,000 秒（10 小时），有效期 90 天
- 你的两个音频文件（约 1-2 分钟）成本约 **0.01 元**

## 输出格式

```txt
# 语音转录结果
生成时间：2026-03-03 19:53:00
模式：online

[00:00:00 - 00:00:05] 你好，这里是识别结果文本。
[00:00:05 - 00:00:10] 这是第二句话的识别结果。
```

## 常见问题

### Q: 为什么需要上传文件到 OSS？

A: 阿里云 FunASR API 要求文件必须是公网可访问的 URL，不支持本地文件直传。这是为了支持批量处理和异步任务。

### Q: 临时文件托管安全吗？

A: 敏感音频建议使用私有 OSS Bucket。公开测试可以用临时托管服务。

### Q: 本地部署和在线 API 哪个更好？

A: 
- **在线 API**: 无需部署，按量付费，适合偶尔使用
- **本地部署**: 数据完全本地，一次性投入（硬件），适合频繁使用

### Q: 识别准确率如何？

A: FunASR 中文识别准确率约 95-98%，支持中英文混合、方言等。

## 下一步

1. **测试在线 API**: 上传文件到 OSS，调用 API 测试真实效果
2. **部署本地模型**: 在 Intel Ultra5 上部署，实现完全离线
3. **集成到应用**: 将转录功能集成到你的业务系统中
