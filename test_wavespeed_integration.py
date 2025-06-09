#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WaveSpeed MCP 集成测试脚本
测试 DeerFlow 与真实 WaveSpeed MCP 服务器的集成
"""

import requests
import json
import os
import time

def test_wavespeed_integration():
    """测试 WaveSpeed MCP 集成"""
    
    # 检查是否设置了 API 密钥
    api_key = os.getenv("WAVESPEED_API_KEY")
    if not api_key:
        print("⚠️  请设置 WAVESPEED_API_KEY 环境变量")
        print("   export WAVESPEED_API_KEY=your_api_key_here")
        return
    
    print(f"🔑 使用 API 密钥: {api_key[:10]}...")
    
    # 测试请求列表
    test_requests = [
        {
            "description": "文本生成图片 - 可爱小猫",
            "prompt": "请帮我生成一张可爱的小猫咪的图片，要求是现实主义风格",
            "expected_tool": "text_to_image"
        },
        {
            "description": "文本生成图片 - 科幻城市",
            "prompt": "生成一个未来科幻风格的城市景观图片，包含飞行汽车和高楼大厦",
            "expected_tool": "text_to_image"
        },
        {
            "description": "图片转视频请求",
            "prompt": "将一张静态的海滩日落图片转换为动态视频，时长5秒",
            "expected_tool": "image_to_video"
        }
    ]
    
    for i, test_case in enumerate(test_requests, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {test_case['description']}")
        print(f"提示词: {test_case['prompt']}")
        print(f"期望工具: {test_case['expected_tool']}")
        print("-" * 60)
        
        try:
            # 发送请求到聊天API
            response = requests.post(
                "http://localhost:8000/api/chat/stream",
                json={
                    "messages": [{"role": "user", "content": test_case['prompt']}],
                    "thread_id": f"test_{i}_{int(time.time())}",
                    "resources": [],
                    "max_plan_iterations": 1,
                    "max_step_num": 3,
                    "max_search_results": 3,
                    "auto_accepted_plan": True,
                    "enable_background_investigation": False,
                    "mcp_settings": {
                        "servers": {
                            "mcp-wavespeed": {
                                "transport": "stdio",
                                "command": "wavespeed-mcp",
                                "args": [],
                                "env": {
                                    "WAVESPEED_API_KEY": api_key,
                                    "WAVESPEED_API_RESOURCE_MODE": "url",
                                    "WAVESPEED_LOG_LEVEL": "INFO"
                                },
                                "enabled_tools": ["text_to_image", "image_to_image", "image_to_video"],
                                "add_to_agents": ["researcher"],
                            }
                        }
                    }
                },
                stream=True,
                timeout=120  # 2分钟超时
            )
            
            if response.status_code != 200:
                print(f"❌ HTTP 错误: {response.status_code}")
                print(f"   响应: {response.text}")
                continue
            
            # 处理流式响应
            tool_calls_found = []
            messages_received = []
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            
                            # 记录工具调用
                            if 'tool_calls' in data:
                                for tool_call in data['tool_calls']:
                                    tool_name = tool_call.get('function', {}).get('name', 'unknown')
                                    tool_calls_found.append(tool_name)
                                    print(f"🔧 调用工具: {tool_name}")
                            
                            # 记录消息内容
                            if 'content' in data and data['content']:
                                content = data['content']
                                messages_received.append(content)
                                print(f"💬 响应: {content[:100]}{'...' if len(content) > 100 else ''}")
                                
                        except json.JSONDecodeError:
                            pass
            
            # 分析结果
            print(f"\n📊 测试结果:")
            print(f"   工具调用: {tool_calls_found}")
            print(f"   消息数量: {len(messages_received)}")
            
            # 检查是否调用了期望的工具
            expected_tool = test_case['expected_tool']
            if any(expected_tool in tool for tool in tool_calls_found):
                print(f"✅ 成功调用了期望的工具: {expected_tool}")
            elif tool_calls_found:
                print(f"⚠️  调用了其他工具: {tool_calls_found}")
            else:
                print(f"❌ 没有调用任何 WaveSpeed 工具")
            
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except requests.exceptions.ConnectionError:
            print("❌ 连接错误 - 请确保服务器正在运行")
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        print(f"{'='*60}")

def test_server_health():
    """测试服务器健康状态"""
    print("🏥 检查服务器健康状态...")
    
    try:
        response = requests.get("http://localhost:8000/api/rag/config", timeout=5)
        if response.status_code == 200:
            print("✅ DeerFlow 服务器运行正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 DeerFlow 服务器")
        print("   请确保服务器正在运行: python server.py --reload")
        return False
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 WaveSpeed MCP 集成测试")
    print("=" * 60)
    
    # 检查环境变量
    api_key = os.getenv("WAVESPEED_API_KEY")
    if not api_key:
        print("❌ 缺少必要的环境变量")
        print("\n📋 设置步骤:")
        print("1. 获取 WaveSpeed API 密钥: https://wavespeed.ai")
        print("2. 设置环境变量: export WAVESPEED_API_KEY=your_api_key_here")
        print("3. 启动 DeerFlow 服务器: python server.py --reload")
        print("4. 重新运行此测试: python test_wavespeed_integration.py")
        return
    
    # 检查服务器状态
    if not test_server_health():
        return
    
    # 运行集成测试
    test_wavespeed_integration()
    
    print("\n🎉 测试完成!")
    print("\n📚 更多信息:")
    print("- WaveSpeed MCP 文档: https://github.com/WaveSpeedAI/mcp-server")
    print("- DeerFlow 图片生成指南: IMAGE_GENERATION_GUIDE.md")
    print("- WaveSpeed 设置指南: WAVESPEED_SETUP_GUIDE.md")

if __name__ == "__main__":
    main() 