import asyncio
import sys
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

from mcpCode import run_code
async def test():
    print(await run_code("python", "print(1 + 2 + 3)"))
    print(await run_code("python", "x = 10\nprint(x * 5)"))

    # Test JavaScript code (requires node installed and on PATH)
    print(await run_code("node", "console.log(7 * 6);"))

asyncio.run(test())

from mcpBase import bash

async def test():
    # Simple command
    result = await bash("echo hello from bash tool")
    print(result)

    # A directory listing (Windows PowerShell/cmd syntax)
    result = await bash("dir")
    print(result["returncode"])
    print(result["stdout"][:200])  # print first 200 chars

asyncio.run(test())

