#!/usr/bin/env python3
"""
测试MCP工具分配给不同agent的配置
"""

from src.graph.nodes import _get_mcp_servers, _get_mcp_tools_for_agent

def test_mcp_agent_assignment():
    """测试MCP工具分配配置"""
    
    # 测试配置
    config = {
        'configurable': {
            'mcp_settings': {
                'servers': {
                    'Wavespeed': {
                        'transport': 'stdio',
                        'command': 'wavespeed-mcp',
                        'args': [],
                        'env': {
                            'WAVESPEED_API_KEY': 'e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208'
                        },
                        'enabled_tools': ['text_to_image', 'image_to_image', 'image_to_video'],
                        'add_to_agents': ['image_generator'],  # 只分配给image_generator
                    }
                }
            }
        }
    }

    print('🔧 测试MCP工具分配配置...\n')
    
    print('MCP服务器配置:')
    mcp_servers = _get_mcp_servers(config)
    print(f'  MCP服务器: {list(mcp_servers.keys()) if mcp_servers else "无"}')
    
    print('\nResearcher可用的MCP工具:')
    try:
        researcher_tools = _get_mcp_tools_for_agent(config, 'researcher')
        print(f'  Researcher MCP工具: {researcher_tools}')
    except Exception as e:
        print(f'  获取researcher MCP工具出错: {e}')

    print('\nImage_generator可用的MCP工具:')
    try:
        image_generator_tools = _get_mcp_tools_for_agent(config, 'image_generator') 
        print(f'  Image_generator MCP工具: {image_generator_tools}')
    except Exception as e:
        print(f'  获取image_generator MCP工具出错: {e}')
    
    # 测试如果给researcher分配工具会如何
    print('\n测试给researcher分配MCP工具:')
    config_with_researcher = {
        'configurable': {
            'mcp_settings': {
                'servers': {
                    'Wavespeed': {
                        'transport': 'stdio',
                        'command': 'wavespeed-mcp',
                        'args': [],
                        'env': {
                            'WAVESPEED_API_KEY': 'e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208'
                        },
                        'enabled_tools': ['text_to_image', 'image_to_image', 'image_to_video'],
                        'add_to_agents': ['researcher', 'image_generator'],  # 给两个都分配
                    }
                }
            }
        }
    }
    
    try:
        researcher_tools_new = _get_mcp_tools_for_agent(config_with_researcher, 'researcher')
        print(f'  新配置下Researcher MCP工具: {researcher_tools_new}')
    except Exception as e:
        print(f'  获取researcher MCP工具出错: {e}')

if __name__ == "__main__":
    test_mcp_agent_assignment() 