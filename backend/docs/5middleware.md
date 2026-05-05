The user wants to add middleware to their FastAPI app, specifically for recording API response time. Let me provide a comprehensive answer about middleware in FastAPI, with a focus on response time logging for their AI agent project.
好问题。AI Agent 项目通常需要记录**请求耗时**（LLM 调用可能耗时很久）、**Token 用量**等信息。以下是完整方案。

## 一、响应时间中间件

```python:utils/middleware.py
import time
import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """记录每个 API 请求的响应时间"""

    async def dispatch(self, request: Request, call_next):
        # 请求开始时间
        start_time = time.perf_counter()

        # 执行路由处理
        response = await call_next(request)

        # 计算耗时
        elapsed = time.perf_counter() - start_time
        elapsed_ms = elapsed * 1000

        # 添加响应头（方便前端/客户端查看）
        response.headers["X-Response-Time"] = f"{elapsed_ms:.0f}ms"

        # 日志记录
        logger.info(
            f"{request.method} {request.url.path} "
            f"=> {response.status_code} "
            f"[{elapsed_ms:.0f}ms]"
        )

        # 如果响应时间过长，打印警告
        if elapsed > 5:
            logger.warning(
                f"响应超时: {request.method} {request.url.path} "
                f"耗时 {elapsed:.1f}s"
            )

        return response
```

## 二、AI Agent 专属中间件（完整版）

```python:utils/middleware.py
import time
import uuid
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AIAgentMiddleware(BaseHTTPMiddleware):
    """
    AI Agent 中间件：
    - 记录请求耗时
    - 为每个请求生成唯一追踪 ID
    - 排除健康检查等静默接口
    """

    # 不需要记录日志的路径
    SILENT_PATHS = {"/health", "/healthz", "/readyz"}

    async def dispatch(self, request: Request, call_next):
        # 生成追踪 ID
        trace_id = str(uuid.uuid4())[:8]
        request.state.trace_id = trace_id
        request.state.start_time = time.perf_counter()

        # 执行路由
        response = await call_next(request)

        # 计算耗时
        elapsed = time.perf_counter() - request.state.start_time
        elapsed_ms = elapsed * 1000

        # 添加响应头
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Response-Time"] = f"{elapsed_ms:.0f}ms"

        # 跳过静默路径（健康检查不记日志）
        if request.url.path not in self.SILENT_PATHS:
            # 按耗时分级
            if elapsed > 10:
                level = "CRITICAL"
                log_func = logger.critical
            elif elapsed > 5:
                level = "WARNING"
                log_func = logger.warning
            elif elapsed > 1:
                level = "INFO"
                log_func = logger.info
            else:
                level = "DEBUG"
                log_func = logger.debug

            log_func(
                f"[{trace_id}] {request.method} {request.url.path} "
                f"=> {response.status_code} | "
                f"{elapsed_ms:.0f}ms"
            )

        return response
```

## 三、在 `main.py` 中注册

```python:main.py
from fastapi import FastAPI
from utils.middleware import AIAgentMiddleware
from utils.global_exception_handler import register_exception_handlers
from utils.logConfig import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="SparkWorld AI Agent",
        version="0.1.0",
    )

    # ====== 注册顺序：中间件 → 异常处理器 → 路由 ======

    # ① 中间件（最先注册，洋葱最外层）
    app.add_middleware(AIAgentMiddleware)

    # ② 异常处理器
    register_exception_handlers(app)

    # ③ 路由
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "healthy"}

    @app.post("/chat")
    async def chat():
        # 模拟 AI Agent 调用（可能耗时较长）
        import asyncio
        await asyncio.sleep(2)  # 模拟 LLM 响应
        return {"reply": "AI response"}

    return app

app = create_app()
```

## 四、运行效果

```
# 正常请求（小于 1 秒）
2026-05-04 15:00:00 - main - INFO - [a1b2c3d4] GET /health => 200 | 2ms

# 较慢请求（1-5 秒）
2026-05-04 15:00:05 - main - INFO - [e5f6g7h8] POST /chat => 200 | 2340ms

# 超慢请求（5-10 秒）
2026-05-04 15:00:10 - main - WARNING - [i9j0k1l2] POST /chat => 200 | 6230ms

# 极慢请求（10 秒以上）
2026-05-04 15:00:20 - main - CRITICAL - [m3n4o5p6] POST /chat => 200 | 15400ms
```

## 五、为什么中间件 > 装饰器

| 方式 | 优点 | 缺点 |
|------|------|------|
| **中间件**（推荐） | 自动覆盖所有路由，新加路由无需改动 | 无法感知函数内部状态 |
| 装饰器 `@app.middleware` | 精细控制 | 需在每个 app 上单独写 |
| 路由内部计时 | 最精确 | 每个路由都要写一遍 |

## 六、AI Agent 专属增强（可选）

```python:utils/middleware.py
class AILoggingMiddleware(BaseHTTPMiddleware):
    """AI Agent 全链路日志"""

    async def dispatch(self, request, call_next):
        trace_id = str(uuid.uuid4())[:8]
        request.state.trace_id = trace_id

        # 记录请求体（对于 /chat 接口记录消息内容）
        body = await request.body()
        if request.url.path == "/chat" and body:
            logger.info(f"[{trace_id}] 请求内容: {body[:500]}")  # 截断长文本

        response = await call_next(request)
        elapsed = time.perf_counter() - request.state.start_time

        logger.info(
            f"[{trace_id}] {request.method} {request.url.path} "
            f"=> {response.status_code} | {elapsed*1000:.0f}ms"
        )

        # 注：请求体只能读取一次，需要重置
        # 更完善的做法用 request.stream()

        return response
```

**核心思想**：AI Agent 项目里，中间件特别有用——你能自动监控到每个接口的响应时间，LLM 调用慢立刻能发现。

The user is asking what the common middleware setup is for main.py in a FastAPI project. Let me provide a concise overview of the most common middleware types that belong in main.py, explaining their purpose.
The user wants to know what the common middleware is for main.py. Let me provide a clear, practical answer about what middleware is typically found in a production FastAPI main.py, and which ones they should add.
FastAPI 项目在 `main.py` 常见的中间件按**重要性和使用率**排列如下：

## 生产环境常见中间件一览

```python
def create_app() -> FastAPI:
    app = FastAPI(...)

    # ====== ① 常见中间件（按常用顺序排列） ======

    # 1. CORS（必加）—— 允许前端跨域访问
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],                    # 生产环境改为具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. GZip 压缩（推荐）—— 压缩大响应体
    from fastapi.middleware.gzip import GZipMiddleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 3. HTTPS 重定向（生产环境）
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
    # app.add_middleware(HTTPSRedirectMiddleware)

    # 4. Trusted Host（安全）—— 防止 Host 头攻击
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.example.com"],
    )

    # 5. 请求耗时监控（你的自定义中间件）
    from utils.middleware import AIAgentMiddleware
    app.add_middleware(AIAgentMiddleware)

    # ====== ② 异常处理器 ======
    register_exception_handlers(app)

    # ====== ③ 路由 ======
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "healthy"}

    return app
```

## 各个中间件的用途

| 中间件 | 作用 | 不加的后果 | 推荐度 |
|--------|------|-----------|--------|
| **CORS** | 允许来自其他域名的浏览器请求 | 前端网页请求 API 被浏览器拦截 | ⭐ **必加** |
| **请求耗时** | 记录每个接口的响应时间 | 无法监控 API 性能 | ✅ 你的项目已实现 |
| **GZip** | 压缩大响应（>1KB） | 传输 JSON 大对象带宽浪费 | ⭐ 推荐 |
| **TrustedHost** | 防止恶意域名访问 | 可能被 Host 头攻击 | 生产环境推荐 |
| **HTTPSRedirect** | HTTP 自动跳转 HTTPS | 未加密访问 | Nginx 做更好 |

## 你的 `main.py` 目前缺什么

看你的代码，最需要加的是 **CORS**——没有它，前端页面请求你的 API 会被浏览器拦截：

```
浏览器访问 http://frontend.com
  └─ 请求 http://localhost:8000/api
       └─ ❌ 跨域被拦截（没有 CORS）
```

```python
def create_app() -> FastAPI:
    app = FastAPI(...)

    # ✅ 加这 4 行
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    # ... 路由 ...
```

**一句话**：你目前主要缺 `CORSMiddleware`，其他按需添加即可。


The user wants to understand the difference between middleware and APIRouter in FastAPI. Let me give a clear, practical explanation.
好问题，这是两个完全不同的概念，我来用类比说明。

## 本质区别

| | **Middleware（中间件）** | **APIRouter（路由分组）** |
|--|------------------------|------------------------|
| 做什么 | **在请求前后"拦截"** | **把路由集中到一个文件** |
| 关注点 | 请求处理的**过程** | 接口的**定义** |
| 类比 | 机场**安检通道** | 机场**登机口分组**（A区、B区、C区） |

## 用你的项目理解

### Middleware — 安检通道

```
          中间件                        路由                   中间件
          (拦截)                       (处理)                  (拦截)
请求进来 → [CORS检查] → [耗时计时] → /chat 路由 → [写日志] → [加响应头] → 返回
                ↑                          ↑
          每个请求都要经过           只有 /chat 才触发
          与具体路由无关             与具体 handler 绑定
```

- CORS 检查：不管是 `/chat`、`/health` 还是 `/agents`，都检查一遍
- 耗时计时：每个请求都计时，放响应头里
- **和具体接口逻辑无关**

### APIRouter — 登记口分组

```python
# routers/agents.py
router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/")          # → GET /agents/
@router.post("/")         # → POST /agents/
@router.get("/{id}")      # → GET /agents/{id}

# routers/chat.py
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")         # → POST /chat/
@router.get("/history")   # → GET /chat/history
```

- 只是把**同类型路由放在一个文件里**，便于管理
- 和不放在一起功能完全一样
- **和请求的处理过程无关**

## 关键记忆点

| 特性 | Middleware | APIRouter |
|------|-----------|-----------|
| 作用于**所有路由** | ✅ 是 | ❌ 只作用于分组内 |
| 可以**修改请求/响应** | ✅ 可加头、改体 | ❌ 只能定义接口 |
| 可以**提前终止请求** | ✅ 如 CORS 拒绝 | ❌ 只能走路由处理 |
| 定义在**单独文件** | 可以，但注册到 `app` | ✅ 注册到 `app.include_router()` |
| 执行**时机** | 请求前/后 | 请求命中时 |
| 执行的**次数** | 每个请求1次 | 只执行被调用的路由 |

## 在 `create_app()` 中的注册顺序

```python
def create_app() -> FastAPI:
    app = FastAPI()

    # ① 中间件（全局拦截器——处理每个请求的"过程"）
    app.add_middleware(CORSMiddleware, ...)
    app.add_middleware(ResponseTimeMiddleware)

    # ② 异常处理器（兜底——处理 "出错时"）
    register_exception_handlers(app)

    # ③ 路由分组（业务逻辑——"做什么"）
    from routers.agents import router as agents_router
    from routers.chat import router as chat_router
    app.include_router(agents_router)
    app.include_router(chat_router)

    return app
```

## 一句话总结

- **Middleware** = 安检通道，**所有请求**都必须经过，**和接口逻辑无关**
- **APIRouter** = 分组柜台，**只有对应请求**才触发，**就是接口逻辑本身**

```
你的项目里：
  Middleware 负责：CORS、耗时、日志、认证前置检查
  APIRouter 负责：定义 /chat、/agents、/memory 等具体接口
```