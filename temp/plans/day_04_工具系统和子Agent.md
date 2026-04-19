# 第4天：工具系统和子Agent

**学习日期**：Day 4  
**预计投入**：5.5小时  
**难度等级**：⭐⭐⭐ (中等)

---

## 📚 学习目标

理解工具多态、注册机制、以及子Agent委托系统。

**关键成果**：
- ✅ 理解工具系统架构
- ✅ 掌握3个内置工具的用途
- ✅ 理解子Agent并发执行模型
- ✅ 理解MCP集成机制
- ✅ 能设计新的工具和子Agent

---

## 📋 任务清单

### 任务4.1：理解工具系统架构（1小时）

**工具分类**：
```
Sandbox工具 (5个)
├─ bash, ls, read_file, write_file, str_replace

子Agent工具 (1个)
├─ task

内置工具 (3个)
├─ present_files, ask_clarification, view_image

MCP工具 (动态)
├─ 从extensions_config.json加载

社区工具 (可选)
├─ tavily, jina_ai, firecrawl等
```

**工具的生命周期**：
```
1. 定义工具 (@tool装饰器)
   ↓
2. 注册到Agent (加入tools列表)
   ↓
3. 系统提示词中声明 (工具清单)
   ↓
4. LLM选择调用
   ↓
5. 执行工具函数
   ↓
6. 结果返回给LLM
```

**工具定义格式**：
```python
@tool(name="tool_name")
def my_tool(param1: str, param2: int) -> str:
    """工具描述 (会注入提示词)"""
    return result
```

**LangChain自动生成**：
- 工具名
- 参数JSON Schema
- 描述

**检验方式**：
- [ ] 工具定义和工具执行有什么区别？
- [ ] LLM如何知道有哪些工具可用？

---

### 任务4.2：内置工具分析（1.5小时）

**1️⃣ present_files工具**

```python
@tool(name="present_files")
def present_files(path: str) -> str:
    """优化的文件展示"""
    # - 根据文件大小和类型智能格式化
    # - 代码文件显示语法高亮信息
    # - 太大的目录截断显示
```

**为什么需要**：
```
原因1：LLM理解格式化输出更好
原因2：_________________________________
原因3：_________________________________
```

**2️⃣ ask_clarification工具**

```python
@tool(name="ask_clarification")
def ask_clarification(
    question: str,
    options: list[str]
) -> str:
    """请求用户澄清"""
    # 当Agent不确定时调用
    # 中断当前执行
    # 等待用户反馈
```

**实现机制**：
```
1. Agent调用ask_clarification()
   ↓
2. ClarificationMiddleware拦截此工具
   ↓
3. 返回特殊响应给前端
   ↓
4. 前端显示选项对话框
   ↓
5. 用户选择后恢复执行
```

**为什么是工具而不是直接返回**：
```
答：LLM决定何时需要澄清，Agent有主动权
_____________________________________________
```

**3️⃣ view_image工具**

```python
@tool(name="view_image")
def view_image(path: str) -> str:
    """加载图像供视觉模型分析"""
    # - 读取图像文件，转base64
    # - 传递给ViewImageMiddleware
    # - 中间件负责注入到消息
```

**为什么需要这个工具**：
```
原因1：_________________________________
原因2：_________________________________
原因3：_________________________________
```

**代码练习**：
```python
# 创建一个自定义内置工具
from langchain.tools import tool

@tool(name="get_system_time")
def get_system_time() -> str:
    """获取当前系统时间"""
    from datetime import datetime
    return datetime.now().isoformat()

# 该工具如何加入Agent？
答：_____________________________________________
```

---

### 任务4.3：子Agent系统（1.5小时）

**子Agent vs 主Agent**：

| 特性 | 主Agent | 子Agent |
|------|--------|--------|
| 实例数 | 1 | 临时创建 |
| 工具集 | 完整 | 受限 |
| 并发数 | 1 | ×3 |
| 超时 | 无限 | 15min |
| 执行方式 | 同步 | 异步线程 |

**内置子Agent**：

**1️⃣ general-purpose**
```
工具集: Sandbox + MCP + 社区 + 内置
用途: 通用任务
例: 分析数据、编写代码、搜索信息
```

**2️⃣ bash**
```
工具集: 仅bash
用途: Shell命令专家
例: 批量文件操作、系统管理
仅当bash enabled时可用
```

**SubagentExecutor架构**：
```python
class SubagentExecutor:
    def __init__(self, config, thread_id):
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
    
    async def run_subagent(
        self,
        task_description: str,
        agent_type: str = 'general-purpose',
        context: dict = None
    ) -> dict:
        # 异步运行子Agent
        # 返回 {status, result, artifacts}
```

**执行流程**：
```
主Agent: task(description, agent_type)
    ↓
执行器: run_subagent()
    ↓
创建子Agent实例
    ↓
运行在线程池
    ↓
SSE事件: subagent_started
    ↓
子Agent执行 (工具调用、可能多步)
    ↓
完成或超时
    ↓
SSE事件: subagent_completed
    ↓
返回结果给主Agent
```

**Registry注册系统**：
```python
class SubagentRegistry:
    _agents = {
        'general-purpose': make_general_purpose_agent,
        'bash': make_bash_agent,
    }
    
    @classmethod
    def get_agent(cls, agent_type: str):
        return cls._agents.get(agent_type)
```

**设计好处**：
```
好处1：_________________________________
好处2：_________________________________
```

**task()工具**：
```python
@tool(name="task")
def task(
    description: str,
    agent_type: str = "general-purpose",
    context: dict = None
) -> str:
    """委托子Agent执行任务"""
    # 这是异步的！返回之前不等待完成
    # 使用SSE通知前端进度
    # 主Agent继续执行
```

**代码练习**：
```python
# 理解子Agent的并发执行

# 主Agent代码逻辑：
# 1. task(description="分析sales.csv", agent_type="general-purpose")
# 2. task(description="分析revenue.csv", agent_type="general-purpose")
# 3. task(description="合并数据", agent_type="general-purpose")

# 执行器创建3个子Agent，同时运行（最多3个）
# 前端通过SSE看到：
# - subagent_1 started
# - subagent_2 started
# - subagent_3 started
# - subagent_1 completed (results: ...)
# ...
```

**检验方式**：
- [ ] 子Agent为什么需要异步？
- [ ] 如何限制最多3个并发？
- [ ] 子Agent超时了怎么办？
- [ ] 如何添加一个新的子Agent类型（e.g., "sql"）？

---

### 任务4.4：MCP工具集成（1小时）

**MCP概念**：
```
MCP = Model Context Protocol
= Claude工具市场协议

好处：
- 标准化工具定义
- 第三方工具生态
- Agent无需修改即可扩展
```

**例如MCP服务器**：
```
mcp-server-git      → Git操作
mcp-server-sqlite   → 数据库查询
mcp-server-slack    → Slack操作
```

**MCP客户端实现**：
```python
class MCPClient:
    def __init__(self, server_config):
        self.process = subprocess.Popen(
            server_config['command'],
            stdin=PIPE, stdout=PIPE
        )
        self.rpc = JSONRPCClient(self.process)
    
    def list_tools(self) -> list:
        return self.rpc.call('tools/list')
    
    def call_tool(self, tool_name: str, args: dict) -> str:
        return self.rpc.call('tools/call', {
            'name': tool_name,
            'arguments': args
        })
```

**工具转换**：
```python
# MCP服务器定义 → Agent工具

@tool(name="git_clone")
def git_clone(url: str, path: str) -> str:
    """Clone a git repository"""
    mcp_client = get_mcp_client()
    return mcp_client.call_tool("git_clone", {
        "url": url, "path": path
    })
```

**工具缓存**：
```python
class MCPCache:
    _clients: dict[str, MCPClient] = {}
    
    @classmethod
    def get_client(cls, server_name: str) -> MCPClient:
        if server_name not in cls._clients:
            config = load_config(server_name)
            cls._clients[server_name] = MCPClient(config)
        return cls._clients[server_name]
```

**extensions_config.json格式**：
```json
{
  "mcpServers": {
    "git": {
      "command": "mcp-server-git",
      "args": ["--debug"],
      "env": {"GIT_AUTHOR": "Agent"}
    }
  }
}
```

**检验方式**：
- [ ] MCP解决什么问题？
- [ ] 如何集成一个新的MCP服务器？
- [ ] MCP服务器崩溃了怎么办？

---

## ✅ 第4天检验清单

**理论题**：
- [ ] 为什么view_image是一个工具而不是自动处理？
- [ ] 子Agent最多同时运行几个？为什么是这个数字？
- [ ] task()工具是同步还是异步的？为什么？
- [ ] 如何添加一个新的MCP服务器？

**实践题**：
- [ ] 能说出3个内置工具的用途 ✓ / ✗
- [ ] 能解释子Agent并发模型 ✓ / ✗
- [ ] 能设计一个新的工具 ✓ / ✗
- [ ] 能描述MCP集成流程 ✓ / ✗

---

## 🎓 Day 4总结

**核心理解**：
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

**设计亮点**：
_____________________________________________

**下一步**：
- [ ] 准备Day 5的内存系统学习

---

**Day 4 完成时间**：_____________  
**理解程度评分** (1-10)：_____

---

**文档版本**：1.0  
**最后更新**：2025-04-19

