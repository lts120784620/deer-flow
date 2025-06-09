#!/usr/bin/env python3
"""
测试前端 MCP 配置是否正确
"""

import requests
import json
import time

def test_with_frontend_mcp_config():
    """使用前端 MCP 配置格式测试"""
    print("🧪 测试带有前端 MCP 配置的请求...")
    
    # 模拟前端发送的配置格式
    mcp_settings = {
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
    
    test_request = {
        "messages": [{"role": "user", "content": "请生成一张可爱的小猫图片，要求高质量"}],
        "thread_id": f"frontend_test_{int(time.time())}",
        "auto_accepted_plan": True,
        "max_plan_iterations": 1,
        "max_step_num": 3,
        "max_search_results": 3,
        "enable_background_investigation": False,
        "mcp_settings": mcp_settings
    }
    
    print(f"📡 发送配置:")
    print(json.dumps(mcp_settings, indent=2, ensure_ascii=False))
    print()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat/stream",
            json=test_request,
            stream=True,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP 错误: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
        
        print("✅ 请求发送成功，解析响应...")
        
        tool_calls = []
        messages = []
        plans = []
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        
                        # 记录消息内容
                        if 'content' in data and data.get('content'):
                            content = data['content']
                            messages.append(content)
                            
                            # 检查是否提到了 wavespeed 或图片生成
                            if any(keyword in content.lower() for keyword in ['text_to_image', 'wavespeed', '图片', 'image']):
                                plans.append(content)
                                print(f"📝 计划内容: {content[:100]}...")
                        
                        # 记录工具调用
                        if 'tool_calls' in data:
                            for tool_call in data['tool_calls']:
                                tool_name = tool_call.get('name', '')
                                if tool_name:
                                    tool_calls.append(tool_name)
                                    print(f"🔧 调用工具: {tool_name}")
                                    
                                    # 检查参数
                                    if tool_name in ['text_to_image', 'image_to_image', 'generate_video']:
                                        args = tool_call.get('args', {})
                                        print(f"   参数: {args}")
                        
                        # 检查工具调用结果
                        if 'tool_call_result' in data:
                            print(f"📤 工具调用结果: {data['tool_call_result'][:100]}...")
                            
                    except json.JSONDecodeError:
                        pass
        
        # 分析结果
        print(f"\n📊 测试结果:")
        print(f"   工具调用: {tool_calls}")
        print(f"   消息数量: {len(messages)}")
        print(f"   计划数量: {len(plans)}")
        
        # 检查是否成功调用了 WaveSpeed 工具
        wavespeed_tools = ['text_to_image', 'image_to_image', 'generate_video']
        called_wavespeed = any(tool in tool_calls for tool in wavespeed_tools)
        
        if called_wavespeed:
            print("🎉 成功调用了 WaveSpeed 工具!")
            return True
        elif tool_calls:
            print(f"⚠️  调用了其他工具: {tool_calls}")
            print("   可能 MCP 配置没有生效，或者没有识别到图片生成意图")
            return False
        else:
            print("❌ 没有调用任何工具")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_common_issues():
    """检查常见问题"""
    print("\n" + "="*60)
    print("🔍 常见问题检查")
    print("="*60)
    
    print("\n1. 前端配置格式检查:")
    print("   正确格式应该是:")
    correct_config = {
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
    print(json.dumps(correct_config, indent=4, ensure_ascii=False))
    
    print("\n2. 检查项目:")
    print("   ✅ 服务器配置 - 需要添加到前端 MCP 设置")
    print("   ✅ 启用状态 - 确保服务器开关为绿色")
    print("   ✅ 工具加载 - 配置后应该看到 3 个工具")
    
    print("\n3. 测试步骤:")
    print("   1. 访问 http://localhost:3000")
    print("   2. 点击右上角设置图标（齿轮）")
    print("   3. 选择 'MCP Servers' 标签页")
    print("   4. 点击 'Add Servers' 按钮")
    print("   5. 粘贴上面的配置")
    print("   6. 保存并确保启用")
    print("   7. 在聊天中输入: '请生成一张可爱的小猫图片'")

if __name__ == "__main__":
    print("🚀 前端 MCP 配置测试")
    print("="*40)
    
    # 运行测试
    success = test_with_frontend_mcp_config()
    
    # 检查常见问题
    check_common_issues()
    
    if not success:
        print("\n⚠️  如果工具没有被调用，请检查:")
        print("   1. 前端 MCP 配置是否正确添加")
        print("   2. 服务器是否已启用（绿色开关）")
        print("   3. 页面是否已刷新")
        print("   4. 浏览器控制台是否有错误信息") 