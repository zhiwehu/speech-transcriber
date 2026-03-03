# 部署指南

## 在线模式（默认）

无需额外配置，直接运行：

```bash
pip install -r requirements.txt
python run.py -i audio.wav -o result.txt
```

## 本地模式部署

### 1. Intel Ultra5 优化部署（推荐）

你的硬件：Intel Ultra5-225H + 32/64GB RAM

#### 使用 OpenVINO 加速

```bash
# 安装 OpenVINO
pip install openvino optimum-intel

# 转换模型为 OpenVINO IR 格式
optimum-cli export openvino \
  --model damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn \
  ./models/paraformer-ov

# 修改配置文件
# configs/config.yaml
# local:
#   device: cpu
#   inference:
#     use_openvino: true
```

#### 性能预期

| 模型 | 模式 | 速度 | 内存 |
|------|------|------|------|
| Paraformer | OpenVINO INT8 | 1.5x RTF | 2GB |
| Silero VAD | OpenVINO | 实时 | 500MB |
| 3D-Speaker | PyTorch | 0.5x RTF | 1GB |

### 2. 纯 CPU 部署

```bash
# 修改配置文件
# configs/config.yaml
# local:
#   device: cpu
#   models:
#     vad: "damo/speech_fsmn_vad_zh-cn-16k-common-pytorch"
#     asr: "damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn"
#     speaker: "damo/speech_campplus_sv_zh-cn_16k-common"
```

### 3. 模型下载

阿里达摩院模型（DAMO Academy）：

```bash
# 使用 modelscope 下载
pip install modelscope

python -c "
from modelscope import snapshot_download
model_dir = snapshot_download('damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn')
print(f'模型下载到：{model_dir}')
"
```

### 4. 切换到本地模式

编辑 `configs/config.yaml`：

```yaml
mode: local  # 从 online 改为 local

local:
  device: cpu  # 或 npu（如果启用 OpenVINO）
```

## 测试

```bash
# 运行测试套件
python tests/test_pipeline.py

# 测试转录
python run.py -i test.wav -o result.txt
```

## 常见问题

### Q: 在线模式需要 API Key 吗？

A: 阿里云 FunASR 提供部分免费额度，日常使用足够。如需大量处理，申请 API Key：
https://dashscope.console.aliyun.com/

### Q: 本地模式内存不足？

A: 使用 INT8 量化模型，或减小 batch_size：

```yaml
local:
  inference:
    batch_size: 1  # 降低为 1
```

### Q: 中文识别不准？

A: 确保使用中文专用模型：
- `damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn`

### Q: 说话人分离错误？

A: 调整阈值：

```yaml
common:
  diarization_threshold: 0.25  # 降低阈值（更敏感）
```

## 下一步

- [ ] 添加 Web UI（Gradio）
- [ ] 批量处理支持
- [ ] SRT 字幕输出
- [ ] 实时流式转录
