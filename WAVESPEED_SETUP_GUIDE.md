# WaveSpeed MCP 设置指南

## 概述

本指南将帮助您集成真实的 [WaveSpeed MCP 服务器](https://github.com/WaveSpeedAI/mcp-server) 来实现图片和视频生成功能。

## 安装和配置

### 1. 安装 WaveSpeed MCP

WaveSpeed MCP 已经安装完成：

```bash
pip install wavespeed-mcp --break-system-packages
```

### 2. 获取 API 密钥

1. 访问 [WaveSpeed AI](https://wavespeed.ai)
2. 注册账户并获取 API 密钥
3. 将 API 密钥添加到环境变量中

### 3. 配置环境变量

创建环境变量配置文件：

```bash
# 基本配置
export WAVESPEED_API_KEY="your_wavespeed_api_key_here"

# 可选配置
export WAVESPEED_API_HOST="https://api.wavespeed.ai"
export WAVESPEED_MCP_BASE_PATH="~/Desktop"
export WAVESPEED_API_RESOURCE_MODE="url"
export WAVESPEED_LOG_LEVEL="INFO"

# API 端点配置
export WAVESPEED_API_TEXT_TO_IMAGE_ENDPOINT="/wavespeed-ai/flux-dev"
export WAVESPEED_API_IMAGE_TO_IMAGE_ENDPOINT="/wavespeed-ai/flux-kontext-pro"
export WAVESPEED_API_VIDEO_ENDPOINT="/wavespeed-ai/wan-2.1/i2v-480p-lora"
```

## 功能特性

### 支持的工具

根据 [WaveSpeed MCP 文档](https://github.com/WaveSpeedAI/mcp-server)，提供以下工具：

1. **text_to_image**: 从文本提示生成图片
2. **image_to_image**: 图片到图片的转换和编辑
3. **image_to_video**: 将静态图片转换为动态视频

### 高级功能

- **图片修复 (Inpainting)**: 修复或编辑图片的特定区域
- **LoRA 模型支持**: 使用定制的 LoRA 模型
- **多种输出模式**: URL、Base64 或本地文件
- **智能重试机制**: 自动处理 API 错误和重试
- **进度跟踪**: 详细的生成进度监控

## 使用方法

### 1. 通过聊天接口

发送自然语言请求：

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/stream",
    json={
        "messages": [{"role": "user", "content": "请帮我生成一张现实主义风格的日落海滩图片"}],
        "thread_id": "__default__",
        "resources": [],
        "max_plan_iterations": 1,
        "max_step_num": 3,
        "max_search_results": 5,
        "auto_accepted_plan": True,
        "enable_background_investigation": False,
        "mcp_settings": {
            "servers": {
                "mcp-wavespeed": {
                    "transport": "stdio",
                    "command": "wavespeed-mcp",
                    "args": [],
                    "env": {
                        "WAVESPEED_API_KEY": "your_wavespeed_api_key_here"
                    },
                    "enabled_tools": ["text_to_image", "image_to_image", "image_to_video"],
                    "add_to_agents": ["researcher"],
                }
            }
        }
    },
    stream=True
)
```

### 2. 示例请求

#### 文本生成图片
- "生成一张科幻风格的城市景观"
- "创建一个可爱的小猫咪图片"
- "制作一个抽象艺术风格的画作"

#### 图片转图片
- "将这张图片转换为卡通风格"
- "为这张图片添加更多细节"
- "修改图片的色调和氛围"

#### 图片转视频
- "将这张静态图片转换为动态视频"
- "为这张风景图添加动态效果"
- "创建一个短视频动画"

## 配置选项

### MCP 服务器配置

```json
{
  "mcp_settings": {
    "servers": {
      "mcp-wavespeed": {
        "transport": "stdio",
        "command": "wavespeed-mcp",
        "args": [],
        "env": {
          "WAVESPEED_API_KEY": "your_api_key_here",
          "WAVESPEED_API_HOST": "https://api.wavespeed.ai",
          "WAVESPEED_API_RESOURCE_MODE": "url",
          "WAVESPEED_LOG_LEVEL": "INFO"
        },
        "enabled_tools": ["text_to_image", "image_to_image", "image_to_video"],
        "add_to_agents": ["researcher"]
      }
    }
  }
}
```

### 资源输出模式

- **url**: 返回图片/视频的 URL 链接（默认）
- **base64**: 返回 Base64 编码的数据
- **local**: 保存到本地文件系统

## 测试

### 1. 测试 MCP 服务器连接

```bash
wavespeed-mcp --api-key your_api_key_here
```

### 2. 运行集成测试

```bash
python test_image_generation.py
```

## 故障排除

### 常见问题

1. **API 密钥错误**
   - 确认 API 密钥正确
   - 检查环境变量设置

2. **连接超时**
   - 检查网络连接
   - 验证 API 端点 URL

3. **权限问题**
   - 确认 API 密钥有足够权限
   - 检查账户余额和使用限制

### 日志调试

设置详细日志：

```bash
export WAVESPEED_LOG_LEVEL=DEBUG
```

## 性能优化

### 配置建议

1. **资源模式选择**:
   - 开发测试: `url`
   - 生产环境: `local` 或 `base64`

2. **重试配置**:
   - WaveSpeed MCP 内置智能重试机制
   - 自动处理 API 限流和临时错误

3. **并发控制**:
   - 避免同时发起过多请求
   - 使用队列管理生成任务

## 扩展功能

### 自定义端点

可以配置自定义的 API 端点：

```bash
export WAVESPEED_API_TEXT_TO_IMAGE_ENDPOINT="/custom/text-to-image"
export WAVESPEED_API_IMAGE_TO_IMAGE_ENDPOINT="/custom/image-to-image"
export WAVESPEED_API_VIDEO_ENDPOINT="/custom/image-to-video"
```

### LoRA 模型

WaveSpeed 支持使用自定义的 LoRA 模型来生成特定风格的内容。

## 许可证和支持

- **许可证**: MIT License
- **支持**: support@wavespeed.ai
- **文档**: [GitHub Repository](https://github.com/WaveSpeedAI/mcp-server)

## 更新日志

当前版本: v0.1.6

主要功能:
- 高质量图片生成
- 图片到图片转换
- 静态图片转视频
- 优化的 API 轮询机制
- 全面的错误处理
- 详细的日志记录 