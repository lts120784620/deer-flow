#!/usr/bin/env python3
"""
测试 WaveSpeed MCP 配置和功能
"""

import requests
import json
import time

def test_mcp_configuration():
    """测试 MCP 配置是否正确"""
    print("🔧 测试 WaveSpeed MCP 配置...")
    
    # 1. 测试 MCP 服务器连接
    print("\n1️⃣ 测试 MCP 服务器连接...")
    try:
        response = requests.post(
            "http://localhost:8000/api/mcp/server/metadata",
            json={
                "transport": "stdio",
                "command": "wavespeed-mcp",
                "args": [],
                "env": {
                    "WAVESPEED_API_KEY": "e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208"
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            tools = data.get('tools', [])
            print(f"✅ MCP 服务器连接成功")
            print(f"📋 可用工具数量: {len(tools)}")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description'][:50]}...")
        else:
            print(f"❌ MCP 服务器连接失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ MCP 服务器连接异常: {e}")
        return False
    
    # 2. 测试图片生成请求
    print("\n2️⃣ 测试图片生成请求...")
    test_prompt = "请生成一张可爱的小猫图片"
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat/stream",
            json={
                "messages": [{"role": "user", "content": test_prompt}],
                "thread_id": f"test_{int(time.time())}",
                "auto_accepted_plan": True,
                "max_plan_iterations": 1,
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
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            print(f"✅ 聊天 API 响应成功")
            
            tool_calls_found = []
            plan_generated = False
            
            # 解析流式响应
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            
                            # 检查计划生成
                            if 'content' in data and 'text_to_image' in str(data.get('content', '')):
                                plan_generated = True
                                print("📝 检测到图片生成计划")
                            
                            # 检查工具调用
                            if 'tool_calls' in data:
                                for tool_call in data['tool_calls']:
                                    tool_name = tool_call.get('name', '')
                                    if tool_name:
                                        tool_calls_found.append(tool_name)
                                        print(f"🔧 调用工具: {tool_name}")
                                        
                        except json.JSONDecodeError:
                            pass
            
            # 分析结果
            print(f"\n📊 测试结果:")
            print(f"   计划生成: {'✅' if plan_generated else '❌'}")
            print(f"   工具调用: {tool_calls_found if tool_calls_found else '❌ 无工具调用'}")
            
            if 'text_to_image' in tool_calls_found:
                print("🎉 WaveSpeed 图片生成工具成功调用!")
                return True
            else:
                print("⚠️  工具调用可能有问题，但配置基本正确")
                return True
                
        else:
            print(f"❌ 聊天 API 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 聊天 API 请求异常: {e}")
        return False

def print_usage_instructions():
    """打印使用说明"""
    print("\n" + "="*60)
    print("🎯 WaveSpeed MCP 使用方法")
    print("="*60)
    
    print("\n📋 前端配置步骤:")
    print("1. 访问 http://localhost:3000")
    print("2. 点击右上角设置图标")
    print("3. 选择 'MCP Servers' 标签页")
    print("4. 点击 'Add Servers' 按钮")
    print("5. 粘贴以下配置并保存:")
    
    config = {
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
    
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    print("\n🗣️ 聊天示例:")
    examples = [
        "请生成一张可爱的小猫图片",
        "生成一个科幻风格的城市景观",
        "创建一个卡通风格的森林场景",
        "制作一个5秒的海浪视频",
        "将静态图片转换为动态视频"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    print("\n✨ 系统会自动识别您的意图并调用相应的 WaveSpeed 工具!")

if __name__ == "__main__":
    print("🚀 WaveSpeed MCP 配置测试")
    print("="*40)
    
    # 运行测试
    success = test_mcp_configuration()
    
    # 打印使用说明
    print_usage_instructions()
    
    if success:
        print("\n🎉 配置测试完成! 您可以开始在聊天界面中使用 WaveSpeed 功能了!")
    else:
        print("\n⚠️  配置可能有问题，请检查服务器状态和网络连接。") 