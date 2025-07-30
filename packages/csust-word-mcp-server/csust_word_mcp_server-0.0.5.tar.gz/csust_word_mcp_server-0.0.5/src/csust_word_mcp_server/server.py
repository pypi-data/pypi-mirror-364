from fastmcp import FastMCP
import asyncio

API_BASE = "https://word-assistant"

mcp = FastMCP('word-assistant')

@mcp.tool(name='word文档生成助手')
async def generate(text: str) -> str:
    """word生成

    Args:
        state: 模型返回的文本内容
    """

    return text

def main():
    # asyncio.run(mcp.run_sse_async(host="0.0.0.0", port=8000))
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

    
