# 第8天：基础框架搭建

**学习日期**：Day 8  
**预计投入**：6小时  
**难度等级**：⭐⭐⭐⭐ (较难)

---

## 🎯 今日目标

建立项目基本结构，创建最小可运行的Agent框架。

---

## 📋 任务清单

### 任务8.1：项目初始化（1小时）

```bash
# 1. 创建新项目目录
mkdir deer-flow-rewrite
cd deer-flow-rewrite

# 2. 初始化Python项目结构
cat > pyproject.toml << 'EOF'
[project]
name = "deer-flow-rewrite"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "langgraph>=0.2.0",
    "langchain>=0.1.0",
    "langchain-anthropic",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.0.0",
]
EOF

# 3. 设置虚拟环境
python -m venv venv
source venv/bin/activate  # on macOS/Linux
# or: venv\Scripts\activate  # on Windows

# 4. 安装依赖
pip install -e ".[dev]"
```

---

### 任务8.2：文件夹结构（0.5小时）

```bash
deerflow/
├── agents/
│   ├── lead_agent/
│   │   ├── agent.py
│   │   └── __init__.py
│   ├── middlewares/
│   │   ├── base.py
│   │   ├── thread_data.py
│   │   └── __init__.py
│   ├── thread_state.py
│   └── __init__.py
├── sandbox/
│   ├── sandbox.py
│   ├── local/
│   │   ├── local_sandbox.py
│   │   └── __init__.py
│   ├── tools.py
│   └── __init__.py
├── tools/
│   ├── builtins/
│   │   ├── present_files.py
│   │   └── __init__.py
│   ├── tools.py
│   └── __init__.py
├── subagents/
│   ├── executor.py
│   ├── registry.py
│   └── __init__.py
├── models/
│   ├── factory.py
│   └── __init__.py
├── config/
│   ├── app_config.py
│   └── __init__.py
└── __init__.py

app/
├── gateway/
│   ├── app.py
│   ├── routers/
│   │   ├── models.py
│   │   └── __init__.py
│   └── __init__.py
└── __init__.py

tests/
├── conftest.py
├── test_thread_state.py
└── __init__.py
```

---

### 任务8.3：ThreadState定义（1.5小时）

```python
# deerflow/agents/thread_state.py

from typing import TypedDict, Optional
from langchain_core.messages import BaseMessage

class ThreadState(TypedDict):
    """DeerFlow Thread State"""
    
    # 标准LangGraph字段
    messages: list[BaseMessage]
    
    # DeerFlow扩展字段
    sandbox: dict  # {provider, id, config}
    thread_data: dict  # {workspace_dir, uploads_dir, outputs_dir}
    artifacts: list[str]  # 生成的文件路径
    title: Optional[str]  # 对话标题
    todos: list[dict]  # 任务列表
    viewed_images: dict  # {path: base64}
```

**测试ThreadState**：
```python
# tests/test_thread_state.py

from deerflow.agents.thread_state import ThreadState

def test_thread_state_creation():
    state = ThreadState(
        messages=[],
        sandbox={},
        thread_data={},
        artifacts=[],
        title=None,
        todos=[],
        viewed_images={}
    )
    assert len(state['messages']) == 0
    assert state['title'] is None
```

---

### 任务8.4：最小Agent（2小时）

```python
# deerflow/agents/lead_agent/agent.py

from langgraph.graph import StateGraph, START, END
from deerflow.agents.thread_state import ThreadState

def make_lead_agent(config):
    """创建主Agent"""
    
    # 1. 定义节点
    def agent_node(state: ThreadState) -> ThreadState:
        """Agent执行节点"""
        # 简单实现：打印消息并返回
        print(f"Agent received {len(state['messages'])} messages")
        return state
    
    # 2. 创建StateGraph
    graph = StateGraph(ThreadState)
    
    # 3. 添加节点
    graph.add_node("agent", agent_node)
    
    # 4. 添加边
    graph.add_edge(START, "agent")
    graph.add_edge("agent", END)
    
    # 5. 编译
    return graph.compile()

# deerflow/agents/__init__.py
from deerflow.agents.lead_agent.agent import make_lead_agent

__all__ = ["make_lead_agent"]
```

**测试Agent**：
```python
# tests/test_agent.py

from deerflow.agents import make_lead_agent
from langchain_core.messages import HumanMessage

def test_minimal_agent():
    config = {}  # 简单配置
    agent = make_lead_agent(config)
    
    input_state = {
        "messages": [HumanMessage(content="Hello")],
        "sandbox": {},
        "thread_data": {},
        "artifacts": [],
        "title": None,
        "todos": [],
        "viewed_images": {}
    }
    
    result = agent.invoke(input_state)
    assert result is not None
```

---

## ✅ Day 8检验清单

**完成项目初始化**：
- [ ] 创建了项目目录结构
- [ ] 安装了核心依赖
- [ ] 配置了虚拟环境

**实现ThreadState**：
- [ ] 定义了ThreadState
- [ ] 编写了单元测试
- [ ] 测试通过

**实现最小Agent**：
- [ ] 创建了StateGraph
- [ ] 定义了agent_node
- [ ] 能成功调用agent.invoke()

**检验方式**：
```bash
# 运行测试
pytest tests/test_thread_state.py -v
pytest tests/test_agent.py -v

# 手动测试
python -c "from deerflow.agents import make_lead_agent; print('Success!')"
```

---

## 🎓 Day 8总结

**完成了什么**：
- ✅ 项目框架搭建完成
- ✅ ThreadState设计完成
- ✅ 最小Agent运行成功

**下一步**（Day 9-10）：
- 实现9个中间件
- 集成中间件链到Agent
- 实现完整的Agent执行流程

---

**Day 8 完成时间**：_____________  
**代码行数**：约 ___ 行  
**测试覆盖率**：___ %  

---

**文档版本**：1.0  
**最后更新**：2025-04-19

