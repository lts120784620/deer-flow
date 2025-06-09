# WaveSpeed 图片生成功能 - 前端使用指南

## 🚀 完整启动流程

### 1. 启动后端服务器

```bash
# 在项目根目录
./start_with_wavespeed.sh
```

或者手动启动：

```bash
# 设置环境变量
export WAVESPEED_API_KEY=e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208

# 启动后端
python server.py --reload
```

后端服务器将在 `http://localhost:8000` 启动。

### 2. 启动前端界面

```bash
# 进入前端目录
cd web

# 安装依赖（如果还没安装）
pnpm install

# 启动前端开发服务器
pnpm dev
```

前端界面将在 `http://localhost:3000` 启动。

## ⚙️ 配置 WaveSpeed MCP 服务器

### 步骤1：打开前端设置界面

1. 访问 `http://localhost:3000`
2. 点击右上角的设置图标（齿轮图标）
3. 选择 "MCP Servers" 标签页

### 步骤2：添加 WaveSpeed MCP 服务器

点击 "Add Servers" 按钮，然后粘贴以下配置：

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

### 步骤3：确认配置生效

1. 点击 "Add" 按钮
2. 确保新添加的 "mcp-wavespeed" 服务器状态为 "启用"
3. 检查工具列表中应该显示：
   - `text_to_image`
   - `image_to_image`
   - `generate_video`

### 步骤4：启用自动接受计划

在 "General" 设置标签页中：
1. 开启 "Allow automatic acceptance of plans" 选项
2. 开启 "Enable background investigation" 选项（可选）

## 💬 在页面上触发 WaveSpeed 功能

### 方法一：直接在聊天界面输入

在前端聊天界面中，直接输入包含图片或视频生成意图的自然语言：

#### 🖼️ 图片生成请求示例
```
请帮我生成一张可爱的小猫咪的图片
```

```
生成一个现实主义风格的日落海滩景观
```

```
创建一张科幻风格的未来城市图片，包含飞行汽车和高楼大厦
```

```
制作一个卡通风格的森林场景，有小动物在玩耍
```

#### 🎬 视频生成请求示例
```
将一张静态的海滩图片转换为动态视频
```

```
为这张风景图添加动态效果，制作成5秒的视频
```

#### 🎨 图片编辑请求示例
```
将这张图片转换为卡通风格
```

```
为这张图片添加更多艺术效果
```

## 🔍 系统工作流程

当您发送图片生成请求时，系统会：

1. **语义识别**: 分析您的请求，识别为图片/视频生成需求
2. **计划生成**: 自动生成包含工具调用的执行计划
3. **MCP 调用**: 调用 WaveSpeed MCP 工具
4. **结果展示**: 返回生成的图片/视频链接

## 🛠️ 故障排除

### 问题1：跳转到 "Start research" 界面

**原因**: `auto_accepted_plan` 设置为 false
**解决方案**: 在设置中启用 "Allow automatic acceptance of plans"

### 问题2：没有调用 MCP 工具

**原因**: MCP 服务器未配置或未启用
**解决方案**: 
1. 检查 MCP 设置中是否正确添加了 mcp-wavespeed
2. 确认服务器状态为"启用"
3. 验证 API 密钥正确

### 问题3：工具调用失败

**原因**: API 密钥无效或网络问题
**解决方案**:
1. 检查 WAVESPEED_API_KEY 是否正确
2. 验证网络连接到 WaveSpeed API
3. 查看浏览器控制台和后端日志

### 问题4：提示词语言问题

**重要**: WaveSpeed API 只支持英文提示词
**解决方案**: 
- 用英文描述图片内容
- 或在中文后添加英文翻译
- 例如："生成一只可爱的小猫 (Generate a cute cat)"

## 🧪 测试配置

### 快速测试命令

在项目根目录运行：

```bash
python test_wavespeed_integration.py
```

### 手动测试步骤

1. 启动后端和前端
2. 配置 MCP 服务器
3. 在聊天界面输入："Generate a cute cat image"
4. 观察系统是否自动调用 text_to_image 工具
5. 检查返回的图片链接

## 📊 配置验证

使用以下 API 调用验证配置：

```bash
curl -X POST http://localhost:8000/api/mcp/server/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "transport": "stdio",
    "command": "wavespeed-mcp",
    "args": [],
    "env": {
      "WAVESPEED_API_KEY": "e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208"
    }
  }'
```

应该返回包含三个工具的 JSON 响应。

## 🎯 最佳实践

1. **明确的提示词**: 使用清晰、具体的描述
2. **英文提示**: 确保提示词为英文以获得最佳效果
3. **耐心等待**: 图片生成可能需要30-60秒
4. **监控日志**: 查看浏览器控制台获取详细信息

## 📝 示例对话

**用户**: "Please generate a realistic image of a sunset beach scene"

**系统响应**:
1. 生成计划："调用图像生成工具生成图片"
2. 自动接受计划（如果启用了自动接受）
3. 调用 `text_to_image` 工具
4. 返回生成的图片链接

**预期结果**: 系统会直接生成图片，而不是跳转到交互界面

---

**配置完成后，您就可以通过自然语言对话来生成高质量的图片和视频了！** 🎉 