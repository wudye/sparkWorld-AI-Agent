# Day 10-11: 后端网关与基础路由

**日期**: Day 10-11 (第十-十一天)  
**目标**: 理解 FastAPI 网关架构，实现基础 CRUD 路由  
**预计时间**: 6-7 小时  
**难度**: ⭐⭐⭐ (较难)  
**前置**: 完成 Day 1-3  

---

## 📋 学习概念

### 1. FastAPI 核心概念

**优势**:
- 基于 Python Type Hints 自动生成 OpenAPI 文档
- 原生异步支持（async/await）
- 自动 JSON 序列化/反序列化
- 内置数据验证（Pydantic）

### 2. DeerFlow Gateway 架构

**职责**:
- 路由管理（/api/langgraph, /api/models 等）
- LangGraph Client 通信
- 认证和授权
- 中间件链处理
- 日志和监控

### 3. Pydantic 模型

**用于**:
- 请求体验证
- 响应序列化
- 类型安全

### 4. 异步编程

**async/await 模式**:
```python
async def handle_request():
    result = await some_async_operation()
    return result
```

---

## 🛠️ Part 1: FastAPI 基础（Day 10 上午）

### 1.1 创建最小化 Gateway 应用

创建 `backend/app/gateway/main.py`:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 实例
app = FastAPI(
    title=\"DeerFlow Gateway\",
    description=\"LangGraph 代理网关\",
    version=\"1.0.0\",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"*\"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

# 健康检查
@app.get(\"/health\")
async def health_check():
    return {\"status\": \"ok\", \"service\": \"gateway\"}

# 启动事件
@app.on_event(\"startup\")
async def startup_event():
    logger.info(\"Gateway startup\")

# 关闭事件
@app.on_event(\"shutdown\")
async def shutdown_event():
    logger.info(\"Gateway shutdown\")

if __name__ == \"__main__\":
    import uvicorn
    uvicorn.run(app, host=\"0.0.0.0\", port=8001)
```

### 1.2 创建请求/响应模型

创建 `backend/app/gateway/models.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class Thread(BaseModel):
    \"\"\"对话线程\"\"\"
    thread_id: str
    created_at: datetime
    metadata: Optional[dict] = None

class ThreadCreateRequest(BaseModel):
    \"\"\"创建线程请求\"\"\"
    config: Optional[dict] = Field(default_factory=dict)
    metadata: Optional[dict] = Field(default_factory=dict)

class ThreadCreateResponse(BaseModel):
    \"\"\"创建线程响应\"\"\"
    thread_id: str
    created_at: datetime

class MessageInput(BaseModel):
    \"\"\"消息输入\"\"\"
    input: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[dict] = None

class ModelListResponse(BaseModel):
    \"\"\"模型列表\"\"\"
    models: list[dict]
    total: int

class SkillListResponse(BaseModel):
    \"\"\"技能列表\"\"\"
    skills: list[dict]
    total: int
```

### 1.3 添加路由模块

创建 `backend/app/gateway/routes/__init__.py`（空文件）

创建 `backend/app/gateway/routes/threads.py`:

```python
from fastapi import APIRouter, HTTPException, Response
from ..models import (
    ThreadCreateRequest,
    ThreadCreateResponse,
    MessageInput,
)
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix=\"/api/langgraph\", tags=[\"LangGraph\"])

# 模拟 LangGraph 客户端
class LangGraphClient:
    async def create_thread(self, config):
        \"\"\"创建 LangGraph 线程\"\"\"
        return {\"thread_id\": str(uuid.uuid4()), \"created_at\": datetime.now()}
    
    async def stream_events(self, thread_id, input_text):
        \"\"\"流式获取事件\"\"\"
        # 模拟 SSE 事件
        yield f\"event: message\\ndata: {{\\\"role\\\": \\\"assistant\\\", \\\"content\\\": \\\"Hello from LangGraph!\\\"}}\\n\\n\"

# 全局客户端实例
langgraph_client = LangGraphClient()

@router.post(\"/threads\", response_model=ThreadCreateResponse)
async def create_thread(req: ThreadCreateRequest):
    \"\"\"创建对话线程\"\"\"
    try:
        result = await langgraph_client.create_thread(req.config)
        return ThreadCreateResponse(**result)
    except Exception as e:
        logger.error(f\"创建线程失败: {e}\")
        raise HTTPException(status_code=500, detail=\"创建线程失败\")

@router.post(\"/threads/{thread_id}/events\")
async def stream_thread_events(thread_id: str, req: MessageInput):
    \"\"\"流式获取线程事件\"\"\"
    
    async def event_generator():
        try:
            async for event in langgraph_client.stream_events(thread_id, req.input):
                yield event
        except Exception as e:
            logger.error(f\"流式事件错误: {e}\")
            yield f\"event: error\\ndata: {{\\\"message\\\": \\\"{str(e)}\\\"}}\\n\\n\"
    
    return Response(
        content=event_generator(),
        media_type=\"text/event-stream\",
        headers={
            \"Cache-Control\": \"no-cache\",
            \"Connection\": \"keep-alive\",
            \"X-Accel-Buffering\": \"no\",  # 禁用 Nginx 缓冲
        },
    )

@router.get(\"/threads/{thread_id}/state\")
async def get_thread_state(thread_id: str):
    \"\"\"获取线程状态\"\"\"
    try:
        return {
            \"thread_id\": thread_id,
            \"state\": {\"messages\": []},
            \"metadata\": {},
        }
    except Exception as e:
        logger.error(f\"获取线程状态失败: {e}\")
        raise HTTPException(status_code=500, detail=\"获取线程状态失败\")
```

---

## 🔌 Part 2: LangGraph 客户端集成（Day 10 下午）

### 2.1 创建真实 LangGraph 客户端

创建 `backend/app/gateway/langgraph_client.py`:

```python
import httpx
import logging
from typing import AsyncIterator
import json

logger = logging.getLogger(__name__)

class LangGraphClient:
    def __init__(self, base_url: str = \"http://localhost:2024\"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def create_thread(self, config: dict = None) -> dict:
        \"\"\"创建 LangGraph 线程\"\"\"
        url = f\"{self.base_url}/threads\"
        payload = {\"configurable\": config or {}}
        
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    async def stream_events(
        self, thread_id: str, input_data: dict
    ) -> AsyncIterator[str]:
        \"\"\"流式获取 LangGraph 事件\"\"\"
        url = f\"{self.base_url}/threads/{thread_id}/events\"
        
        async with self.client.stream(
            \"POST\",
            url,
            json=input_data,
            headers={\"Accept\": \"application/x-ndjson\"},
        ) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line:
                    # LangGraph 返回 NDJSON 格式
                    event = json.loads(line)
                    
                    # 转换为 SSE 格式
                    event_type = event.get(\"event\", \"message\")
                    if event_type == \"on_chat_model_stream\":
                        yield f\"event: message\\ndata: {json.dumps({'content': event.get('data', {}).get('chunk', {}).get('content', '')})}\\n\\n\"
                    elif event_type == \"on_tool_start\":
                        yield f\"event: function_call\\ndata: {json.dumps(event.get('data', {}))}\\n\\n\"
                    elif event_type == \"on_tool_end\":\n                        yield f\"event: function_result\\ndata: {json.dumps(event.get('data', {}))}\\n\\n\"\n\n    async def get_thread_state(self, thread_id: str) -> dict:\n        \"\"\"获取线程状态\"\"\"\n        url = f\"{self.base_url}/threads/{thread_id}/state\"\n        response = await self.client.get(url)\n        response.raise_for_status()\n        return response.json()\n\n    async def close(self):\n        \"\"\"关闭客户端\"\"\"\n        await self.client.aclose()\n```\n\n---\n\n## 🛣️ Part 3: 更多路由实现（Day 11 上午）\n\n### 3.1 创建模型路由\n\n创建 `backend/app/gateway/routes/models.py`:\n\n```python\nfrom fastapi import APIRouter\nfrom ..models import ModelListResponse\n\nrouter = APIRouter(prefix=\"/api\", tags=[\"Models\"])\n\n@router.get(\"/models\", response_model=ModelListResponse)\nasync def list_models():\n    \"\"\"获取可用模型列表\"\"\"\n    models = [\n        {\n            \"id\": \"gpt-4\",\n            \"name\": \"GPT-4\",\n            \"provider\": \"openai\",\n            \"capabilities\": [\"chat\", \"vision\", \"code\"],\n        },\n        {\n            \"id\": \"claude-3-sonnet\",\n            \"name\": \"Claude 3 Sonnet\",\n            \"provider\": \"anthropic\",\n            \"capabilities\": [\"chat\", \"vision\"],\n        },\n    ]\n    return ModelListResponse(models=models, total=len(models))\n```\n\n### 3.2 创建技能路由\n\n创建 `backend/app/gateway/routes/skills.py`:\n\n```python\nfrom fastapi import APIRouter\nfrom ..models import SkillListResponse\n\nrouter = APIRouter(prefix=\"/api\", tags=[\"Skills\"])\n\n@router.get(\"/skills\", response_model=SkillListResponse)\nasync def list_skills():\n    \"\"\"获取可用技能列表\"\"\"\n    skills = [\n        {\n            \"id\": \"web_search\",\n            \"name\": \"Web Search\",\n            \"description\": \"搜索互联网\",\n            \"enabled\": True,\n        },\n        {\n            \"id\": \"code_execution\",\n            \"name\": \"Code Execution\",\n            \"description\": \"执行代码\",\n            \"enabled\": True,\n        },\n    ]\n    return SkillListResponse(skills=skills, total=len(skills))\n```\n\n### 3.3 在主应用中注册路由\n\n编辑 `backend/app/gateway/main.py`:\n\n```python\nfrom .routes import threads, models, skills\n\n# 注册路由\napp.include_router(threads.router)\napp.include_router(models.router)\napp.include_router(skills.router)\n```\n\n---\n\n## 📊 Part 4: 中间件与错误处理（Day 11 下午）\n\n### 4.1 创建日志中间件\n\n创建 `backend/app/gateway/middleware.py`:\n\n```python\nfrom fastapi import Request, Response\nfrom starlette.middleware.base import BaseHTTPMiddleware\nimport logging\nimport time\n\nlogger = logging.getLogger(__name__)\n\nclass LoggingMiddleware(BaseHTTPMiddleware):\n    async def dispatch(self, request: Request, call_next) -> Response:\n        start_time = time.time()\n        \n        # 记录请求\n        logger.info(\n            f\"[{request.method}] {request.url.path} \"\n            f\"from {request.client.host}\"\n        )\n        \n        try:\n            response = await call_next(request)\n        except Exception as e:\n            logger.error(f\"请求处理错误: {e}\")\n            raise\n        \n        # 记录响应\n        duration = time.time() - start_time\n        logger.info(\n            f\"[{response.status_code}] {request.url.path} \"\n            f\"completed in {duration:.2f}s\"\n        )\n        \n        return response\n```\n\n在 main.py 中添加：\n\n```python\nfrom .middleware import LoggingMiddleware\n\napp.add_middleware(LoggingMiddleware)\n```\n\n### 4.2 全局异常处理\n\n编辑 `backend/app/gateway/main.py`：\n\n```python\nfrom fastapi.exceptions import RequestValidationError\nfrom fastapi.responses import JSONResponse\n\n@app.exception_handler(RequestValidationError)\nasync def validation_exception_handler(request, exc):\n    return JSONResponse(\n        status_code=422,\n        content={\"detail\": \"请求验证失败\", \"errors\": exc.errors()},\n    )\n\n@app.exception_handler(Exception)\nasync def general_exception_handler(request, exc):\n    logger.error(f\"未处理的异常: {exc}\")\n    return JSONResponse(\n        status_code=500,\n        content={\"detail\": \"服务器内部错误\"},\n    )\n```\n\n---\n\n## ✅ 实战检查清单\n\n- [ ] FastAPI 应用成功启动\n- [ ] /health 端点返回 200\n- [ ] 可创建线程（/threads POST）\n- [ ] 可获取模型列表（/models GET）\n- [ ] 可获取技能列表（/skills GET）\n- [ ] SSE 流式响应正确格式化\n- [ ] 错误处理有效\n- [ ] 日志输出清晰\n\n---\n\n## 📚 关键文档\n\n- [FastAPI 官方文档](https://fastapi.tiangolo.com/)\n- [Pydantic 文档](https://docs.pydantic.dev/)\n- [LangGraph 客户端文档](https://langchain-ai.github.io/langgraph/)\n\n---\n\n## ⏱️ 时间记录\n\n| 阶段 | 预计时间 | 实际时间 |\n|------|---------|----------|\n| Part 1: FastAPI 基础 (Day 10 AM) | 2 小时 | ___ |\n| Part 2: LangGraph 集成 (Day 10 PM) | 2 小时 | ___ |\n| Part 3: 更多路由 (Day 11 AM) | 1.5 小时 | ___ |\n| Part 4: 中间件处理 (Day 11 PM) | 1.5 小时 | ___ |\n| **总计** | **6-7 小时** | **___** |\n\n---\n\n**下一步**: 完成后，进入 Day 12 - LangGraph 代理系统\n"
