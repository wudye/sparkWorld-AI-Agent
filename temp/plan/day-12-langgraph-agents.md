# Day 12: LangGraph 代理系统

**日期**: Day 12 (第十二天)  
**目标**: 理解 Lead Agent 设计，实现代理核心流程  
**预计时间**: 5-6 小时  
**难度**: ⭐⭐⭐⭐ (困难)  
**前置**: 完成 Day 1-11  

---

## 📋 学习概念

### 1. LangGraph 图结构

**核心组件**:
- **State**: 图的数据容器（类型化）
- **Nodes**: 执行单元（函数或可调用对象）
- **Edges**: 节点连接（可条件化）
- **Compiled Graph**: 可执行的图实例

### 2. DeerFlow Lead Agent 角色

**职责**:
- 协调整个对话流程
- 决定何时调用 LLM
- 决定何时执行工具
- 管理状态转移
- 处理错误

### 3. 中间件链模式

**顺序**:
```
输入 → 前置中间件 → LLM 调用 → 工具执行 → 后置中间件 → 输出
```

---

## 🛠️ Part 1: 定义 Agent State（1.5 小时）

### 1.1 创建 State 类

创建 `backend/packages/harness/deerflow/agents/agent_state.py`:

```python
from typing import Annotated, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, MessageLike
from langgraph.graph.message import add_messages

class ThreadState(BaseModel):
    \"\"\"代理线程状态\"\"\"
    
    # 消息历史
    messages: Annotated[Sequence[BaseMessage], add_messages] = Field(
        default_factory=list,
        description=\"消息历史\",
    )
    
    # 工件（生成的代码、图表等）
    artifacts: dict = Field(
        default_factory=dict,
        description=\"生成的工件\",
    )
    
    # 元数据
    metadata: dict = Field(
        default_factory=dict,
        description=\"线程元数据\",
    )
    
    # 是否应该停止
    should_stop: bool = Field(
        default=False,
        description=\"是否应该停止执行\",
    )
```

### 1.2 创建类型定义

创建 `backend/packages/harness/deerflow/agents/types.py`:

```python
from typed_dict import TypedDict\nfrom typing import Literal\nfrom langgraph.graph import START, END\n\nclass NodeInput(TypedDict):\n    \"\"\"节点输入\"\"\"\n    state: \"ThreadState\"\n\nclass EdgeCondition:\n    \"\"\"边条件\"\"\"\n    def __call__(self, state: \"ThreadState\") -> Literal[\"continue\", \"end\"]:\n        return \"continue\" if not state.should_stop else \"end\"\n```\n\n---\n\n## 🎯 Part 2: 构建代理图（2 小时）\n\n### 2.1 创建节点函数\n\n创建 `backend/packages/harness/deerflow/agents/nodes.py`:\n\n```python\nfrom langchain_core.language_model import BaseLLM\nfrom langchain_core.messages import AIMessage, HumanMessage\nfrom .agent_state import ThreadState\nimport logging\n\nlogger = logging.getLogger(__name__)\n\ndef create_node_process_input(\n    model: BaseLLM,\n):\n    \"\"\"创建输入处理节点\"\"\"\n    async def process_input(state: ThreadState) -> ThreadState:\n        logger.info(f\"Processing input with {len(state.messages)} messages\")\n        # 可在此处理输入（如文本清理、预处理）\n        return state\n    return process_input\n\ndef create_node_llm_call(\n    model: BaseLLM,\n):\n    \"\"\"创建 LLM 调用节点\"\"\"\n    async def llm_call(state: ThreadState) -> dict:\n        logger.info(\"Calling LLM...\")\n        \n        # 调用模型\n        response = await model.ainvoke(state.messages)\n        \n        # 添加到消息历史\n        return {\"messages\": [response]}\n    \n    return llm_call\n\ndef create_node_tool_execution(\n    tools: list,\n):\n    \"\"\"创建工具执行节点\"\"\"\n    async def execute_tools(state: ThreadState) -> dict:\n        logger.info(\"Executing tools...\")\n        last_message = state.messages[-1]\n        \n        # 如果最后一条消息包含工具调用\n        if hasattr(last_message, \"tool_calls\"):\n            for tool_call in last_message.tool_calls:\n                tool_name = tool_call[\"name\"]\n                tool_input = tool_call[\"args\"]\n                \n                # 查找并执行工具\n                for tool in tools:\n                    if tool.name == tool_name:\n                        result = await tool.ainvoke(tool_input)\n                        logger.info(f\"Tool {tool_name} returned: {result[:100]}...\")\n                        break\n        \n        return {}\n    \n    return execute_tools\n\ndef create_node_should_continue(\n    model: BaseLLM,\n):\n    \"\"\"创建继续判断节点\"\"\"\n    def should_continue(state: ThreadState) -> str:\n        logger.info(\"Checking if should continue...\")\n        \n        last_message = state.messages[-1]\n        \n        # 如果 LLM 要求调用工具\n        if hasattr(last_message, \"tool_calls\") and last_message.tool_calls:\n            return \"tools\"\n        else:\n            return \"end\"\n    \n    return should_continue\n```\n\n### 2.2 创建完整的 Lead Agent\n\n创建 `backend/packages/harness/deerflow/agents/lead_agent.py`:\n\n```python\nfrom langgraph.graph import StateGraph, START, END\nfrom langchain_core.language_model import BaseLLM\nfrom .agent_state import ThreadState\nfrom .nodes import (\n    create_node_process_input,\n    create_node_llm_call,\n    create_node_tool_execution,\n    create_node_should_continue,\n)\nimport logging\n\nlogger = logging.getLogger(__name__)\n\ndef make_lead_agent(\n    model: BaseLLM,\n    tools: list = None,\n):\n    \"\"\"构建 Lead Agent\"\"\"\n    \n    if tools is None:\n        tools = []\n    \n    # 创建图\n    graph = StateGraph(ThreadState)\n    \n    # 添加节点\n    graph.add_node(\n        \"process_input\",\n        create_node_process_input(model),\n    )\n    graph.add_node(\n        \"llm_call\",\n        create_node_llm_call(model),\n    )\n    graph.add_node(\n        \"tool_execution\",\n        create_node_tool_execution(tools),\n    )\n    \n    # 添加边\n    graph.add_edge(START, \"process_input\")\n    graph.add_edge(\"process_input\", \"llm_call\")\n    \n    # 添加条件边\n    graph.add_conditional_edges(\n        \"llm_call\",\n        create_node_should_continue(model),\n        {\n            \"tools\": \"tool_execution\",\n            \"end\": END,\n        },\n    )\n    \n    graph.add_edge(\"tool_execution\", \"llm_call\")\n    \n    # 编译图\n    return graph.compile()\n```\n\n---\n\n## 🔄 Part 3: 中间件链（1.5 小时）\n\n### 3.1 创建中间件基类\n\n创建 `backend/packages/harness/deerflow/agents/middleware.py`:\n\n```python\nfrom abc import ABC, abstractmethod\nfrom .agent_state import ThreadState\nimport logging\n\nlogger = logging.getLogger(__name__)\n\nclass Middleware(ABC):\n    \"\"\"中间件基类\"\"\"\n    \n    @abstractmethod\n    async def before(self, state: ThreadState) -> ThreadState:\n        \"\"\"在 LLM 调用前执行\"\"\"\n        return state\n    \n    @abstractmethod\n    async def after(self, state: ThreadState) -> ThreadState:\n        \"\"\"在 LLM 调用后执行\"\"\"\n        return state\n\nclass LoggingMiddleware(Middleware):\n    \"\"\"日志中间件\"\"\"\n    \n    async def before(self, state: ThreadState) -> ThreadState:\n        logger.info(f\"Before: {len(state.messages)} messages\")\n        return state\n    \n    async def after(self, state: ThreadState) -> ThreadState:\n        logger.info(f\"After: {len(state.messages)} messages\")\n        return state\n\nclass ErrorHandlingMiddleware(Middleware):\n    \"\"\"错误处理中间件\"\"\"\n    \n    async def before(self, state: ThreadState) -> ThreadState:\n        return state\n    \n    async def after(self, state: ThreadState) -> ThreadState:\n        # 检查是否有错误消息\n        for message in state.messages:\n            if hasattr(message, \"content\") and \"error\" in message.content.lower():\n                logger.warning(f\"Error detected: {message.content}\")\n        return state\n\nclass MiddlewareChain:\n    \"\"\"中间件链\"\"\"\n    \n    def __init__(self, middlewares: list[Middleware] = None):\n        self.middlewares = middlewares or []\n    \n    async def execute_before(self, state: ThreadState) -> ThreadState:\n        \"\"\"执行所有 before 中间件\"\"\"\n        for middleware in self.middlewares:\n            state = await middleware.before(state)\n        return state\n    \n    async def execute_after(self, state: ThreadState) -> ThreadState:\n        \"\"\"执行所有 after 中间件\"\"\"\n        for middleware in reversed(self.middlewares):\n            state = await middleware.after(state)\n        return state\n```\n\n---\n\n## 🧪 Part 4: 测试与集成（1.5 小时）\n\n### 4.1 创建测试\n\n创建 `backend/tests/test_lead_agent.py`:\n\n```python\nimport pytest\nfrom unittest.mock import AsyncMock, MagicMock\nfrom deerflow.agents.agent_state import ThreadState\nfrom deerflow.agents.lead_agent import make_lead_agent\nfrom langchain_core.messages import HumanMessage, AIMessage\n\n@pytest.mark.asyncio\nasync def test_lead_agent_creation():\n    \"\"\"测试 Lead Agent 创建\"\"\"\n    mock_model = AsyncMock()\n    mock_model.ainvoke = AsyncMock(return_value=AIMessage(content=\"Hello!\"))\n    \n    agent = make_lead_agent(mock_model)\n    assert agent is not None\n\n@pytest.mark.asyncio\nasync def test_agent_execution():\n    \"\"\"测试代理执行\"\"\"\n    mock_model = AsyncMock()\n    mock_model.ainvoke = AsyncMock(return_value=AIMessage(content=\"Response\"))\n    \n    agent = make_lead_agent(mock_model)\n    \n    initial_state = ThreadState(\n        messages=[HumanMessage(content=\"Hello\")],\n    )\n    \n    result = await agent.ainvoke(initial_state)\n    assert len(result.messages) > 1\n    assert result.messages[-1].content == \"Response\"\n\n@pytest.mark.asyncio\nasync def test_middleware_chain():\n    \"\"\"测试中间件链\"\"\"\n    from deerflow.agents.middleware import (\n        MiddlewareChain,\n        LoggingMiddleware,\n    )\n    \n    chain = MiddlewareChain([LoggingMiddleware()])\n    state = ThreadState(messages=[])\n    \n    state = await chain.execute_before(state)\n    state = await chain.execute_after(state)\n    \n    assert state is not None\n```\n\n### 4.2 运行测试\n\n```powershell\ncd backend\nuv run pytest tests/test_lead_agent.py -v\n```\n\n---\n\n## ✅ 实战检查清单\n\n- [ ] ThreadState 模型完能正常使用\n- [ ] 所有节点函数创建成功\n- [ ] 图能正确编译\n- [ ] 条件边逻辑正确\n- [ ] 中间件链能正确执行\n- [ ] 所有测试通过\n- [ ] 能处理多轮对话\n- [ ] 错误情况能正确处理\n\n---\n\n## ⏱️ 时间记录\n\n| 阶段 | 预计时间 | 实际时间 |\n|------|---------|----------|\n| Part 1: State 定义 | 1.5 小时 | ___ |\n| Part 2: 构建图 | 2 小时 | ___ |\n| Part 3: 中间件链 | 1.5 小时 | ___ |\n| Part 4: 测试集成 | 1.5 小时 | ___ |\n| **总计** | **5-6 小时** | **___** |\n\n---\n\n**下一步**: 完成后，进入 Day 13 - 高级特性（技能库、MCP、沙箱）\n"
