from mcp.server.fastmcp import FastMCP

API_BASE = "https://word-assistant"

mcp = FastMCP('word-assistant')

@mcp.tool(name='word文档生成助手')
async def generate(text: str) -> str:
    """word生成

    Args:
        state: 模型返回的文本内容
    """

    return None

def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()

    
