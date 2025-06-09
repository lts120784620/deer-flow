#!/usr/bin/env python3
"""
直接测试图像生成handoff功能
"""

import asyncio
import logging
from src.graph import build_graph

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_image_handoff_direct():
    """直接测试图像生成handoff"""
    
    print("🎨 测试图像生成handoff...")
    
    # 配置
    config = {
        "configurable": {
            "thread_id": "test_image_direct",
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
        "recursion_limit": 50,
    }
    
    # 明确要求生成图像的任务
    initial_state = {
        "messages": [{"role": "user", "content": "请生成一张AI技术发展趋势的专业图表图像，显示不同技术的发展时间线和应用领域"}],
        "auto_accepted_plan": True,
        "enable_background_investigation": False,
    }
    
    try:
        # 构建graph
        graph = build_graph()
        print("✅ Graph构建成功")
        
        # 执行workflow
        print("🚀 开始执行workflow...")
        
        handoff_detected = False
        image_generator_executed = False
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
                            
                            # 检查handoff信号
                            if "HANDOFF_TO_IMAGE_GENERATOR:" in content:
                                handoff_detected = True
                                print("🔄 检测到图像生成handoff!")
                                print(f"Handoff内容: {content[:300]}...")
                            
                            # 检查image_generator响应
                            if hasattr(last_message, "name") and last_message.name == "image_generator":
                                image_generator_executed = True
                                print("🖼️ Image_generator执行成功!")
                                print(f"生成结果: {content[:300]}...")
                    
                    final_state = state
                    
            except Exception as e:
                logger.error(f"处理状态时出错: {e}")
                continue
        
        print("\n✅ Workflow执行完成!")
        
        # 结果分析
        print("\n📋 结果分析:")
        if handoff_detected:
            print("✅ 成功检测到researcher handoff!")
        else:
            print("❌ 未检测到researcher handoff")
        
        if image_generator_executed:
            print("✅ Image_generator成功执行!")
        else:
            print("❌ Image_generator未执行")
        
        return final_state
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🎯 开始测试图像生成handoff...\n")
    asyncio.run(test_image_handoff_direct())
    print("\n🎉 测试完成!") 