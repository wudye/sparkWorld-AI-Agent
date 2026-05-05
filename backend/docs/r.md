from fastapi import Request, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
import json

# 不需要认证的路径白名单
PUBLIC_PATHS = ["/", "/docs", "/openapi.json", "/redoc", "/health", "/auth/login"]

async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    
    api_key = request.headers.get("X-API-Key")
    auth_header = request.headers.get("Authorization")
    
    if api_key != "your-secret-api-key" and not auth_header:
        raise HTTPException(status_code=401, detail="需要认证")
    
    response = await call_next(request)
    return response

# 在 main.py 中注册
# app.middleware("http")(auth_middleware)





The user is asking about how to import `get_logger` from `utils.log_config` in the `app/routers/agents.py` file. They want to know if they need to set up `__init__.py` files for the import to work.

Let me check the current project structure to understand the module hierarchy.
让我先看看你的项目结构，确认导入路径。
Now I understand the project structure:

```
backend/
├── main.py                    ← 启动文件
├── utils/
│   ├── __init__.py            ← 空文件
│   └── log_config.py          ← get_logger 在这里
├── app/
│   ├── __init__.py            ← 空文件
│   └── routers/
│       ├── __init__.py        ← 空文件
│       └── agents.py          ← 用户在这里想导入 get_logger
```

The user is asking: `from utils.log_config import get_logger` — is this the right way? And should `__init__.py` files exist?

The answer is:
1. `__init__.py` files already exist (they're empty files)
2. Since all packages have `__init__.py`, and `backend/` is the working directory (or has a `pyproject.toml`), the import `from utils.log_config import get_logger` should work fine.

But the question is about how running `uvicorn main:app` will resolve the import. When running from `backend/`:
- `main.py` is at `backend/main.py`
- `from utils.log_config import get_logger` works because Python can find `utils` as a package

But when `agents.py` (at `backend/app/routers/agents.py`) imports:
- `from utils.log_config import get_logger` — this should work because `backend/` is the working directory and Python's sys.path includes the current directory.

However, the user might be wondering about how to make it work. The answer is:
1. `__init__.py` files are already in place ✅
2. Import statement is correct ✅
3. The key is that when running `uvicorn main:app` from `backend/`, Python can resolve `utils.log_config` because `backend/` is in `sys.path`

But there's one thing to consider: if they run the app from `app/routers/` or some other directory, the import might break. The safest approach is to either:
1. Always run from `backend/`
2. Or use relative imports: `from ...utils.log_config import get_logger` (but this requires the module to be part of a package)

Actually, since `agents.py` is inside `app.routers` package, relative imports would be:
```python
from ...utils.log_config import get_logger
```
But this is fragile. The better approach is to ensure the project root is in Python path.

Let me check the `pyproject.toml` to see if there's any path configuration.
你的 `__init__.py` 文件**已经在所有目录中存在了**（虽然都是空文件），所以导入路径是正确的。

## 你的目录结构

```
backend/                      ← 运行目录（Python 自动加入 sys.path）
├── utils/                    ← 有 __init__.py
│   ├── __init__.py
│   └── log_config.py
├── app/                      ← 有 __init__.py
│   ├── __init__.py
│   └── routers/
│       ├── __init__.py
│       └── agents.py         ← 你在这里
```

## 直接写这个 import 即可

在 `agents.py` 中：

```python:app/routers/agents.py
from utils.log_config import get_logger  # ✅ 路径正确

logger = get_logger(__name__)
```

## 为什么能正常工作

当你从 `backend/` 目录运行 `uvicorn main:app`：

```
Python 寻找 utils.log_config:
  ① sys.path 包含 backend/（当前目录）
  ② 找到 backend/utils/（有 __init__.py → 是包）
  ③ 找到 backend/utils/log_config.py
  ④ 导入成功 ✅
```

## `__init__.py` 的作用

| 有 `__init__.py` | 没有 `__init__.py` |
|-----------------|-------------------|
| `utils/` 被视为**包** | `utils/` 只是普通目录 |
| `from utils.log_config import ...` ✅ | `from utils.log_config import ...` ❌ 报错 |

你现在的 `__init__.py` 都是空文件，但已经足够让 Python 识别这些目录为包。

## 一个可选的改进

如果你想让导入更直观，可以在 `utils/__init__.py` 中**直接暴露**常用的函数：

```python:utils/__init__.py
from .log_config import setup_logger, get_logger
```

然后 `agents.py` 中就可以更简洁地导入：


```python:app/routers/agents.py
from utils import get_logger  # ✅ 更简洁

logger = get_logger(__name__)
```

不过两种写法都可以，看你个人偏好。**当前直接用 `from utils.log_config import get_logger` 完全没有问题。**