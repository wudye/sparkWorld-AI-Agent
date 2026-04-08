import subprocess
from mcp.server.fastmcp import FastMCP
from sympy import resultant

mcp = FastMCP("Bash tool")

@mcp.tool()
async def bash(command: str) -> str:
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True

    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")