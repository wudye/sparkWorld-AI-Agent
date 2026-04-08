import asyncio
from contextlib import AsyncExitStack

from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client


async def main() -> None:
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            r"H:\sparkworld\ basicKnowledge\12mcp",  # NOTE: no leading space
            "run",
            "1mcpServerDemo.py",
        ],
        env=None,
    )

    exit_stack = AsyncExitStack()

    try:
        # Connect to the MCP server over stdio
        stdio, write = await exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # Create a client session on top of the streams
        session = await exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )

        # Initialize the session (handshake)
        await session.initialize()

        # List tools exposed by the server
        list_tools_response = await session.list_tools()
        tools = list_tools_response.tools
        print("Available tools:", tools)

        # Call the "calculator" tool with a sample expression
        call_tool_response = await session.call_tool(
            "calculator", {"expression": "12 * 355"}
        )
        print("Tool response:", call_tool_response.content)

    finally:
        # Make sure everything is cleaned up
        await exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(main())
