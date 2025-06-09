#!/usr/bin/env python3
"""
简单的MCP直接调用测试
直接在coordinator_node中测试MCP工具调用
"""

import asyncio
import logging
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_core.runnables import RunnableConfig
from src.graph.nodes import coordinator_node
from src.graph.types import State
from src.config.configuration import Configuration

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_simple_mcp():
    """简单的MCP测试 - 修改为同步版本"""
    
    print("🚀 开始简单MCP测试...")
    
    # 直接读取配置文件
    print("📋 读取配置文件...")
    try:
        import json
        with open('.deerflow/config.json', 'r') as f:
            config_data = json.load(f)
        mcp_settings = config_data.get('mcp_settings')
        if mcp_settings:
            print(f"✅ MCP设置加载成功: {list(mcp_settings.get('servers', {}).keys())}")
        else:
            print("❌ 未找到MCP设置")
            return
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return
    
    # 创建基本的state
    state: State = {
        "messages": [
            {"role": "user", "content": "生成一张美丽的日落图片"}
        ],
        "locale": "zh-CN"
    }
    
    # 创建配置 - 直接传入MCP设置
    config = RunnableConfig(
        configurable={
            "user_id": "test_user",
            "thread_id": "test_thread",
            "mcp_settings": mcp_settings
        }
    )
    
    try:
        print("📞 调用coordinator_node...")
        result = coordinator_node(state, config)
        print(f"✅ coordinator_node调用成功")
        print(f"📋 返回结果: {result}")
        
    except Exception as e:
        print(f"❌ coordinator_node调用失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_mcp() 