# 第12天：工具和子Agent系统

**学习日期**：Day 12  
**预计投入**：8小时  
**难度等级**：⭐⭐⭐⭐ (较难)

---

## 🎯 今日目标

实现工具注册系统和子Agent委托。

---

## 📋 任务清单

### 任务12.1：工具注册系统（2小时）

```python
# deerflow/tools/tools.py

from langchain.tools import tool
from typing import List

def create_tools(sandbox):
    """创建完整工具集"""
    
    tools = []
    
    # Sandbox工具
    @tool(name="read_file")
    def read_file(path: str) -> str:
        """读取文件"""
        return sandbox.read_file(path)
    
    @tool(name="write_file")
    def write_file(path: str, content: str) -> str:
        """写入文件"""
        sandbox.write_file(path, content)
        return "OK"
    
    @tool(name="str_replace")
    def str_replace(path: str, old_str: str, new_str: str) -> str:
        """替换文件内容"""
        content = sandbox.read_file(path)
        new_content = content.replace(old_str, new_str)
        sandbox.write_file(path, new_content)
        return "Replaced"
    
    tools.extend([read_file, write_file, str_replace])
    
    # 内置工具
    @tool(name="present_files")
    def present_files(path: str) -> str:
        """展示文件"""
        files = sandbox.list_dir(path)
        return "\n".join(files[:10])  # 显示前10个
    
    tools.append(present_files)
    
    return tools
```

### 任务12.2：内置工具（1.5小时）

```python
# deerflow/tools/builtins/present_files.py

from langchain.tools import tool

@tool(name="present_files")
def present_files(path: str) -> str:
    """优化的文件展示"""
    return "Files in " + path

# deerflow/tools/builtins/ask_clarification.py

@tool(name="ask_clarification")
def ask_clarification(question: str, options: list[str]) -> str:
    """请求用户澄清"""
    return f"Clarification needed: {question}"

# deerflow/tools/builtins/view_image.py

@tool(name="view_image")
def view_image(path: str) -> str:
    """加载图像"""
    return f"Loaded image: {path}"
```

### 任务12.3：子Agent执行器（2.5小时）

```python
# deerflow/subagents/executor.py

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

class SubagentExecutor:
    """子Agent执行器"""
    
    def __init__(self, config: Dict, thread_id: str):
        self.config = config
        self.thread_id = thread_id
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
    
    async def run_subagent(
        self,
        task_description: str,
        agent_type: str = "general-purpose",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """异步运行子Agent"""
        
        # 这里简单实现，真实版本会更复杂
        def execute_task():
            return {
                "status": "completed",
                "result": f"Executed: {task_description}",
                "artifacts": []
            }
        
        future = self.thread_pool.submit(execute_task)
        return future.result(timeout=15*60)
```

### 任务12.4：Registry和task工具（2小时）

```python
# deerflow/subagents/registry.py

class SubagentRegistry:
    """子Agent注册表"""
    
    _agents = {
        'general-purpose': None,  # 后续实现
        'bash': None,
    }
    
    @classmethod
    def get_agent(cls, agent_type: str):
        return cls._agents.get(agent_type)

# task工具
@tool(name="task")
def task(
    description: str,
    agent_type: str = "general-purpose",
    context: dict = None
) -> str:
    """委托子Agent执行任务"""
    # 异步执行，立即返回
    return f"Task queued: {description}"
```

---

## ✅ Day 12检验清单

**工具系统**：
- [ ] 工具注册机制 ✓ / ✗
- [ ] Sandbox工具集 ✓ / ✗
- [ ] 内置工具 ✓ / ✗

**子Agent**：
- [ ] SubagentExecutor ✓ / ✗
- [ ] Registry系统 ✓ / ✗
- [ ] task工具 ✓ / ✗

**测试**：
- [ ] 工具执行测试 ✓ / ✗
- [ ] 子Agent测试 ✓ / ✗

---

**Day 12 完成时间**：_____________  
**代码行数**：约 ___ 行

---

**文档版本**：1.0

