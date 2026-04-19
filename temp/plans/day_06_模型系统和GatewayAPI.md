# 第6天：模型系统和Gateway API

**学习日期**：Day 6  
**预计投入**：5小时  
**难度等级**：⭐⭐⭐ (中等)

---

## 📚 学习目标

理解模型工厂、多模型支持、以及REST API网关。

**关键成果**：
- ✅ 理解模型工厂和动态选择
- ✅ 理解模型能力声明机制
- ✅ 理解思考模式和视觉模型集成
- ✅ 理解Gateway API整体设计
- ✅ 理解线程清理的分离职责

---

## 📋 任务清单

### 任务6.1：模型工厂和动态选择（1.5小时）

**模型配置**：
```yaml
models:
  - name: "claude-opus"
    provider: "anthropic"
    api_key: "${ANTHROPIC_API_KEY}"
    capabilities:
      - thinking
      - vision
    token_limit: 200000
  
  - name: "gpt-4"
    provider: "openai"
    api_key: "${OPENAI_API_KEY}"
    capabilities:
      - vision
    token_limit: 128000
```

**模型工厂**：
```python
class ModelFactory:
    @staticmethod
    def create_model(config: ModelConfig):
        if config.provider == 'anthropic':
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=config.name,
                api_key=config.api_key,
                temperature=config.temperature
            )
        elif config.provider == 'openai':
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=config.name,
                api_key=config.api_key,
                temperature=config.temperature
            )
```

**模型能力声明**：
```python
class ModelCapabilities:
    vision: bool         # 支持图像输入
    thinking: bool       # 支持思考模式
    tool_use: bool       # 支持工具调用
    max_tokens: int
    input_token_limit: int
```

**模型选择策略**：
```python
def select_model(
    task_type: str,
    user_preference: str = None,
    context_length: int = None
) -> ChatModel:
    """选择最合适的模型"""
    
    if user_preference:
        return get_model(user_preference)
    
    if task_type == 'vision_analysis':
        return get_model_with_vision()
    
    if context_length and context_length > 100000:
        return get_model_with_large_context()
    
    return get_default_model()
```

**思考模式集成**：
```python
if model.capabilities.thinking:
    system_prompt += """
你有能力进行深入思考。在处理复杂问题时：
1. 先内部思考（不需要呈现给用户）
2. 分析问题的各个方面
3. 得出结论后再回复
"""
```

**视觉模型支持**：
```python
if model.capabilities.vision:
    message = HumanMessage(
        content=[
            {"type": "text", "text": "分析这个图像"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_data}"}
            }
        ]
    )
```

**检验方式**：
- [ ] 如何添加一个新的模型提供商？
- [ ] 思考模式和普通模式的差异？
- [ ] 如何根据任务自动选择模型？

---

### 任务6.2：Gateway API设计（1.5小时）

**FastAPI应用结构**：
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    load_config()
    initialize_db()
    yield
    # 关闭事件
    cleanup()

app = FastAPI(lifespan=lifespan)

# 包含路由
app.include_router(models.router)
app.include_router(mcp.router)
app.include_router(skills.router)
app.include_router(uploads.router)
app.include_router(threads.router)
app.include_router(artifacts.router)
```

**路由模块**：

**models.py - /api/models**
```python
@router.get("/models")
async def list_models() -> list[ModelInfo]:
    """列表所有可用模型"""
    ...

@router.get("/models/{name}")
async def get_model(name: str) -> ModelInfo:
    """获取模型详情"""
    ...

@router.post("/models/{name}/test")
async def test_model(name: str, prompt: str) -> TestResult:
    """测试模型连接"""
    ...
```

**uploads.py - /api/threads/{id}/uploads**
```python
@router.post("/threads/{thread_id}/uploads")
async def upload_file(thread_id: str, file: UploadFile):
    """上传文件"""
    # 1. 验证thread_id
    # 2. 保存到 thread/{thread_id}/uploads/
    # 3. 返回虚拟路径
```

**threads.py - /api/threads/{id}**
```python
@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """删除线程
    
    分离职责：
    - LangGraph: DELETE /api/langgraph/threads/{id}
    - Gateway: DELETE /api/threads/{id}
    """
    # 1. 调用LangGraph删除
    # 2. 删除本地文件
```

**artifacts.py - /api/threads/{id}/artifacts**
```python
@router.get("/threads/{thread_id}/artifacts")
async def list_artifacts(thread_id: str) -> list:
    """列表生成的工件"""
    ...

@router.get("/threads/{thread_id}/artifacts/{name}")
async def download_artifact(thread_id: str, name: str):
    """下载工件"""
    ...
```

**线程清理流程**：
```
前端: DELETE /api/langgraph/threads/{id}
    └→ LangGraph处理，删除消息历史

前端: DELETE /api/threads/{id}
    └→ Gateway处理：
        1. rm -rf thread/{id}/workspace/
        2. rm -rf thread/{id}/uploads/
        3. rm -rf thread/{id}/outputs/
```

**代码练习**：创建一个新的路由模块
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/custom", tags=["custom"])

class CustomRequest(BaseModel):
    data: str

@router.post("/process")
async def process_data(req: CustomRequest):
    result = some_processing(req.data)
    return {"result": result}

# 在app.py中包含
app.include_router(custom.router)
```

**检验方式**：
- [ ] Gateway API和LangGraph Server的职责边界？
- [ ] 为什么上传/删除要用虚拟路径？
- [ ] 如何新增一个API路由？

---

## ✅ 第6天检验清单

**理论题**：
- [ ] 如何添加一个新的模型提供商？
- [ ] 思考模式如何在系统提示词中启用？
- [ ] 视觉模型如何加载图像？
- [ ] Gateway和LangGraph的职责边界？

**实践题**：
- [ ] 理解模型选择策略 ✓ / ✗
- [ ] 理解FastAPI架构 ✓ / ✗
- [ ] 能设计新的API路由 ✓ / ✗
- [ ] 理解线程清理流程 ✓ / ✗

---

## 🎓 Day 6总结

**模型系统的灵活性**：
_____________________________________________

**Gateway的职责清晰性**：
_____________________________________________

**设计亮点**：
_____________________________________________

---

**Day 6 完成时间**：_____________  
**理解程度评分** (1-10)：_____

---

**文档版本**：1.0  
**最后更新**：2025-04-19

