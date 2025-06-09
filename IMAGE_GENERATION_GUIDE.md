# 图片和视频生成功能使用指南

## 概述

DeerFlow 现在集成了真实的 [WaveSpeed MCP 服务器](https://github.com/WaveSpeedAI/mcp-server) 来支持高质量的图片和视频生成。当用户的输入语义表示需要生成图片或视频时，系统会自动调用相应的 WaveSpeed AI 工具。

## 功能特性

### 图片生成 (text_to_image)
- 基于 Flux 模型的高质量图片生成
- 支持多种艺术风格和主题
- 智能提示词优化
- 多种输出格式：URL、Base64、本地文件

### 图片编辑 (image_to_image)
- 图片风格转换
- 图片修复和增强
- 基于提示词的图片修改
- 支持 LoRA 模型定制

### 视频生成 (image_to_video)
- 静态图片转动态视频
- 智能动画效果生成
- 可控制的视频时长和质量
- 支持多种视频格式输出

## 使用方法

### 通过聊天接口

发送包含图片或视频生成意图的消息：

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/stream",
    json={
        "messages": [{"role": "user", "content": "请帮我生成一张可爱的小猫咪的图片"}],
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

### 示例请求

#### 图片生成请求
- "请帮我生成一张可爱的小猫咪的图片"
- "生成一个科幻风格的城市景观图片"
- "创建一个卡通风格的森林场景"
- "制作一个现实主义风格的日落海滩图片"

#### 视频生成请求
- "生成一个5秒的海浪视频"
- "创建一个卡通风格的动物跑步视频"
- "制作一个科幻风格的太空场景视频"

## 配置说明

### MCP 服务器配置

在请求中包含 `mcp_settings` 配置：

```json
{
  "mcp_settings": {
    "servers": {
      "mcp-wavespeed": {
        "transport": "stdio",
        "command": "python",
        "args": ["mock_wavespeed_mcp.py"],
        "enabled_tools": ["generate_image", "generate_video"],
        "add_to_agents": ["researcher"]
      }
    }
  }
}
```

### 工具参数

#### generate_image 工具
- `prompt` (必需): 图片生成提示词
- `style` (可选): 图片风格，默认 "realistic"
- `size` (可选): 图片尺寸，默认 "1024x1024"

#### generate_video 工具
- `prompt` (必需): 视频生成提示词
- `duration` (可选): 视频时长（秒），默认 5
- `style` (可选): 视频风格，默认 "realistic"

## 工作流程

1. **语义识别**: 系统分析用户输入，识别是否为图片/视频生成请求
2. **工具调用**: 如果识别为生成请求，系统会调用相应的 MCP 工具
3. **参数提取**: 从用户输入中提取风格、尺寸等参数
4. **生成执行**: 调用 Wavespeed API 执行生成
5. **结果返回**: 返回生成的图片/视频链接和元数据

## 测试

运行测试脚本：

```bash
python test_image_generation.py
```

## 注意事项

1. 确保服务器正在运行
2. 确保 MCP 配置正确
3. 模拟服务器仅用于测试，实际使用需要真实的 Wavespeed API
4. 生成的图片/视频链接是模拟的，实际使用时会返回真实链接

## 扩展

要集成真实的 Wavespeed API：

1. 替换 `mock_wavespeed_mcp.py` 为真实的 MCP 服务器
2. 配置正确的 API 密钥和端点
3. 更新工具参数以匹配真实 API 规范 