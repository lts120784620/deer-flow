#!/usr/bin/env python3
"""
测试新的图像生成agent架构
验证researcher -> image_generator的handoff流程
"""

import asyncio
import logging
import os
from src.graph import build_graph
from src.graph.types import State
from src.config.configuration import Configuration

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_image_agent_handoff():
    """测试图像生成agent的handoff流程"""
    
    print("🎨 测试新的图像生成agent架构...")
    
    # 创建测试配置
    config = {
        "configurable": {
            "thread_id": "test_image_handoff",
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "mcp_settings": {
                "servers": {
                    "Wavespeed": {
                        "transport": "stdio",
                        "command": "wavespeed-mcp",
                        "args": [],
                        "env": {
                            "WAVESPEED_API_KEY": "e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208"
                        },
                        "enabled_tools": ["text_to_image", "image_to_image", "image_to_video"],
                        "add_to_agents": ["image_generator"],
                    }
                }
            },
        },
        "recursion_limit": 100,
    }
    
    # 创建初始状态
    initial_state = {
        "messages": [{"role": "user", "content": "请生成一张显示AI技术发展趋势的图片"}],
        "auto_accepted_plan": True,
        "enable_background_investigation": True,
    }
    
    try:
        # 构建graph
        graph = build_graph()
        print("✅ Graph构建成功")
        
        # 执行workflow
        print("🚀 开始执行workflow...")
        
        final_state = None
        async for state in graph.astream(initial_state, config=config, stream_mode="values"):
            try:
                if isinstance(state, dict):
                    print(f"📊 当前状态: {list(state.keys())}")
                    
                    # 检查消息
                    if "messages" in state and state["messages"]:
                        last_message = state["messages"][-1]
                        if hasattr(last_message, "content"):
                            content = last_message.content
                            if "HANDOFF_TO_IMAGE_GENERATOR:" in content:
                                print("🔄 检测到图像生成handoff!")
                                print(f"Handoff内容: {content}")
                            elif "image" in content.lower() or "图" in content:
                                print("🖼️ 检测到图像相关内容!")
                                print(f"内容片段: {content[:200]}...")
                    
                    # 保存最终状态
                    final_state = state
                    
            except Exception as e:
                logger.error(f"处理状态时出错: {e}")
                continue
        
        print("\n✅ Workflow执行完成!")
        
        # 分析结果
        if final_state:
            print("\n📋 最终结果分析:")
            
            if "final_report" in final_state:
                report = final_state["final_report"]
                print(f"📄 最终报告长度: {len(report)}字符")
                
                if "http" in report and ("image" in report.lower() or "图" in report):
                    print("✅ 检测到生成的图像URL!")
                    # 提取URL
                    import re
                    urls = re.findall(r'https?://[^\s)]+', report)
                    for url in urls:
                        print(f"🔗 发现URL: {url}")
                else:
                    print("❌ 未检测到图像生成结果")
            
            if "messages" in final_state:
                print(f"📬 总消息数: {len(final_state['messages'])}")
                
                # 查找handoff消息
                handoff_found = False
                for msg in final_state["messages"]:
                    if hasattr(msg, "content") and "HANDOFF_TO_IMAGE_GENERATOR:" in msg.content:
                        handoff_found = True
                        print("✅ 发现handoff消息!")
                        break
                
                if not handoff_found:
                    print("❌ 未发现handoff消息")
        
        return final_state
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_direct_image_generator():
    """直接测试image_generator node"""
    print("\n🔧 直接测试image_generator node...")
    
    from src.graph.nodes import image_generator_node
    
    # 创建模拟状态，包含图像生成请求
    state = {
        "current_plan": {
            "steps": [{
                "title": "生成图像",
                "description": "HANDOFF_TO_IMAGE_GENERATOR: A futuristic AI robot in a laboratory | Type: text_to_image | Style: high quality, realistic",
                "execution_res": None
            }]
        },
        "messages": [],
        "observations": []
    }
    
    config = {
        "configurable": {
            "thread_id": "test_direct",
            "mcp_settings": {
                "servers": {
                    "Wavespeed": {
                        "transport": "stdio",
                        "command": "wavespeed-mcp",
                        "args": [],
                        "env": {
                            "WAVESPEED_API_KEY": "e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208"
                        },
                        "enabled_tools": ["text_to_image", "image_to_image", "image_to_video"],
                        "add_to_agents": ["image_generator"],
                    }
                }
            },
        },
    }
    
    try:
        result = await image_generator_node(state, config)
        print("✅ image_generator node执行成功!")
        print(f"结果: {result}")
        return result
        
    except Exception as e:
        print(f"❌ image_generator node测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🎯 开始测试图像生成agent架构...\n")
    
    # 测试完整流程
    asyncio.run(test_image_agent_handoff())
    
    # 测试直接调用
    asyncio.run(test_direct_image_generator())
    
    print("\n🎉 测试完成!") 