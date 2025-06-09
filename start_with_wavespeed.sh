#!/bin/bash

# DeerFlow with WaveSpeed MCP 启动脚本

echo "🚀 启动 DeerFlow 与 WaveSpeed MCP 集成"
echo "=================================="

# 检查 API 密钥
if [ -z "$WAVESPEED_API_KEY" ]; then
    echo "❌ 错误: 未设置 WAVESPEED_API_KEY 环境变量"
    echo ""
    echo "📋 设置步骤:"
    echo "1. 获取 WaveSpeed API 密钥: https://wavespeed.ai"
    echo "2. 设置环境变量:"
    echo "   export WAVESPEED_API_KEY=your_api_key_here"
    echo "3. 重新运行此脚本"
    exit 1
fi

echo "🔑 API 密钥已设置: ${WAVESPEED_API_KEY:0:10}..."

# 设置 WaveSpeed 配置
export WAVESPEED_API_HOST="https://api.wavespeed.ai"
export WAVESPEED_API_RESOURCE_MODE="url"
export WAVESPEED_LOG_LEVEL="INFO"

echo "⚙️  WaveSpeed 配置:"
echo "   API Host: $WAVESPEED_API_HOST"
echo "   Resource Mode: $WAVESPEED_API_RESOURCE_MODE"
echo "   Log Level: $WAVESPEED_LOG_LEVEL"

# 检查依赖
echo ""
echo "🔍 检查依赖..."

if ! command -v wavespeed-mcp &> /dev/null; then
    echo "❌ wavespeed-mcp 未安装"
    echo "   运行: pip install wavespeed-mcp --break-system-packages"
    exit 1
fi

echo "✅ WaveSpeed MCP 已安装"

# 启动服务器
echo ""
echo "🌟 启动 DeerFlow 服务器..."
echo "   服务器地址: http://localhost:8000"
echo "   支持的工具: text_to_image, image_to_image, image_to_video"
echo ""
echo "💡 测试命令:"
echo "   python test_wavespeed_integration.py"
echo ""

python server.py --reload --host 0.0.0.0 --port 8000 