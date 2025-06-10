import asyncio
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_wavespeed_mcp():
    mcp_servers = {
        "Wavespeed": {
            "transport": "stdio",
            "command": "wavespeed-mcp",
            "args": [],
            "env": {
                "WAVESPEED_API_KEY": "e1a55eafd82c53eb1ae658096ed4104e86dcdae7d85c918d02b06092b6ae9208"
            }
        }
    }
    logger.info("开始测试 Wavespeed MCP...")

    try:
        client = MultiServerMCPClient(mcp_servers)
        tools = await client.get_tools()
        logger.info(f"获取到的工具: {[tool.name for tool in tools]}")
        text_to_image_tool = next((tool for tool in tools if tool.name == "text_to_image"), None)
        if not text_to_image_tool:
            logger.error("未找到 text_to_image 工具")
            return
        logger.info("开始生成图片...")
        result = await text_to_image_tool.ainvoke({
            "prompt": "A cute kitten playing with a ball of yarn, high quality, detailed",
            "negative_prompt": "blurry, low quality, distorted",
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 50,
            "guidance_scale": 7.5
        })
        logger.info(f"图片生成结果: {result}")
    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}", exc_info=True)

def main():
    print("🚀 WaveSpeed MCP 最小测试")
    print("=" * 60)
    asyncio.run(test_wavespeed_mcp())
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    main()