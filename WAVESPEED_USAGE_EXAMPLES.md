# WaveSpeed MCP 工具使用示例

## 🎯 前端配置

### 1. 在前端 MCP 设置中添加 WaveSpeed 服务器

1. 打开浏览器访问 `http://localhost:3000`
2. 点击右上角的设置图标（齿轮图标）
3. 选择 "MCP Servers" 标签页
4. 点击 "Add Servers" 按钮
5. 粘贴以下配置：

```json
{
  "mcpServers": {
    "mcp-wavespeed": {
      "command": "wavespeed-mcp",
      "args": [],
      "env": {
        "WAVESPEED_API_KEY": "e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208"
      }
    }
  }
}
```

6. 点击保存
7. 确保启用该服务器（开关为绿色）

### 2. 工具会自动加载

配置成功后，您会看到 3 个工具：
- ✅ text_to_image
- ✅ image_to_image  
- ✅ generate_video

## 🚀 使用方法

### 方法1：直接在聊天中使用（推荐）

只需在聊天界面输入包含图片或视频生成意图的自然语言：

#### 文本生成图片 (text_to_image)
```
用户：请帮我生成一张可爱的小猫咪的图片
系统：[自动调用 text_to_image 工具]

用户：生成一个科幻风格的未来城市景观
系统：[自动调用 text_to_image 工具]

用户：制作一个写实风格的日落海滩场景
系统：[自动调用 text_to_image 工具]
```

#### 图片到图片转换 (image_to_image)  
```
用户：将这张图片转换为卡通风格
系统：[自动调用 image_to_image 工具]

用户：为这张图片添加冬天的效果
系统：[自动调用 image_to_image 工具]
```

#### 视频生成 (generate_video)
```
用户：生成一个5秒的海浪视频
系统：[自动调用 generate_video 工具]

用户：将静态图片转换为动态视频
系统：[自动调用 generate_video 工具]
```

### 方法2：通过 API 测试

使用以下 Python 脚本测试：

```python
import requests

# 测试图片生成
response = requests.post(
    "http://localhost:8000/api/chat/stream",
    json={
        "messages": [{"role": "user", "content": "请生成一张可爱的小猫图片"}],
        "thread_id": "test_wavespeed",
        "auto_accepted_plan": True,
        "max_step_num": 3,
        "mcp_settings": {
            "servers": {
                "mcp-wavespeed": {
                    "transport": "stdio",
                    "command": "wavespeed-mcp", 
                    "args": [],
                    "env": {
                        "WAVESPEED_API_KEY": "e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208"
                    },
                    "enabled_tools": ["text_to_image", "image_to_image", "generate_video"],
                    "add_to_agents": ["researcher"]
                }
            }
        }
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

## 🎨 具体示例

### 图片生成示例

1. **基础图片生成**：
   ```
   "请生成一张金毛犬在草地上奔跑的图片"
   ```

2. **风格化图片**：
   ```
   "生成一个赛博朋克风格的城市夜景，包含霓虹灯和飞行汽车"
   ```

3. **特定尺寸**：
   ```
   "创建一个1024x768的写实风格日落海滩场景"
   ```

### 视频生成示例

1. **基础视频**：
   ```
   "生成一个5秒的云朵飘动视频"
   ```

2. **动物视频**：
   ```
   "制作一个小鸟在天空中飞翔的短视频"
   ```

## 🔧 故障排除

### 问题1：工具没有被调用
**症状**：聊天界面没有显示工具调用
**解决方案**：
1. 检查前端 MCP 设置是否正确配置
2. 确认服务器已启用
3. 刷新页面重新加载配置

### 问题2：API 密钥错误
**症状**：工具调用失败，返回认证错误
**解决方案**：
1. 确认 API 密钥正确
2. 检查环境变量设置

### 问题3：生成失败
**症状**：工具调用成功但生成失败
**解决方案**：
1. 确保提示词是英文（工具要求）
2. 检查网络连接
3. 查看错误日志

## 📝 注意事项

1. **语言要求**：WaveSpeed 工具要求提示词为英文，系统会自动翻译中文输入
2. **网络要求**：需要稳定的网络连接到 WaveSpeed API
3. **配置要求**：确保前端 MCP 配置正确并已启用
4. **自动识别**：系统会根据用户输入的语义自动选择合适的工具

## 🎉 成功标志

当配置正确时，您会看到：
- ✅ 聊天界面显示工具调用过程
- ✅ 返回生成的图片/视频链接
- ✅ 浏览器控制台没有错误信息 