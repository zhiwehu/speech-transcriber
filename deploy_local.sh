#!/bin/bash
# Speech Transcriber 本地部署脚本
# 适用于 Intel Ultra5-225H + 32/64GB RAM

set -e

echo "=========================================="
echo "🚀 Speech Transcriber 本地部署"
echo "=========================================="
echo ""

# 检查 Python 版本
echo "📋 检查 Python 环境..."
python3 --version || { echo "❌ 未找到 Python3"; exit 1; }

# 检查 pip
pip3 --version || { echo "❌ 未找到 pip3"; exit 1; }

echo ""
echo "✅ Python 环境检查通过"
echo ""

# 1. 安装基础依赖
echo "📦 步骤 1/5: 安装基础依赖..."
pip3 install -r requirements.txt
echo "✅ 基础依赖安装完成"
echo ""

# 2. 安装本地模式额外依赖
echo "📦 步骤 2/5: 安装本地模式依赖..."
pip3 install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
echo "✅ 本地依赖安装完成"
echo ""

# 3. 下载 3D-Speaker 模型
echo "📥 步骤 3/5: 下载 3D-Speaker 模型（约 500MB）..."
python3 << 'EOF'
from modelscope import snapshot_download
import os

print("⏳ 正在下载 3D-Speaker 模型...")
model_dir = snapshot_download('damo/speech_campplus_sv_zh-cn_16k-common')
print(f"✅ 模型已下载到：{model_dir}")
EOF
echo ""

# 4. 下载 FunASR 主模型
echo "📥 步骤 4/5: 下载 FunASR 主模型（约 2GB）..."
python3 << 'EOF'
from modelscope import snapshot_download
import os

print("⏳ 正在下载 FunASR Paraformer 模型...")
model_dir = snapshot_download('damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn')
print(f"✅ 模型已下载到：{model_dir}")
EOF
echo ""

# 5. 下载 VAD 模型
echo "📥 步骤 5/5: 下载 VAD 模型（约 100MB）..."
python3 << 'EOF'
from modelscope import snapshot_download
import os

print("⏳ 正在下载 VAD 模型...")
model_dir = snapshot_download('damo/speech_fsmn_vad_zh-cn-16k-common-pytorch')
print(f"✅ 模型已下载到：{model_dir}")
EOF
echo ""

# 6. 切换到本地模式
echo "⚙️  配置本地模式..."
CONFIG_FILE="configs/config.yaml"

if [ -f "$CONFIG_FILE" ]; then
    # 备份原配置
    cp "$CONFIG_FILE" "${CONFIG_FILE}.backup"
    
    # 修改模式
    sed -i 's/mode: online/mode: local/' "$CONFIG_FILE"
    sed -i 's/device: cpu/device: cpu/' "$CONFIG_FILE"
    
    echo "✅ 配置已更新（备份：${CONFIG_FILE}.backup）"
else
    echo "⚠️  配置文件不存在：$CONFIG_FILE"
fi
echo ""

# 7. 测试安装
echo "🧪 测试安装..."
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

try:
    from config import get_config
    config = get_config()
    print(f"✅ 配置加载成功：mode={config.mode}")
    
    # 检查模型是否存在
    from modelscope import snapshot_download
    import os
    
    models = [
        'damo/speech_campplus_sv_zh-cn_16k-common',
        'damo/speech_paraformer-large-vad-punc-zh-cn-16k-common-zh-cn',
        'damo/speech_fsmn_vad_zh-cn-16k-common-pytorch'
    ]
    
    for model_name in models:
        try:
            model_dir = snapshot_download(model_name)
            if os.path.exists(model_dir):
                print(f"✅ 模型已存在：{model_name}")
            else:
                print(f"❌ 模型目录不存在：{model_name}")
        except Exception as e:
            print(f"⚠️  模型检查失败 {model_name}: {e}")
    
    print("✅ 所有模型检查完成")
    
except Exception as e:
    print(f"❌ 测试失败：{e}")
    import traceback
    traceback.print_exc()
EOF
echo ""

# 完成
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📝 使用说明："
echo "   1. 编辑 configs/config.yaml 确认配置"
echo "   2. 运行测试：python3 run.py -i test.wav -o result.txt"
echo "   3. 查看结果：cat result.txt"
echo ""
echo "💡 性能优化建议："
echo "   - Intel NPU 加速：安装 OpenVINO"
echo "   - 批量处理：使用 --batch 参数"
echo "   - 实时转录：使用 src/asr_realtime.py"
echo ""
echo "🎉 开始使用吧！"
echo ""
