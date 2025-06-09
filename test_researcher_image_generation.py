#!/usr/bin/env python3
"""
测试researcher agent的图像生成功能
"""

import asyncio
import json
import logging
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_core.runnables import RunnableConfig
from src.graph.nodes import researcher_node
from src.graph.types import State
from src.prompts.planner_model import Plan, Step

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_researcher_image_generation():
    """测试researcher是否能识别和执行图像生成任务"""
    
    print("🎨 测试researcher agent的图像生成功能...")
    
    # 读取MCP配置
    try:
        with open('.deerflow/config.json', 'r') as f:
            config_data = json.load(f)
        mcp_settings = config_data.get('mcp_settings')
        if not mcp_settings:
            print("❌ 未找到MCP设置")
            return
        print(f"✅ MCP设置加载成功: {list(mcp_settings.get('servers', {}).keys())}")
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return
    
    # 创建包含图像生成任务的plan
    plan = Plan(
        locale="zh-CN",
        title="为美丽的日落景色生成展示图片",
        thought="用户要求生成一张美丽的日落景色图片用于展示",
        has_enough_context=True,
        steps=[
            Step(
                need_search=False,
                title="生成日落景色图片",
                description="创建一张美丽的日落景色图片，包含温暖的色调和宁静的氛围，用于展示目的。请生成高质量的图像并提供图片描述。",
                step_type="processing",
                execution_res=""  # 空的，等待执行
            )
        ]
    )
    
    # 创建state
    state: State = {
        "messages": [
            {"role": "user", "content": "请为我生成一张美丽的日落景色图片"}
        ],
        "locale": "zh-CN",
        "current_plan": plan,
        "observations": []
    }
    
    # 创建配置 - 包含MCP设置
    config = RunnableConfig(
        configurable={
            "user_id": "test_user",
            "thread_id": "test_thread",
            "mcp_settings": mcp_settings,
            "max_search_results": 3
        }
    )
    
    try:
        print("🔍 调用researcher_node执行图像生成任务...")
        result = await researcher_node(state, config)
        
        print("✅ researcher_node执行完成")
        print(f"📋 返回结果类型: {type(result)}")
        print(f"📄 返回结果: {result}")
        
        # 检查执行结果
        if "update" in result and "observations" in result["update"]:
            observations = result["update"]["observations"]
            if observations:
                latest_observation = observations[-1]
                print(f"📝 最新研究结果长度: {len(latest_observation)} 字符")
                print(f"🔍 研究结果预览: {latest_observation[:200]}...")
                
                # 检查是否包含图像生成的内容
                if "text_to_image" in latest_observation.lower() or "generated" in latest_observation.lower():
                    print("🎉 ✅ 检测到图像生成工具的使用！")
                else:
                    print("⚠️ 未检测到图像生成工具的使用")
                
                if "http" in latest_observation and ("cloudfront" in latest_observation or "wavespeed" in latest_observation):
                    print("🖼️ ✅ 检测到生成的图像URL！")
                else:
                    print("❌ 未检测到生成的图像URL")
        
    except Exception as e:
        print(f"❌ researcher_node执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_researcher_image_generation()) 