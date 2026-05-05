The user wants a comprehensive guide on how Swagger works in FastAPI. Let me provide detailed information covering all aspects.
The user wants a comprehensive guide on Swagger in FastAPI. Let me provide a thorough explanation covering how Swagger works in FastAPI, all the configuration options, and practical use cases.
好的，我来详细讲解 FastAPI 中 Swagger 的完整用法。

## FastAPI Swagger 全景图

```
main.py
  │
  ├─ FastAPI() 参数配置
  │    ├─ title, description, version → OpenAPI 元信息
  │    ├─ openapi_tags              → 接口分组
  │    ├─ swagger_ui_parameters      → 自定义 UI 行为
  │    ├─ servers                   → 多环境 URL
  │    ├─ docs_url / redoc_url      → 文档路由
  │    └─ lifespan                  → 生命周期
  │
  ├─ @app.get() 等装饰器
  │    ├─ tags = [...]              → 归属分组
  │    ├─ summary / description     → 接口说明
  │    ├─ response_model            → 响应 schema
  │    ├─ status_code               → 状态码
  │    ├─ deprecated                → 标记废弃
  │    └─ include_in_schema=False   → 隐藏接口
  │
  └─ Pydantic models
       ├─ 请求体自动生成 Schema
       └─ 响应体自动生成 Schema
```

## 一、FastAPI() 的完整配置

```python
from fastapi import FastAPI
from fastapi.security import APIKeyHeader, HTTPBearer

api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)
jwt_scheme = HTTPBearer(auto_error=False)

app = FastAPI(
    # ====== 基本信息 ======
    title="SparkWorld AI Agent",            # API 标题
    description="""                         # 详细描述（支持 Markdown）
    # SparkWorld AI Agent
    
    ## 功能
    - AI 模型管理
    - 对话系统
    - Agent 编排
    
    ## 认证
    使用 `X-API-Key` Header 或 Bearer Token
    """,
    summary="AI Agent 的统一服务入口",       # 简短摘要（OpenAPI 3.1+）
    version="0.1.0",                        # 版本号
    terms_of_service="http://example.com/tos",  # 服务条款 URL
    contact={                               # 联系方式
        "name": "开发者",
        "url": "http://example.com",
        "email": "dev@example.com",
    },
    license_info={                          # 许可证
        "name": "MIT",
        "url": "https://mit-license.org",
    },
    
    # ====== 文档路由 ======
    docs_url="/docs",                       # Swagger UI 路径（默认 /docs）
    redoc_url="/redoc",                     # ReDoc 路径（默认 /redoc）
    openapi_url="/openapi.json",            # OpenAPI JSON 路径
    
    # ====== 多环境 URL ======
    servers=[
        {"url": "http://localhost:8000", "description": "开发环境"},
        {"url": "https://api.example.com", "description": "生产环境"},
    ],
    
    # ====== 接口分组 ======
    openapi_tags=[
        {
            "name": "public",
            "description": "公开接口，无需认证",
        },
        {
            "name": "agents",
            "description": "Agent 管理",
            "externalDocs": {               # 外部文档链接
                "description": "Agent 详细文档",
                "url": "http://docs.example.com/agents",
            },
        },
        {
            "name": "models",
            "description": "AI 模型管理",
        },
    ],
    
    # ====== Swagger UI 配置 ======
    swagger_ui_parameters={
        "persistAuthorization": True,       # 刷新保留 Token
        "defaultModelsExpandDepth": -1,     # 折叠 Schemas
        "displayRequestDuration": True,     # 显示请求耗时
        "tryItOutEnabled": True,            # 默认展开 Try it out
        "filter": True,                     # 显示搜索框
        "syntaxHighlight.theme": "monokai",  # 代码高亮主题
        "docExpansion": "list",             # 默认展开方式
    },
    
    # ====== 生命周期 ======
    lifespan=lifespan,
)
```

## 二、接口装饰器的 OpenAPI 参数

```python
from pydantic import BaseModel

# ====== 请求/响应模型 ======
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4"
    temperature: float = 0.7
    
    model_config = {
        "json_schema_extra": {
            "example": {                    # 示例数据
                "message": "你好",
                "model": "gpt-4",
                "temperature": 0.7
            }
        }
    }

class ChatResponse(BaseModel):
    reply: str
    usage: dict

# ====== 接口定义 ======
@app.post(
    "/chat",
    tags=["chat"],                         # 归属分组
    summary="发送对话消息",                  # 简短标题
    description="""                         # 接口详细说明
    向 AI Agent 发送一条消息并获取回复。

    ## 参数说明
    - **message**: 用户输入的消息
    - **model**: 使用的 AI 模型
    - **temperature**: 生成温度 0-1

    ## 注意事项
    - 需要认证
    - 消息长度不超过 4096 字符
    """,
    response_description="AI 回复结果",      # 响应说明
    response_model=ChatResponse,           # 响应模型
    status_code=200,                        # 响应状态码
    deprecated=False,                       # 是否废弃
    include_in_schema=True,                 # 是否显示在文档中
    operation_id="chat_send",              # 唯一操作 ID
)
async def chat(
    request: ChatRequest,
    api_key: str = Security(api_key_scheme),
):
    """这是 docstring，也会显示在 Swagger 中"""
    return {"reply": f"你说了: {request.message}", "usage": {"tokens": 10}}
```

## 三、Swagger UI 页面结构

```
http://localhost:8000/docs
┌──────────────────────────────────────────────┐
│  🔍 [搜索框]     [Authorize ▼]  [选择环境 ▼] │
│                                              │
│  ▼ public                                    │
│    ├─ GET /      欢迎页面                     │
│    └─ GET /health  健康检查                   │
│                                              │
│  ▼ agents                                    │
│    ├─ GET /agents        🔒 获取 Agent 列表  │
│    ├─ POST /agents       🔒 创建 Agent       │
│    └─ DELETE /agents/id  🔒 删除 Agent       │
│                                              │
│  ▼ Schemas (折叠)                            │
│    ├─ ChatRequest                            │
│    └─ ChatResponse                           │
└──────────────────────────────────────────────┘
```

## 四、认证在 Swagger 中的显示

当你在接口中使用 `Security()` 时，Swagger UI 会自动：

```
1. 在接口旁边显示 🔒 图标
2. 在页面顶部显示 "Authorize" 按钮
3. 点击 Authorize 后弹出对话框：
   ┌────────────────────────┐
   │ Available authorizations │
   │                         │
   │ X-API-Key: [________]   │
   │ Bearer Token: [______] │
   │                         │
   │  [Authorize]  [Close]  │
   └────────────────────────┘
4. 填入 Token 后，点击 Try it out → Execute
   → 请求会自动带上 Authorization 头
```

## 五、高级用法

### 5.1 条件隐藏接口

```python
@app.get("/internal/status", include_in_schema=False)  # 不在文档显示
async def internal_status():
    pass

# 或根据环境变量控制
import os
SHOW_DOCS = os.getenv("ENV") != "production"

app = FastAPI(
    docs_url="/docs" if SHOW_DOCS else None,   # 生产环境关闭文档
)
```

### 5.2 自定义 OpenAPI 扩展

```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="SparkWorld AI Agent",
        version="0.1.0",
        description="自定义配置",
        routes=app.routes,
    )
    
    # 添加自定义字段
    openapi_schema["x-custom-field"] = "value"
    openapi_schema["x-logo"] = {
        "url": "https://example.com/logo.png",
        "backgroundColor": "#FFFFFF"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 5.3 自带异常响应文档

```python
from fastapi import HTTPException, status

@app.get("/agents/{id}", responses={
    200: {"description": "成功获取"},
    404: {"description": "Agent 不存在", "content": {
        "application/json": {
            "example": {"detail": "Agent not found"}
        }
    }},
    500: {"description": "服务器错误"},
})
async def get_agent(id: str):
    if id == "bad":
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"id": id}
```

## 六、FastAPI 自动生成的内容

| 你写的代码 | Swagger 自动生成 |
|-----------|----------------|
| `def root():` 的 docstring | 接口描述 |
| 函数参数名 + 类型注解 | 请求参数 |
| Pydantic `BaseModel` | 请求/响应 Schema |
| `response_model` | 响应格式 |
| `Security()` | 认证方式 |
| `status_code` | 响应状态码 |
| `tags` | 接口分组 |
| `summary` / `description` | 接口说明 |

## 总结

FastAPI 的 Swagger 完全是**自动化的**——你只需要写好类型注解和 Pydantic 模型，FastAPI 就会自动生成高质量的 API 文档，零额外工作量。