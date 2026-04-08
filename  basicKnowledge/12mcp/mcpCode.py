import os
import  subprocess
import uuid

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="code", port=9988)

Base_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"Base_DIR: {Base_DIR}")

UV_CMD = "uv"

@mcp.tool()
async def run_code(language: str, code: str, timeout: int=30) -> str:

    language = (language or "").strip().lower()
    if language not in ("python", "node"):
        return f"Invalid language {language}"

    suffix = ".py" if language=="python" else ".js"
    name = f"temp_{uuid.uuid4().hex}{suffix}"
    temp_path = os.path.join(Base_DIR, name)

    os.makedirs(Base_DIR,exist_ok=True)

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(code)

        cwd = Base_DIR
        if language == "python":
            cmd = [UV_CMD, "--directory", Base_DIR, "run",  name]
        else:
            cmd = ["node", temp_path]

        proc = subprocess.run(
            cmd,
            text=True,
            timeout=timeout,
            capture_output=True
        )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        if proc.returncode == 0:
            return stdout
        else:
            return f"Error: {stderr}"
    except subprocess.TimeoutExpired:
        return "Timeout"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    mcp.run(transport="stdio")