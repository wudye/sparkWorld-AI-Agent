import  asyncio
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

async  def main() -> None:
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            "H:\\sparkworld\\ basicKnowledge\\12mcp",
            "run",
            "1mcpServerDemo.py"
        ],
        env=None
    )

    async with stdio_client(server_params) as transport:
        stdio, write = transport
        async with ClientSession(stdio, write) as session:
            await session.initialize()

            list_tools_response = await session.list_tools()
            tools = list_tools_response.tools
            print("Available tools:", tools)

            call_tool_response = await session.call_tool(
                "calculator", {"expression": "12 * 355"}
            )
            print("Tool response:", call_tool_response.content)



if __name__ == "__main__":
    asyncio.run(main())