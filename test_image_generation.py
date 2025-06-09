#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_image_generation():
    """测试图片生成功能"""
    
    # 测试请求
    test_requests = [
        "请帮我生成一张可爱的小猫咪的图片",
        "生成一个科幻风格的城市景观图片",
        "创建一个卡通风格的森林场景",
        "制作一个现实主义风格的日落海滩图片"
    ]
    
    for prompt in test_requests:
        print(f"\n测试提示词: {prompt}")
        print("-" * 50)
        
        # 发送请求到聊天API
        response = requests.post(
            "http://localhost:8000/api/chat/stream",
            json={
                "messages": [{"role": "user", "content": prompt}],
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
        
        # 处理流式响应
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if 'content' in data:
                            print(f"响应: {data['content']}")
                    except json.JSONDecodeError:
                        pass
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    test_image_generation() 