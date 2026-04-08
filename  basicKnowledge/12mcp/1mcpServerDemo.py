import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
async def calculator(expression:str) -> str:
    """a simple calculator tool demo"""
    try:
        result = eval(expression)
        print("test")
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"Invalid expression: {e}"})


if __name__ == "__main__":
    mcp.run(transport="stdio")