# DeerFlow 后端 14天实战学习和重写计划

> **目标**：通过14天的系统学习和实践，完全理解DeerFlow后端架构，并能够从头到尾独立重写整个项目。

**总体策略**：
- 前7天：深度学习和理解
- 后7天：实践重写和验证
- 每天4-6小时投入，共计50-80小时

---

## 第1天：基础框架和项目结构认知

### 目标
建立整体认知，理解DeerFlow的定位、技术栈、系统架构。

### 任务清单

#### 任务1.1：学习项目定义和定位（1小时）
```
阅读材料：
  ✓ backend/README.md (完整)
  ✓ backend/CLAUDE.md - 项目概览部分
  ✓ backendclaude.md 第一、二部分

学习要点：
  • DeerFlow 是什么？（超级Agent框架 vs 普通ChatBot）
  • 为什么需要它？（隔离执行、持久化记忆、子Agent并行）
  • 与竞品的差异？（OpenAI Assistants vs AutoGen vs DeerFlow）
  
检验方式：
  - 用一句话定义DeerFlow
  - 列举其3个核心特性
  - 说出与Assistants API的3个差异
```

#### 任务1.2：学习系统架构（1小时）
```
阅读材料：
  ✓ backend/README.md - Architecture部分
  ✓ backend/docs/ARCHITECTURE.md - System Architecture
  ✓ backendclaude.md 第1.3节

学习要点：
  • 4层架构（Nginx → LangGraph/Gateway → 存储/工具）
  • 端口分配和服务隔离
  • 请求路由（/api/langgraph/ vs /api/* vs /）
  • 为什么需要反向代理？

检验方式：
  - 画出4层架构图
  - 解释Nginx为什么必要
  - 说出LangGraph和Gateway的职责边界
```

#### 任务1.3：理解技术栈（1小时）
```
阅读材料：
  ✓ backend/pyproject.toml
  ✓ backend/package/harness/pyproject.toml
  ✓ backendclaude.md 第1.2节

学习要点：
  • Python 3.12选择的原因
  • LangGraph核心库（版本、功能）
  • FastAPI为什么选择
  • 其他关键依赖（uvicorn, sse-starlette等）

检验方式：
  - 列举5个核心依赖和它们的用途
  - 说出为什么不用Flask/Django
```

#### 任务1.4：本地启动和初步探索（1.5小时）
```
操作步骤：
  1. cd /path/to/deer-flow
  2. make check                           # 验证工具链
  3. make install                         # 安装依赖
  4. make dev                             # 启动所有服务
  5. 浏览器打开 http://localhost:2026
  6. 查看logs/下的4个日志文件

关键观察：
  • 启动顺序（哪个服务先启）
  • 日志中的关键信息（config加载、模型初始化）
  • 前端界面基本功能
  • 试发一条简单消息，观察日志

检验方式：
  - 描述启动过程中发生了什么
  - 指出4个日志文件各自的作用
  - 找到一条Agent响应消息在logs中的生命周期
```

#### 任务1.5：快速代码浏览（1小时）
```
探索文件结构：
  tree backend/packages/harness/deerflow/ -L 2
  tree backend/app/gateway/ -L 2
  
  快速浏览文件清单：
  • agents/lead_agent/agent.py    (先看函数签名)
  • agents/thread_state.py        (理解ThreadState)
  • agents/middlewares/           (列举所有中间件)
  • sandbox/sandbox.py            (理解抽象接口)
  • tools/tools.py                (理解工具注册)
  • app/gateway/app.py            (理解FastAPI结构)

关键点：
  • 代码量并不大（相比业界水准）
  • 模块化设计（低耦合）
  • 命名清晰（易于理解）

检验方式：
  - 统计代码行数（估算）
  - 列举10个关键类/函数
  - 指出5个最复杂的模块
```

### 第1天总结
- ✅ 理解DeerFlow定位和价值
- ✅ 掌握系统4层架构
- ✅ 了解技术栈选择
- ✅ 成功启动本地开发环境
- ✅ 完成代码初步扫描

### 每日检验
在笔记本中回答：
- 什么是ThreadState？
- DeerFlow和Assistants API最大的差异是什么？
- 4个服务分别在哪个端口？

---

## 第2天：LangGraph和中间件链深度学习

### 目标
理解LangGraph基础和DeerFlow的中间件设计模式。

### 前置学习
```
官方资源：
  • https://langchain-ai.github.io/langgraph/concepts/low_level_vs_high_level/
  • https://langchain-ai.github.io/langgraph/how-tos/state-management/
  • LangGraph源码中的StateGraph类
```

### 任务清单

#### 任务2.1：学习LangGraph基础（1.5小时）
```
学习内容：
  1. StateGraph概念
     - 图中的节点 (node)
     - 图中的边 (edge)
     - 条件边 (conditional_edge)
     - 状态对象 (state)
  
  2. 执行流程
     - invoke() 同步执行
     - ainvoke() 异步执行
     - stream() 流式执行
  
  3. 检查点机制
     - Checkpointer接口
     - 暂停/恢复
  
实践代码：
  创建一个最简单的LangGraph例子：
  ```python
  from langgraph.graph import StateGraph
  from typing import TypedDict
  
  class SimpleState(TypedDict):
      messages: list[str]
  
  def node_a(state):
      state['messages'].append('A')
      return state
  
  def node_b(state):
      state['messages'].append('B')
      return state
  
  graph = StateGraph(SimpleState)
  graph.add_node('a', node_a)
  graph.add_node('b', node_b)
  graph.add_edge('a', 'b')
  graph.set_entry_point('a')
  
  app = graph.compile()
  result = app.invoke({'messages': []})
  print(result)  # {'messages': ['A', 'B']}
  ```

检验方式：
  - 建立一个3节点的StateGraph
  - 使用stream()查看中间状态
  - 从检查点恢复一次执行
```

#### 任务2.2：理解DeerFlow的ThreadState设计（1小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/agents/thread_state.py (完整)
  ✓ backendclaude.md 第2.1.3节

分析重点：
  1. ThreadState vs AgentState
     - 继承关系
     - 扩展字段
  
  2. 核心字段用途
     - messages: LangGraph标准消息历史
     - sandbox: 隔离执行环境信息
     - artifacts: 生成的文件
     - thread_data: 隔离目录路径
     - title: 自动生成的标题
     - todos: 任务追踪
     - viewed_images: 视觉模型图像
  
  3. 为什么这样设计？
     - 每个字段对应一个系统功能
     - 字段修改由中间件驱动

代码练习：
  # 创建ThreadState实例
  from deerflow.agents.thread_state import ThreadState
  
  state = ThreadState(
      messages=[],
      sandbox={'provider': 'local', 'id': 'thread_123'},
      artifacts=[],
      thread_data={...},
      ...
  )

检验方式：
  - 解释ThreadState的5个核心字段
  - ThreadState流经所有中间件，最后传给LLM，这样设计的好处是？
```

#### 任务2.3：深入学习中间件链（2小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/agents/middlewares/*.py (逐个文件)
  ✓ backendclaude.md 第2.1.2节
  ✓ backend/docs/middleware-execution-flow.md

分析每个中间件：

1. ThreadDataMiddleware (middlewares/thread_data.py)
   功能：为每个thread创建隔离目录
   输入：thread_id
   输出：state.thread_data = {workspace_dir, uploads_dir, outputs_dir}
   关键实现：使用什么库创建目录？
   
2. UploadsMiddleware (middlewares/uploads.py)
   功能：处理用户上传文件，注入到消息
   输入：上传文件的thread存储路径
   输出：修改state.messages，添加文件内容
   关键实现：如何避免重复处理同一文件？
   
3. SandboxMiddleware (middlewares/sandbox.py)
   功能：获取/初始化Sandbox环境
   输入：配置中的sandbox provider
   输出：state.sandbox = {provider_instance, id}
   关键实现：LocalSandbox vs AioSandbox的区别？
   
4. SummarizationMiddleware (middlewares/summarization.py)
   功能：当token接近上限时，压缩对话历史
   输入：state.messages（可能很长）
   输出：state.messages（压缩后）
   关键实现：如何评估token数？调用哪个LLM进行总结？
   
5. TodoListMiddleware (middlewares/todo_list.py)
   功能：在plan_mode下追踪任务列表
   输入：LLM解析的结构化输出
   输出：state.todos更新
   关键实现：如何从自由文本中提取结构化任务？
   
6. TitleMiddleware (middlewares/title.py)
   功能：首次对话后自动生成标题
   输入：第一个用户消息 + Agent响应
   输出：state.title = "生成的标题"
   关键实现：调用LLM生成标题的提示词是什么？
   
7. MemoryMiddleware (middlewares/memory.py)
   功能：将对话加入异步提取队列
   输入：完整对话（messages）
   输出：state（不修改），触发后台任务
   关键实现：如何保证不丢失任务？持久化到哪？
   
8. ViewImageMiddleware (middlewares/view_image.py)
   功能：为视觉模型加载图像数据
   输入：消息中的图像路径
   输出：state.viewed_images = {path: base64}
   关键实现：如何处理大图像？是否压缩？
   
9. ClarificationMiddleware (middlewares/clarification.py)
   功能：拦截澄清请求
   输入：可能的clarification标记
   输出：提前返回，中断后续处理
   关键实现：为什么要放在最后？

代码深入：
  # 打开middlewares/thread_data.py，逐行理解：
  class ThreadDataMiddleware(BaseMiddleware):
      def __call__(self, state: ThreadState) -> ThreadState:
          # 第1步：读取thread_id
          # 第2步：创建目录结构
          # 第3步：更新state.thread_data
          # 第4步：返回修改后的state
          ...

检验方式：
  - 用表格总结9个中间件的输入、输出、功能
  - 中间件执行顺序能否改变？为什么？
  - 如何调试一个中间件？
  - 如何新增一个中间件（例如：自定义上下文注入中间件）？
```

#### 任务2.4：理解中间件链集成（1小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/agents/lead_agent/agent.py
    - 特别关注make_lead_agent函数中的middleware应用

理解流程：
  1. 中间件链的构建
     ```python
     middleware_chain = [
         ThreadDataMiddleware(...),
         UploadsMiddleware(...),
         SandboxMiddleware(...),
         # ... 其他中间件
     ]
     ```
  
  2. 中间件链如何集成到Agent
     - StateGraph中的pre_process_state
     - 或者Runnable包装
  
  3. 执行顺序
     - 每个middleware.__call__()依次调用
     - ThreadState依次流经每个中间件

代码练习：
  # 创建一个简单的中间件链并测试
  class CustomMiddleware(BaseMiddleware):
      def __call__(self, state: ThreadState) -> ThreadState:
          print(f"Before: {len(state.messages)} messages")
          state.messages.append(...) # 某个修改
          print(f"After: {len(state.messages)} messages")
          return state
  
  # 链接起来
  middlewares = [existing_1, existing_2, CustomMiddleware(), ...]
  # 应用到graph

检验方式：
  - 描述ThreadState如何流经中间件链
  - 如何调试整个链？
  - 如果某个中间件抛异常，如何处理？
```

### 第2天总结
- ✅ 理解LangGraph基础概念和执行模型
- ✅ 掌握ThreadState设计思想
- ✅ 完整理解9个中间件的功能和顺序
- ✅ 理解中间件链集成机制
- ✅ 能手动创建简单的中间件

### 每日检验
```
在代码中标记出：
1. ThreadState的所有字段及其用途
2. 9个中间件的执行顺序
3. 哪个中间件调用了LLM？
4. 为什么SummarizationMiddleware要在SandboxMiddleware之后？
```

---

## 第3天：Sandbox隔离执行系统

### 目标
完全理解Sandbox的设计、实现和安全机制。

### 任务清单

#### 任务3.1：理解Sandbox抽象接口（1小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/sandbox/sandbox.py
  ✓ backendclaude.md 第2.2节

学习内容：
  1. Sandbox的5个核心方法
     - execute_command(command: str) -> str
     - read_file(path: str) -> str
     - write_file(path: str, content: str, append: bool) -> None
     - list_dir(path: str, max_depth: int) -> list[str]
     - glob(path: str, pattern: str) -> tuple[list[str], bool]
     - grep(path: str, pattern: str) -> tuple[list[GrepMatch], bool]
     - update_file(path: str, content: bytes) -> None
  
  2. 为什么要设计成抽象基类？
     - 支持多种实现（Local vs Docker vs SSH）
     - 工具代码无需知道实现细节
     - 易于单元测试（Mock Sandbox）

代码练习：
  # 理解接口
  from deerflow.sandbox import Sandbox
  
  class DummySandbox(Sandbox):
      def execute_command(self, command: str) -> str:
          return "dummy output"
      # ... 实现其他抽象方法
  
  # 这样的设计在未来如何支持SSH沙箱？

检验方式：
  - 为什么需要glob和grep方法？（而不是shell来做）
  - Sandbox为什么不提供delete_file方法？（安全考虑）
```

#### 任务3.2：理解LocalSandbox实现（1.5小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/sandbox/local/local_sandbox.py
  ✓ backend/packages/harness/deerflow/sandbox/tools.py (沙箱工具)
  ✓ backendclaude.md 第2.2.6节

分析重点：

1. LocalSandbox vs LocalSandboxProvider
   - Provider: 创建Sandbox实例的工厂
   - Sandbox: 具体的执行环境
   
   ```python
   class LocalSandboxProvider:
       def create_sandbox(self, sandbox_id: str) -> LocalSandbox:
           return LocalSandbox(sandbox_id, self.base_path)
   
   class LocalSandbox(Sandbox):
       def execute_command(self, command: str) -> str:
           # 实际实现
   ```

2. LocalSandbox的限制
   - bash工具禁用（直接执行命令太危险）
   - 只支持read/write/list_dir/glob/grep
   - 虚拟路径映射到真实目录

3. 虚拟路径映射
   ```python
   # 输入：/mnt/user-data/workspace/file.txt
   # 映射：/real/path/thread_{thread_id}/workspace/file.txt
   
   def resolve_path(self, virtual_path: str) -> str:
       if virtual_path.startswith('/mnt/user-data'):
           return os.path.join(self.base_path, ...)
   ```

4. 文件操作的原子性
   ```python
   class FileOperationLock:
       _locks: dict[tuple[str, str], RLock]  # (sandbox_id, path)
       
       # 保证str_replace的read-modify-write原子
       with self.acquire_lock(sandbox_id, path):
           content = read()
           content = content.replace(old, new)
           write(content)
   ```

代码练习：
  # 创建一个LocalSandbox并测试
  from deerflow.sandbox.local import LocalSandboxProvider
  
  provider = LocalSandboxProvider(base_path='/tmp/sandboxes')
  sandbox = provider.create_sandbox('test_123')
  
  # 测试操作
  sandbox.write_file('/mnt/user-data/workspace/test.txt', 'hello')
  content = sandbox.read_file('/mnt/user-data/workspace/test.txt')
  
  # 观察真实文件位置
  import os
  files = os.listdir('/tmp/sandboxes/test_123/workspace/')

检验方式：
  - 解释虚拟路径和真实路径的映射
  - str_replace为什么需要FileOperationLock？
  - LocalSandbox为何禁用bash？如何在需要时启用？
```

#### 任务3.3：Sandbox工具实现（1小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/sandbox/tools.py
  ✓ LLM工具协议 (tool_choice, function_calling等)

分析5个工具：

1. bash 工具
   ```python
   @tool(name="bash")
   def bash(command: str) -> str:
       """执行bash命令"""
       # LocalSandbox: 禁用
       # AioSandbox: 在Docker容器中执行
   ```
   
   配置：DEFAULT_BASH_ENABLED = False

2. ls 工具
   ```python
   @tool(name="ls")
   def ls(path: str, max_depth: int = 2) -> str:
       """列表目录内容，最多2层深度"""
       return sandbox.list_dir(path, max_depth)
   ```
   
   为什么有max_depth？
   - 防止列表太大
   - 强制LLM多步探索
   
3. read_file 工具
   ```python
   @tool(name="read_file")
   def read_file(path: str) -> str:
       """读取文件内容"""
       return sandbox.read_file(path)
   ```
   
   考虑：大文件处理？截断？

4. write_file 工具
   ```python
   @tool(name="write_file")
   def write_file(path: str, content: str) -> str:
       """覆盖写文件"""
       sandbox.write_file(path, content, append=False)
   ```
   
   什么场景用这个？

5. str_replace 工具 ⭐ 最重要
   ```python
   @tool(name="str_replace")
   def str_replace(
       path: str,
       old_str: str,
       new_str: str
   ) -> str:
       """替换文件中的文本
       
       1. 读取文件
       2. 查找old_str（必须精确匹配，包括缩进空格）
       3. 替换为new_str
       4. 写回
       5. 返回修改前后各20行上下文
       """
   ```
   
   为什么最好用？
   - LLM需要看到上下文
   - 精确匹配避免误触
   - 原子操作
   
   示例：
   ```python
   # 修改Python文件中的一个函数
   str_replace(
       path="/mnt/user-data/workspace/main.py",
       old_str="""def hello(name):
       print(f"Hi {name}")""",
       new_str="""def hello(name):
       print(f"Hello {name}!")"""
   )
   ```

代码练习：
  # 观察str_replace如何显示上下文
  # 打开test_sandbox.py，找到str_replace的测试用例
  
  # 修改一个源代码文件
  sandbox.write_file(
      '/mnt/user-data/workspace/app.py',
      '''def main():
    x = 1
    y = 2
    return x + y
'''
  )
  
  # 使用str_replace替换其中一部分
  result = sandbox.str_replace(
      '/mnt/user-data/workspace/app.py',
      'y = 2',
      'y = 3'
  )
  # 观察返回的上下文

检验方式：
  - str_replace vs write_file的区别是什么？
  - 为什么str_replace的old_str必须精确匹配？
  - 如何用str_replace修改一个代码文件中某个类的一个方法？
```

#### 任务3.4：安全策略和权限控制（0.5小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/sandbox/security.py

分析内容：

1. 命令黑名单
   ```python
   DANGEROUS_PATTERNS = [
       r"(?i)rm\s+-rf",              # 不允许递归删除
       r"(?i):(){ *:|:|",            # Fork炸弹
       r"(?i)shutdown|reboot",       # 系统命令
   ]
   ```
   
   这些检查在LocalSandbox有用吗？
   - LocalSandbox：bash禁用，所以无关
   - AioSandbox：Docker容器内检查，有用

2. 权限模型
   - Sandbox操作都在隔离的虚拟路径内
   - 无法访问/etc, /root等系统目录
   - 虚拟路径映射强制隔离

检验方式：
  - 设计一个恶意Agent：如何突破隔离？
  - 虚拟路径映射能否真正保证隔离？
```

#### 任务3.5：实现一个简单的Mock Sandbox（1小时）
```
实践目标：
  创建一个内存中的Sandbox（不操作真实文件系统）

代码框架：
  ```python
  from deerflow.sandbox import Sandbox
  
  class MemorySandbox(Sandbox):
      def __init__(self, sandbox_id: str):
          self._id = sandbox_id
          self._files = {}  # {path: content}
      
      def execute_command(self, command: str) -> str:
          raise NotImplementedError("Not supported")
      
      def read_file(self, path: str) -> str:
          return self._files.get(path, "File not found")
      
      def write_file(self, path: str, content: str, append: bool = False) -> None:
          if append:
              self._files[path] = self._files.get(path, "") + content
          else:
              self._files[path] = content
      
      def list_dir(self, path: str, max_depth=2) -> list[str]:
          # 实现目录列表
          ...
      
      # ... 其他方法
  ```

测试：
  ```python
  sandbox = MemorySandbox('test')
  sandbox.write_file('/test/file.txt', 'hello')
  content = sandbox.read_file('/test/file.txt')
  assert content == 'hello'
  ```

这个Mock有什么用？
  - 单元测试中避免真实文件I/O
  - 模拟复杂的Sandbox行为
  - 快速验证逻辑
```

### 第3天总结
- ✅ 理解Sandbox抽象设计
- ✅ 完全掌握LocalSandbox实现
- ✅ 理解5个沙箱工具的用途
- ✅ 理解虚拟路径隔离机制
- ✅ 理解安全策略
- ✅ 能创建Mock Sandbox进行测试

### 每日检验
```
1. Sandbox的7个方法分别用来做什么？
2. 虚拟路径/mnt/user-data/workspace映射到哪里？
3. str_replace与write_file的差异？
4. LocalSandbox为什么禁用bash？
5. 如何实现一个SSH-based Sandbox？
```

---

## 第4天：工具系统和子Agent

### 目标
理解工具多态、注册机制、以及子Agent委托系统。

### 任务清单

#### 任务4.1：理解工具系统架构（1小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/tools/tools.py
  ✓ backend/packages/harness/deerflow/tools/builtins/*.py
  ✓ backendclaude.md 第2.4节

学习内容：

1. LLM工具的标准格式
   ```python
   @tool(name="tool_name")
   def my_tool(param1: str, param2: int) -> str:
       """工具描述 (会注入提示词)"""
       return result
   ```
   
   LangChain自动生成：
   - 工具名
   - 参数JSON Schema
   - 描述

2. 工具的生命周期
   ```
   定义工具 (@tool装饰器)
       ↓
   注册到Agent (加入tools列表)
       ↓
   系统提示词中声明 (工具清单)
       ↓
   LLM选择调用
       ↓
   执行工具函数
       ↓
   结果返回给LLM
   ```

3. 工具分类
   - Sandbox工具 (5个: bash, ls, read_file, write_file, str_replace)
   - 子Agent工具 (task)
   - 内置工具 (present_files, ask_clarification, view_image)
   - MCP工具 (动态注册)
   - 社区工具 (可选)

检验方式：
  - 工具定义和工具执行有什么区别？
  - LLM如何知道有哪些工具可用？
```

#### 任务4.2：内置工具分析（1.5小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/tools/builtins/*.py
  ✓ 各工具源代码

逐个分析：

1. present_files (tools/builtins/present_files.py)
   功能：
   - 优化的文件展示（不是简单的列表）
   - 根据文件大小和类型智能格式化
   - 代码文件显示语法高亮信息
   - 太大的目录截断显示
   
   调用：
   ```python
   present_files(path='/mnt/user-data/workspace')
   # 返回格式化的字符串
   ```
   
   为什么需要这个工具？
   - LLM理解格式化输出更好
   - 减少token消耗
   - 提高可读性

2. ask_clarification (tools/builtins/ask_clarification.py)
   功能：
   - 当Agent不确定时请求用户澄清
   - 中断当前执行
   - 等待用户反馈
   
   调用：
   ```python
   ask_clarification(
       question="应该用Python还是Shell？",
       options=["Python", "Shell"]
   )
   ```
   
   实现机制：
   - ClarificationMiddleware拦截此工具
   - 返回特殊响应给前端
   - 前端显示选项对话框
   - 用户选择后恢复执行
   
   这为什么是"工具"而不是直接返回？
   - LLM决定何时需要澄清
   - Agent有主动权

3. view_image (tools/builtins/view_image.py)
   功能：
   - 加载图像供视觉模型分析
   - 读取图像文件，转base64
   - 传递给ViewImageMiddleware
   
   调用：
   ```python
   view_image(path='/mnt/user-data/uploads/screenshot.png')
   ```
   
   为什么需要这个工具？
   - 视觉模型在工具中处理图像
   - base64转换由工具负责
   - 不是直接在消息中嵌入

代码练习：
  # 创建一个自定义内置工具
  from langchain.tools import tool
  
  @tool(name="get_system_time")
  def get_system_time() -> str:
      """获取当前系统时间"""
      from datetime import datetime
      return datetime.now().isoformat()
  
  # 该工具如何加入Agent？
  # 在lead_agent/agent.py中添加到tools列表

检验方式：
  - 这3个工具分别解决什么问题？
  - 如何新增一个内置工具？
  - view_image为什么不直接读取文件到消息中？
```

#### 任务4.3：子Agent系统（1.5小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/subagents/executor.py
  ✓ backend/packages/harness/deerflow/subagents/builtins/
  ✓ backend/packages/harness/deerflow/subagents/registry.py
  ✓ backendclaude.md 第2.3节

分析内容：

1. 子Agent vs 主Agent
   
   主Agent:
   - 单一全局实例
   - 每个thread一个状态
   - 工具集完整
   - 同步执行
   - 无超时
   
   子Agent:
   - 临时实例
   - 每个任务一个
   - 工具集受限
   - 异步执行（线程池）
   - 15分钟超时
   - 最多3个并发

2. 内置子Agent
   
   a) general-purpose
      - 工具集: Sandbox + MCP + 社区 + 内置
      - 用途: 通用任务
      - 例: 分析数据、编写代码、搜索信息
   
   b) bash
      - 工具集: 仅bash
      - 用途: Shell命令专家
      - 例: 批量文件操作、系统管理
      - 仅当bash enabled时可用

3. SubagentExecutor架构
   
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
   
   执行流程：
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

4. Registry注册系统
   
   ```python
   class SubagentRegistry:
       _agents = {
           'general-purpose': make_general_purpose_agent,
           'bash': make_bash_agent,
       }
       
       @classmethod
       def get_agent(cls, agent_type: str) -> Callable:
           return cls._agents.get(agent_type)
   ```
   
   设计好处：
   - 易于添加新的子Agent类型
   - 不需要修改执行器代码

5. task()工具的实现
   
   ```python
   @tool(name="task")
   def task(
       description: str,
       agent_type: str = "general-purpose",
       context: dict = None
   ) -> str:
       """委托子Agent执行任务"""
       executor = get_subagent_executor()
       result = await executor.run_subagent(
           description, agent_type, context
       )
       return json.dumps(result)
   ```
   
   关键点：
   - 这是异步的！返回之前不等待完成
   - 使用SSE通知前端进度
   - 主Agent继续执行

代码练习：
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
  # - subagent_2 completed (results: ...)
  # - subagent_3 completed (results: ...)

检验方式：
  - 子Agent为什么需要异步？
  - 如何限制最多3个并发？
  - 子Agent超时了怎么办？
  - 如何添加一个新的子Agent类型（e.g., "sql"）？
```

#### 任务4.4：MCP工具集成（1小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/mcp/client.py
  ✓ backend/packages/harness/deerflow/mcp/tools.py
  ✓ MCP规范: https://modelcontextprotocol.io/

学习内容：

1. MCP概念
   MCP (Model Context Protocol) = Claude工具市场协议
   
   好处：
   - 标准化工具定义
   - 第三方工具生态
   - Agent无需修改即可扩展
   
   例如MCP服务器：
   - mcp-server-git (Git操作)
   - mcp-server-sqlite (数据库查询)
   - mcp-server-slack (Slack操作)

2. MCP客户端实现
   
   ```python
   class MCPClient:
       def __init__(self, server_config):
           self.process = subprocess.Popen(
               server_config['command'],
               stdin=PIPE, stdout=PIPE
           )
           self.rpc = JSONRPCClient(self.process)
       
       def list_tools(self) -> list[ToolDefinition]:
           return self.rpc.call('tools/list')
       
       def call_tool(
           self,
           tool_name: str,
           args: dict
       ) -> str:
           return self.rpc.call('tools/call', {
               'name': tool_name,
               'arguments': args
           })
   ```

3. MCP工具到Agent工具的转换
   
   ```python
   # MCP服务器提供的工具定义
   mcp_tool_def = {
       "name": "git_clone",
       "description": "Clone a git repository",
       "inputSchema": {
           "properties": {
               "url": {"type": "string"},
               "path": {"type": "string"}
           }
       }
   }
   
   # 转换为LangChain tool
   @tool(name="git_clone")
   def git_clone(url: str, path: str) -> str:
       """Clone a git repository"""
       mcp_client = get_mcp_client()
       return mcp_client.call_tool("git_clone", {
           "url": url, "path": path
       })
   ```

4. 工具缓存和生命周期
   
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

5. extensions_config.json格式
   
   ```json
   {
     "mcpServers": {
       "git": {
         "command": "mcp-server-git",
         "args": ["--debug"],
         "env": {"GIT_AUTHOR": "Agent"}
       },
       "sqlite": {
         "command": "mcp-server-sqlite",
         "args": ["/path/to/db"]
       }
     }
   }
   ```

检验方式：
  - MCP解决什么问题？
  - 如何集成一个新的MCP服务器？
  - MCP服务器崩溃了怎么办？
```

### 第4天总结
- ✅ 理解工具系统架构
- ✅ 掌握3个内置工具的用途
- ✅ 理解子Agent并发执行模型
- ✅ 理解MCP集成机制
- ✅ 能设计新的工具和子Agent

### 每日检验
```
1. 为什么view_image是一个工具而不是自动处理？
2. 子Agent最多同时运行几个？为什么是这个数字？
3. task()工具是同步还是异步的？为什么？
4. 如何添加一个新的MCP服务器？
5. 设计一个"researcher" Agent类型，只提供搜索、阅读、总结工具
```

---

## 第5天：记忆系统和技能系统

### 目标
理解持久化记忆提取和技能加载机制。

### 任务清单

#### 任务5.1：内存提取系统（1.5小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/agents/memory/*.py
  ✓ backend/docs/MEMORY_IMPROVEMENTS.md
  ✓ backendclaude.md 第2.1.5节

学习内容：

1. 内存系统架构
   
   会话完成
       ↓
   MemoryMiddleware入队对话
       ↓
   异步消费者线程
       ├→ memory/extraction.py: 分析对话
       ├→ memory/queue.py: 处理队列
       └→ memory/prompts.py: LLM提示词
       ↓
   提取: {用户背景, 关键事实, 偏好, 置信度}
       ↓
   持久化到memory.db
       ↓
   后续对话检索相关记忆
       ↓
   注入系统提示词

2. extraction.py - 内存提取
   
   功能：
   - 分析对话文本
   - 识别用户信息
   - 提取可重用事实
   - 评分置信度
   
   LLM提示词例：
   ```
   你是记忆助手。分析这段对话，提取：
   
   1. 用户背景 (work_context)
   2. 个人偏好 (personal_context)
   3. 关键事实 (facts: list[{text, confidence}])
   
   对话:
   [对话文本]
   
   返回JSON:
   {
       "work_context": "用户是数据分析师...",
       "personal_context": "用户喜欢Python...",
       "facts": [
           {"text": "用户使用Pandas", "confidence": 0.95},
           {"text": "用户偏好可视化", "confidence": 0.8}
       ]
   }
   ```

3. queue.py - 异步处理
   
   设计：
   ```python
   class MemoryQueue:
       def __init__(self):
           self.queue: queue.Queue = queue.Queue()
           self.consumer_thread = Thread(
               target=self._consume,
               daemon=True
           )
           self.consumer_thread.start()
       
       def add(self, thread_id: str, messages: list):
           self.queue.put((thread_id, messages))
       
       def _consume(self):
           while True:
               thread_id, messages = self.queue.get()
               facts = extract_memory(messages)
               save_to_db(facts)
               self.queue.task_done()
   ```
   
   为什么异步？
   - 提取耗时（LLM调用）
   - 不应阻塞主Agent
   - 后台构建知识库
   
   队列持久化吗？
   - 简单持久化：写到文件
   - 生产级：写到Redis或消息队列

4. 数据库schema
   
   ```sql
   CREATE TABLE facts (
       id TEXT PRIMARY KEY,
       user_id TEXT,
       fact TEXT,
       confidence FLOAT,  -- [0.0, 1.0]
       source_thread_id TEXT,
       created_at DATETIME,
       updated_at DATETIME,
       category TEXT -- 'background', 'preference', 'fact'
   );
   
   CREATE TABLE user_context (
       user_id TEXT PRIMARY KEY,
       work_context TEXT,
       personal_context TEXT,
       top_of_mind TEXT,
       updated_at DATETIME
   );
   ```

5. 检索和注入
   
   当新对话开始：
   ```python
   def get_memory_context(user_id: str) -> str:
       facts = db.query("""
           SELECT fact, confidence FROM facts
           WHERE user_id = ? AND confidence > 0.7
           ORDER BY updated_at DESC
           LIMIT 10
       """, user_id)
       
       context = db.query("""
           SELECT work_context, personal_context
           FROM user_context
           WHERE user_id = ?
       """, user_id)
       
       prompt = f"""
   关于用户的信息：
   
   工作背景: {context.work_context}
   个人偏好: {context.personal_context}
   
   关键事实:
   {' '.join([f"• {f.fact} (置信度:{f.confidence})" for f in facts])}
   
   请在回复中参考这些信息。
   """
       return prompt
   ```

6. 置信度和衰减
   
   ```python
   # 同一事实重复出现→置信度上升
   if existing_fact:
       existing_fact.confidence = min(
           existing_fact.confidence + 0.1,
           1.0
       )
   
   # 时间衰减→旧事实权重下降
   confidence = base_confidence * (0.95 ** days_ago)
   ```

代码练习：
  # 设计一个内存提取提示词
  # 目标：从对话中提取"这个用户擅长什么技能"
  
  conversation = """
  用户: 我想分析这个数据集
  助手: 可以，用什么工具？
  用户: 我用R的ggplot2
  助手: 不错，用R做可视化很强...
  用户: 我经常用R和Python切换
  """
  
  # 为extraction写一个提示词，提取skills
  prompt = """
  从对话中提取用户的技能...
  """

检验方式：
  - 为什么内存提取必须异步？
  - 如何处理内存中的重复事实？
  - 置信度如何随时间衰减？
  - 如何避免内存提取的"幻觉"？
```

#### 任务5.2：技能系统（1.5小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/skills/*.py
  ✓ skills/public/目录结构
  ✓ 任意一个SKILL.md文件

学习内容：

1. 技能发现机制
   
   ```python
   def discover_skills(skills_dir: str) -> dict[str, dict]:
       skills = {}
       
       for root, dirs, files in os.walk(skills_dir):
           if 'SKILL.md' in files:
               skill_name = os.path.basename(root)
               skill_path = os.path.relpath(root, skills_dir)
               
               skills[skill_name] = {
                   'name': skill_name,
                   'path': f'/mnt/skills/{skill_path}',
                   'description': parse_skill_description(),
                   'usage': parse_usage_examples(),
               }
       
       return skills
   ```
   
   为什么递归扫描？
   - 支持嵌套技能容器
   - 灵活的技能组织方式

2. SKILL.md格式
   
   ```markdown
   # 数据分析技能
   
   ## 功能概述
   此技能提供...
   
   ## 使用示例
   ```python
   from utils import analyze_csv
   result = analyze_csv('/mnt/user-data/uploads/data.csv')
   ```
   
   ## 文件清单
   - utils.py
   - requirements.txt
   
   ## 限制
   - 仅支持CSV格式
   - 最大文件1GB
   ```
   
   三个部分：
   - 功能概述：做什么
   - 使用示例：如何用
   - 文件清单：包含什么

3. 技能提示词注入
   
   系统提示词示例：
   ```
   可用的技能：
   
   1. 数据分析 (/mnt/skills/data_analysis)
      功能: CSV分析、统计、绘图
      使用: from utils import analyze_csv
      
   2. Web研究 (/mnt/skills/web_research)
      功能: 网页爬取、信息提取
      使用: from utils import web_search
      
   使用技能的步骤：
   1. cd /mnt/skills/技能名
   2. 查看README和示例
   3. 导入并调用函数或脚本
   ```

4. 技能加载到沙箱
   
   ```python
   # /mnt/skills 是只读共享的
   # Agent通过相对导入加载技能
   
   # 例：在沙箱中执行
   bash("""
   cd /mnt/skills/data_analysis
   python analyze.py /mnt/user-data/uploads/data.csv
   """)
   ```

5. 嵌套技能容器
   
   ```
   skills/public/
   ├── simple_skill/
   │   └── SKILL.md
   │
   └── complex_analysis/
       ├── SKILL.md
       ├── python/
       │   ├── SKILL.md           # 嵌套
       │   └── main.py
       └── shell/
           ├── SKILL.md           # 嵌套
           └── run.sh
   ```
   
   虚拟路径:
   ```
   /mnt/skills/simple_skill
   /mnt/skills/complex_analysis
   /mnt/skills/complex_analysis/python
   /mnt/skills/complex_analysis/shell
   ```
   
   为什么支持嵌套？
   - 组织复杂技能集合
   - 子技能独立版本控制
   - 代码重用

6. 技能管理工具
   
   ```python
   @tool(name="skill_manage")
   def skill_manage(
       action: str,  # list, search, install, update
       name: str = None
   ) -> str:
       """管理技能"""
       if action == 'list':
           return json.dumps(discover_skills())
       elif action == 'search':
           return search_skills_in_market(name)
       elif action == 'install':
           return install_skill_from_market(name)
   ```

代码练习：
  # 创建一个自定义技能
  
  # 1. 创建目录
  mkdir -p skills/public/my_analyzer
  
  # 2. 编写SKILL.md
  cat > skills/public/my_analyzer/SKILL.md << 'EOF'
  # 自定义分析器
  
  ## 功能
  分析JSON数据并生成报告
  
  ## 使用
  ```python
  from analyzer import run_analysis
  result = run_analysis('/mnt/user-data/uploads/data.json')
  ```
  EOF
  
  # 3. 编写analyzer.py
  cat > skills/public/my_analyzer/analyzer.py << 'EOF'
  def run_analysis(path):
      import json
      with open(path) as f:
          data = json.load(f)
      return {"count": len(data), "keys": list(data[0].keys())}
  EOF
  
  # 4. 测试发现
  # 运行Agent，看是否发现到这个技能

检验方式：
  - SKILL.md格式的三个关键部分是什么？
  - 为什么技能路径用虚拟路径？
  - 嵌套技能如何组织和访问？
  - 如何从Agent中调用一个技能？
```

### 第5天总结
- ✅ 理解异步内存提取机制
- ✅ 理解内存数据库设计
- ✅ 理解技能发现和加载
- ✅ 理解SKILL.md格式
- ✅ 理解嵌套技能容器
- ✅ 能创建自定义技能

### 每日检验
```
1. 内存提取为什么必须异步？
2. 置信度如何在重复事实时更新？
3. 技能发现算法是什么？
4. SKILL.md的三个必要部分？
5. 如何让Agent知道一个新增的技能？
```

---

## 第6天：模型系统和Gateway API

### 目标
理解模型工厂、多模型支持、以及REST API网关。

### 任务清单

#### 任务6.1：模型工厂和动态选择（1.5小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/models/*.py
  ✓ backend/packages/harness/deerflow/config/model_config.py
  ✓ backend/docs/AUTO_TITLE_GENERATION.md

学习内容：

1. 模型配置
   
   ```yaml
   # config.yaml
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

2. 模型工厂
   
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

3. 模型能力声明
   
   ```python
   class ModelCapabilities:
       vision: bool         # 支持图像输入
       thinking: bool       # 支持思考模式
       tool_use: bool       # 支持工具调用
       max_tokens: int      # 最大生成token
       input_token_limit: int
   
   # 使用：
   if model.capabilities.vision:
       # 启用ViewImageMiddleware
       pass
   
   if model.capabilities.thinking:
       # 在系统提示词中启用思考模式
       pass
   ```

4. 模型选择策略
   
   ```python
   def select_model(
       task_type: str,
       user_preference: str = None,
       context_length: int = None
   ) -> ChatModel:
       """
       选择最合适的模型
       
       策略：
       1. 用户指定 → 使用用户模型
       2. Task需求 → 选择具有必要能力的模型
       3. Context长度 → 选择token限制足够的
       4. 默认 → 配置中的default_model
       """
       
       if user_preference:
           return get_model(user_preference)
       
       if task_type == 'vision_analysis' and model.capabilities.vision:
           return get_model_with_vision()
       
       if context_length and context_length > 100000:
           return get_model_with_large_context()
       
       return get_default_model()
   ```

5. 思考模式集成
   
   ```python
   # 对于支持thinking的模型
   if model.capabilities.thinking:
       system_prompt += """
   你有能力进行深入思考。在处理复杂问题时：
   1. 先内部思考（不需要呈现给用户）
   2. 分析问题的各个方面
   3. 得出结论后再回复
   
   这样能提高准确性。
   """
   ```

6. 视觉模型支持
   
   ```python
   if model.capabilities.vision:
       # ViewImageMiddleware 会填充 state.viewed_images
       # 消息中包含 {'type': 'image_url', 'image_url': {...}}
       
       # LangChain自动处理格式转换
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

代码练习：
  # 创建一个新的模型配置
  new_config = ModelConfig(
      name="claude-sonnet",
      provider="anthropic",
      api_key="sk-...",
      capabilities=ModelCapabilities(
          vision=True,
          thinking=False,
          tool_use=True,
          max_tokens=4000
      )
  )
  
  model = ModelFactory.create_model(new_config)

检验方式：
  - 如何添加一个新的模型提供商？
  - 思考模式和普通模式的差异？
  - 如何根据任务自动选择模型？
```

#### 任务6.2：Gateway API设计（1.5小时）
```
阅读材料：
  ✓ backend/app/gateway/app.py
  ✓ backend/app/gateway/routers/*.py
  ✓ backend/docs/API.md

学习内容：

1. FastAPI应用结构
   
   ```python
   # app/gateway/app.py
   
   from fastapi import FastAPI
   from contextlib import asynccontextmanager
   
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

2. 路由模块
   
   a) models.py - /api/models
   ```python
   @router.get("/models")
   async def list_models() -> list[ModelInfo]:
       """列表所有可用模型"""
       return [
           ModelInfo(name="claude-opus", capabilities=[...]),
           ModelInfo(name="gpt-4", capabilities=[...])
       ]
   
   @router.get("/models/{name}")
   async def get_model(name: str) -> ModelInfo:
       """获取模型详情"""
       model = config.get_model(name)
       return ModelInfo(...)
   
   @router.post("/models/{name}/test")
   async def test_model(name: str, prompt: str) -> TestResult:
       """测试模型连接"""
       model = ModelFactory.create(config.get_model(name))
       response = model.invoke(prompt)
       return TestResult(success=True, response=response)
   ```
   
   b) mcp.py - /api/mcp
   ```python
   @router.get("/mcp/servers")
   async def list_servers() -> list[MCPServerInfo]:
       """列表已启用的MCP服务器"""
       ...
   
   @router.post("/mcp/servers")
   async def add_server(config: MCPServerConfig):
       """新增MCP服务器"""
       client = MCPClient(config)
       register_mcp_tools(client)
       cache_server(config.name, client)
   ```
   
   c) skills.py - /api/skills
   ```python
   @router.get("/skills")
   async def list_skills() -> dict[str, SkillInfo]:
       """列表所有技能"""
       return discover_skills()
   
   @router.post("/skills/install")
   async def install_skill(name: str) -> InstallResult:
       """从市场安装技能"""
       ...
   
   @router.delete("/skills/{name}")
   async def delete_skill(name: str):
       """删除技能"""
       ...
   ```
   
   d) uploads.py - /api/threads/{id}/uploads
   ```python
   @router.post("/threads/{thread_id}/uploads")
   async def upload_file(
       thread_id: str,
       file: UploadFile
   ) -> UploadResponse:
       """上传文件"""
       # 1. 验证thread_id
       # 2. 保存到 thread/{thread_id}/uploads/
       # 3. 返回虚拟路径
       save_path = f"{thread_dir}/uploads/{file.filename}"
       with open(save_path, 'wb') as f:
           content = await file.read()
           f.write(content)
       
       return UploadResponse(
           path=f"/mnt/user-data/uploads/{file.filename}",
           size=len(content)
       )
   ```
   
   e) threads.py - /api/threads/{id}
   ```python
   @router.get("/threads/{thread_id}")
   async def get_thread(thread_id: str) -> ThreadInfo:
       """获取线程信息"""
       return ThreadInfo(
           id=thread_id,
           created_at=...,
           updated_at=...,
           files_count=...
       )
   
   @router.delete("/threads/{thread_id}")
   async def delete_thread(thread_id: str):
       """删除线程
       
       分离职责：
       - LangGraph: DELETE /api/langgraph/threads/{id}
       - Gateway: DELETE /api/threads/{id} (删除本地文件)
       """
       
       # 1. 调用LangGraph删除
       await langgraph_runtime.delete_thread(thread_id)
       
       # 2. 删除本地文件
       thread_dir = Paths.get_thread_dir(thread_id)
       shutil.rmtree(thread_dir)
   ```
   
   f) artifacts.py - /api/threads/{id}/artifacts
   ```python
   @router.get("/threads/{thread_id}/artifacts")
   async def list_artifacts(thread_id: str) -> list[ArtifactInfo]:
       """列表线程中生成的工件"""
       artifacts_dir = f"{thread_dir}/outputs/"
       return [
           ArtifactInfo(name=f, size=size)
           for f in os.listdir(artifacts_dir)
       ]
   
   @router.get("/threads/{thread_id}/artifacts/{name}")
   async def download_artifact(thread_id: str, name: str):
       """下载工件"""
       path = f"{thread_dir}/outputs/{name}"
       return FileResponse(path)
   ```

3. 线程清理流程
   
   用户删除对话：
   ```
   前端: DELETE /api/langgraph/threads/{id}
       └→ LangGraph处理，删除消息历史
   
   前端: DELETE /api/threads/{id}
       └→ Gateway处理：
           1. rm -rf thread/{id}/workspace/
           2. rm -rf thread/{id}/uploads/
           3. rm -rf thread/{id}/outputs/
   ```

代码练习：
  # 创建一个新的路由模块
  
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

检验方式：
  - Gateway API和LangGraph Server的职责边界？
  - 为什么上传/删除要用虚拟路径？
  - 如何新增一个API路由？
  - 什么情况下应该在LangGraph中实现，什么情况下在Gateway中？
```

### 第6天总结
- ✅ 理解模型工厂和动态选择
- ✅ 理解模型能力声明机制
- ✅ 理解思考模式和视觉模型集成
- ✅ 理解Gateway API整体设计
- ✅ 理解每个路由的职责
- ✅ 理解线程清理的分离职责

### 每日检验
```
1. 如何添加一个新的模型提供商？
2. 思考模式如何在系统提示词中启用？
3. 视觉模型如何加载图像？
4. Gateway和LangGraph的职责边界？
5. 上传的文件为什么不直接保存到outputs/?
```

---

## 第7天：配置系统、错误处理和部署

### 目标
理解配置管理、错误处理策略和部署架构。

### 任务清单

#### 任务7.1：配置系统（1小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/config/*.py
  ✓ config.example.yaml
  ✓ extensions_config.example.json

学习内容：

1. 配置加载顺序
   
   ```
   1. config.yaml (主配置文件)
       ├→ models:配置
       ├→ sandbox: 配置
       ├→ tools: 配置
       ├→ memory: 配置
       └→ ...
   
   2. extensions_config.json (MCP和技能)
       ├→ mcpServers: {...}
       └→ skills: {...}
   
   3. 环境变量 (覆盖文件配置)
       ├→ ANTHROPIC_API_KEY
       ├→ OPENAI_API_KEY
       └→ ...
   
   4. 运行时修改 (最高优先级)
       └→ API调用修改配置
   ```

2. AppConfig数据类
   
   ```python
   @dataclass
   class AppConfig:
       models: list[ModelConfig]
       sandbox: SandboxConfig
       tools: ToolsConfig
       memory: MemoryConfig
       skills: SkillsConfig
       channels: dict[str, ChannelConfig]
       
       # 验证
       def validate(self):
           # 检查必需字段
           # 检查格式
           # 检查API Key存在
           pass
   ```

3. 配置验证
   
   ```python
   def load_config() -> AppConfig:
       # 1. 读取yaml
       with open('config.yaml') as f:
           yaml_config = yaml.safe_load(f)
       
       # 2. 解析为AppConfig
       config = AppConfig(**yaml_config)
       
       # 3. 验证
       config.validate()
       
       # 4. 环境变量覆盖
       config.override_from_env()
       
       return config
   ```

4. 动态重加载
   
   ```python
   # 支持在运行时更新配置
   @router.post("/api/config/reload")
   async def reload_config():
       """重加载配置（无需重启服务）"""
       new_config = load_config()
       global APP_CONFIG
       APP_CONFIG = new_config
       
       return {"status": "reloaded"}
   ```

检验方式：
  - 配置的加载顺序是什么？
  - 如何覆盖一个模型的API Key？
  - 支持动态重加载吗？
```

#### 任务7.2：错误处理和日志（1小时）
```
阅读材料：
  ✓ backend/packages/harness/deerflow/exceptions.py
  ✓ 项目中的logging使用

学习内容：

1. 异常体系
   
   ```python
   class DeerFlowException(Exception):
       """基础异常"""
       pass
   
   class SandboxException(DeerFlowException):
       """沙箱执行异常"""
       pass
   
   class ToolExecutionException(DeerFlowException):
       """工具执行异常"""
       pass
   
   class ConfigException(DeerFlowException):
       """配置异常"""
       pass
   
   class MemoryException(DeerFlowException):
       """内存系统异常"""
       pass
   ```

2. 异常处理策略
   
   ```python
   # 工具执行时：捕获异常，返回错误信息
   try:
       result = tool.invoke(args)
   except ToolExecutionException as e:
       return ToolExecutionResult(
           success=False,
           error=str(e),
           suggestion="可能的解决方案..."
       )
   
   # 中间件中：异常传播vs吞掉
   try:
       state = middleware(state)
   except Exception as e:
       if isinstance(e, CriticalException):
           raise  # 关键异常：中止执行
       else:
           log.error(f"Middleware error: {e}")
           # 继续执行
   ```

3. 日志系统
   
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   
   logger.info(f"Starting agent for thread {thread_id}")
   logger.warning(f"Model {model_name} not available")
   logger.error(f"Failed to execute tool: {e}")
   logger.debug(f"ThreadState: {state}")
   ```
   
   日志级别：
   - DEBUG: 详细执行流
   - INFO: 关键事件
   - WARNING: 警告但继续
   - ERROR: 错误处理
   - CRITICAL: 系统崩溃

检验方式：
  - DeerFlow有哪些自定义异常？
  - 工具执行异常如何处理？
  - 日志输出的关键信息是什么？
```

#### 任务7.3：部署架构（1.5小时）
```
阅读材料：
  ✓ docker/docker-compose-dev.yaml
  ✓ docker/docker-compose.yaml
  ✓ backend/Dockerfile
  ✓ Makefile

学习内容：

1. 开发部署 (make dev)
   
   ```
   启动4个进程：
   
   1. LangGraph Server (2024)
      - 运行: python -m langgraph.cli serve
      - 从backend/langgraph.json加载agent
      - 提供: /api/langgraph/* 端点
   
   2. Gateway API (8001)
      - 运行: python -m app.gateway.app
      - FastAPI应用
      - 提供: /api/* 端点（非langgraph）
   
   3. Frontend (3000)
      - 运行: pnpm dev
      - Next.js开发服务器
      - 提供: /* (Web UI)
   
   4. Nginx (2026)
      - 运行: nginx -c /path/to/nginx.conf
      - 反向代理，统一入口
      - 路由到上述3个服务
   
   启动顺序：
   - 先启动后端（LangGraph, Gateway）
   - 后启动前端
   - 最后启动Nginx
   ```

2. Docker生产部署
   
   ```yaml
   # docker-compose.yaml
   
   services:
     langgraph:
       image: deerflow:langgraph
       ports:
         - "2024:2024"
       volumes:
         - ./config.yaml:/app/config.yaml
         - threads_data:/app/thread_data
     
     gateway:
       image: deerflow:gateway
       ports:
         - "8001:8001"
       depends_on:
         - langgraph
       environment:
         - LANGGRAPH_URL=http://langgraph:2024
     
     frontend:
       image: deerflow:frontend
       ports:
         - "3000:3000"
     
     nginx:
       image: nginx
       ports:
         - "2026:80"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
       depends_on:
         - langgraph
         - gateway
         - frontend
   
   volumes:
     threads_data:
   ```

3. Kubernetes部署 (Provisioner模式)
   
   ```
   当Agent需要执行高隔离的任务：
   
   1. Agent调用 provision_sandbox()
   2. Provisioner(K8s controller) 收到请求
   3. 创建临时Pod
   4. Agent连接执行
   5. 任务完成删除Pod
   
   优点：
   - 完全隔离
   - 可动态扩展
   - 资源高效
   ```

4. Makefile命令
   
   ```makefile
   make dev              # 启动4个进程
   make dev-pro          # 启动Gateway mode (嵌入Agent)
   make stop             # 停止所有服务
   make docker-dev       # Docker开发模式
   make docker-prod      # Docker生产模式
   
   # 后端特定
   cd backend
   make lint             # 代码检查
   make test             # 运行测试
   make serve            # 启动LangGraph
   ```

代码练习：
  # 理解Dockerfile的多阶段构建
  
  cat backend/Dockerfile
  
  # 典型结构：
  # Stage 1: Build
  #   - 安装Python依赖
  #   - 编译(如需要)
  # Stage 2: Runtime
  #   - 复制build产物
  #   - 设置入口

检验方式：
  - make dev启动了哪几个进程？
  - Nginx的作用是什么？
  - Docker部署时如何共享thread数据？
  - 如何扩展Gateway API的副本数？
```

#### 任务7.4：系统集成和测试（1小时）
```
阅读材料：
  ✓ backend/tests/test_*.py (选看几个)

学习内容：

1. 测试分类
   
   ```
   单元测试: 
     - test_sandbox.py: Sandbox操作
     - test_middlewares.py: 中间件链
     - test_tools.py: 工具执行
   
   集成测试:
     - test_agent_e2e.py: Agent完整流程
     - test_file_upload.py: 上传到处理
   
   E2E测试:
     - test_client_e2e.py: 完整Web流程
   ```

2. 测试框架
   
   ```python
   import pytest
   from unittest.mock import Mock, patch
   
   @pytest.fixture
   def sandbox():
       """创建测试用沙箱"""
       return MemorySandbox('test_123')
   
   def test_read_file(sandbox):
       sandbox.write_file('/test.txt', 'hello')
       content = sandbox.read_file('/test.txt')
       assert content == 'hello'
   
   @pytest.mark.asyncio
   async def test_agent_execution():
       """异步Agent测试"""
       agent = make_lead_agent(test_config)
       result = await agent.ainvoke({...})
       assert result['success']
   ```

3. Mock和Fixture
   
   ```python
   @pytest.fixture
   def mock_model():
       """Mock LLM模型"""
       model = Mock()
       model.invoke.return_value = "Model response"
       return model
   
   @pytest.fixture
   def test_config():
       """测试配置"""
       return AppConfig(
           models=[...],
           sandbox=SandboxConfig(provider='local')
       )
   ```

检验方式：
  - 后端的测试覆盖了哪些关键功能？
  - 如何mock一个外部服务（如MCP服务器）？
  - 如何测试异步流程？
```

### 第7天总结
- ✅ 理解配置系统和加载顺序
- ✅ 理解异常体系和错误处理
- ✅ 理解日志记录
- ✅ 理解4种部署方式（开发、Docker、K8s、Gateway mode）
- ✅ 理解测试体系

### 每日检验
```
1. 配置的加载顺序是什么？环境变量如何覆盖？
2. DeerFlow有哪些自定义异常？
3. 开发模式启动了几个进程？
4. Docker生产模式如何共享thread数据？
5. 如何编写一个完整的单元测试？
```

---

## 第8-14天：实践重写阶段

> **进入实践阶段**：使用前7天的学习，从头开始完整重写DeerFlow后端。

### 总体策略

**时间分配**：
- Day 8: 基础框架搭建 (1天)
- Day 9-10: 中间件链 + ThreadState (2天)
- Day 11: Sandbox系统 (1天)
- Day 12: 工具和子Agent系统 (1天)
- Day 13: 网关API + 模型系统 (1天)
- Day 14: 测试、集成和打磨 (1天)

### 第8天：基础框架搭建

#### 目标
建立项目基本结构，创建最小可运行的Agent框架。

#### 任务清单

```
任务8.1：项目初始化 (1小时)
├─ 1. 创建新项目目录: deer-flow-rewrite/
├─ 2. 初始化Python项目结构
│  ├─ pyproject.toml (依赖声明)
│  ├─ requirements.txt (快速安装)
│  ├─ uv.lock (锁定版本)
│  └─ ruff.toml (代码风格)
├─ 3. 设置虚拟环境: python -m venv venv
└─ 4. 安装核心依赖: langgraph, fastapi, ...

任务8.2：文件夹结构 (0.5小时)
├─ deerflow/
│  ├─ agents/
│  │  ├─ lead_agent/
│  │  ├─ middlewares/
│  │  └─ thread_state.py
│  ├─ sandbox/
│  ├─ tools/
│  ├─ subagents/
│  ├─ models/
│  ├─ skills/
│  ├─ mcp/
│  ├─ config/
│  └─ __init__.py
├─ app/
│  ├─ gateway/
│  └─ __init__.py
├─ tests/
└─ docs/

任务8.3：ThreadState定义 (1.5小时)
├─ 1. 理解LangGraph的AgentState
├─ 2. 扩展AgentState创建ThreadState
├─ 3. 定义所有字段 (messages, sandbox, artifacts等)
└─ 4. 写单元测试

任务8.4：最小Agent (1小时)
├─ 1. 创建make_lead_agent()函数框架
├─ 2. 创建一个简单的StateGraph
├─ 3. 添加一个简单的节点 (agent_node)
└─ 4. 编译并测试: agent.invoke(input)

检验标准：
✓ 能运行 python -c "from deerflow.agents import make_lead_agent"
✓ 能创建一个空的Agent
✓ 能调用 agent.invoke({"messages": []}) 并得到输出
```

### 第9-10天：中间件链实现

#### 目标
完整实现9个中间件，建立中间件链执行框架。

#### 任务清单

```
Day 9 - 中间件基础框架 (1天)

任务9.1：中间件基类 (1小时)
├─ 1. 创建BaseMiddleware抽象基类
│  ├─ __call__(state: ThreadState) -> ThreadState
│  └─ 子类需要实现__call__
├─ 2. 创建MiddlewareChain协调器
│  └─ 依次调用所有中间件
└─ 3. 异常处理机制

任务9.2：关键中间件实现 (2小时)
├─ ThreadDataMiddleware
│  ├─ 为thread_id创建目录
│  ├─ workspace/, uploads/, outputs/
│  └─ 更新state.thread_data
├─ UploadsMiddleware
│  ├─ 扫描上传文件
│  └─ 注入到messages
└─ SandboxMiddleware
   ├─ 初始化Sandbox
   └─ 更新state.sandbox

任务9.3：其他中间件 (1小时)
├─ SummarizationMiddleware (简单实现)
├─ TodoListMiddleware (可选skip)
├─ TitleMiddleware (调用LLM生成标题)
├─ MemoryMiddleware (异步队列)
├─ ViewImageMiddleware (条件启用)
└─ ClarificationMiddleware (最后执行)

任务9.4：测试中间件链 (1小时)
├─ 测试单个中间件
├─ 测试链式调用
└─ 测试异常处理

检验标准：
✓ 能创建中间件链: chain = MiddlewareChain(middlewares)
✓ 能流转ThreadState: state = chain(state)
✓ ThreadState的各字段已更新
✓ 单元测试覆盖 >70%

Day 10 - 中间件与Agent集成 (1天)

任务10.1：Agent节点设计 (1小时)
├─ 1. 设计Agent执行节点
│  ├─ 输入: ThreadState
│  ├─ 处理: 调用LLM + 工具调用
│  └─ 输出: 修改后的ThreadState
└─ 2. 处理多步骤（工具调用循环）

任务10.2：工具调用循环 (1.5小时)
├─ 1. LLM返回ToolCall
├─ 2. 执行工具
├─ 3. 返回结果给LLM
└─ 4. 循环直到LLM返回消息

任务10.3：集成中间件与Agent (0.5小时)
├─ 1. 在Agent节点前调用中间件链
├─ 2. 修改后的ThreadState传给LLM
└─ 3. 测试完整流程

任务10.4：端到端流程测试 (1小时)
├─ 1. 创建测试用例
├─ 2. 模拟用户输入
├─ 3. 验证Agent响应
└─ 4. 验证ThreadState更新

检验标准：
✓ Agent能处理消息并响应
✓ 中间件在正确的顺序执行
✓ ThreadState完整流转
✓ 工具调用循环正常
```

### 第11天：Sandbox系统实现

#### 目标
实现Sandbox的本地提供商和工具集。

#### 任务清单

```
任务11.1：Sandbox抽象接口 (0.5小时)
├─ 1. 定义Sandbox基类
│  ├─ execute_command()
│  ├─ read_file()
│  ├─ write_file()
│  ├─ list_dir()
│  ├─ glob()
│  └─ grep()
└─ 2. 定义SandboxProvider工厂

任务11.2：LocalSandbox实现 (2小时)
├─ 1. 虚拟路径映射
│  ├─ /mnt/user-data/ → thread_dir
│  ├─ /mnt/skills/ → skills_dir
│  └─ 路径转换函数
├─ 2. 文件操作实现
│  ├─ read_file: os.read
│  ├─ write_file: os.write
│  └─ list_dir: os.listdir + 递归
├─ 3. 并发安全
│  └─ FileOperationLock机制
└─ 4. 安全检查
   └─ 路径边界检查

任务11.3：Sandbox工具 (1.5小时)
├─ bash (禁用LocalSandbox)
├─ ls
├─ read_file
├─ write_file
└─ str_replace (重点)

任务11.4：测试Sandbox (1小时)
├─ 1. 测试路径映射
├─ 2. 测试文件操作
├─ 3. 测试并发安全
└─ 4. 测试安全检查

检验标准：
✓ 能创建LocalSandbox实例
✓ 虚拟路径正确映射
✓ str_replace正确工作
✓ 并发操作安全
```

### 第12天：工具和子Agent系统

#### 目标
实现工具注册系统和子Agent委托。

#### 任务清单

```
任务12.1：工具注册系统 (1.5小时)
├─ 1. 定义Tool数据结构
├─ 2. 工具注册到Agent
├─ 3. 系统提示词中声明工具
└─ 4. LLM工具选择和调用

任务12.2：内置工具 (1.5小时)
├─ present_files (智能展示)
├─ ask_clarification (澄清请求)
└─ view_image (图像加载)

任务12.3：子Agent执行器 (1小时)
├─ 1. SubagentExecutor设计
├─ 2. ThreadPool并发执行
├─ 3. 超时控制
└─ 4. 结果汇总

任务12.4：测试工具和子Agent (1小时)
├─ 1. 工具执行测试
├─ 2. 子Agent并发测试
└─ 3. 超时处理测试

检验标准：
✓ 能调用工具并获得结果
✓ 子Agent并发运行(最多3个)
✓ 超时正确处理
```

### 第13天：网关API + 模型系统

#### 目标
实现FastAPI网关和模型工厂。

#### 任务清单

```
任务13.1：模型工厂 (1.5小时)
├─ 1. 模型配置定义
├─ 2. 模型工厂创建模型
├─ 3. 能力声明
└─ 4. 动态模型选择

任务13.2：FastAPI网关框架 (0.5小时)
├─ 1. 创建FastAPI应用
├─ 2. 路由组织
└─ 3. CORS配置

任务13.3：关键API路由 (2小时)
├─ /api/models - 模型管理
├─ /api/threads/{id}/uploads - 文件上传
├─ /api/threads/{id} - 线程清理
├─ /api/threads/{id}/artifacts - 工件管理
└─ /api/skills - 技能列表

任务13.4：测试API (1小时)
├─ 1. 模型API测试
├─ 2. 上传API测试
├─ 3. 工件API测试
└─ 4. 集成测试

检验标准：
✓ FastAPI能启动
✓ 所有路由可访问
✓ 数据格式正确
```

### 第14天：测试、集成和打磨

#### 目标
完整的单元测试、集成测试和系统完善。

#### 任务清单

```
任务14.1：单元测试覆盖 (2小时)
├─ ThreadState测试
├─ 中间件测试
├─ Sandbox测试
├─ 工具测试
└─ 模型测试

任务14.2：集成测试 (1小时)
├─ 完整Agent流程测试
├─ 文件上传到处理
└─ 子Agent执行

任务14.3：端到端测试 (1小时)
├─ API调用测试
├─ Web流程模拟
└─ 异常恢复

任务14.4：代码质量 (1小时)
├─ 代码风格检查: ruff check
├─ 类型检查: mypy (可选)
├─ 文档补充
└─ 性能优化

检验标准：
✓ 测试覆盖率 >70%
✓ 所有测试通过
✓ 代码风格符合ruff
✓ 能独立启动并运行
```

---

## 总体进度检查表

### 学习阶段 (Day 1-7)

- [ ] Day 1: 项目概览、架构、技术栈、本地启动
- [ ] Day 2: LangGraph基础、ThreadState、中间件链
- [ ] Day 3: Sandbox系统、虚拟路径、文件操作、安全
- [ ] Day 4: 工具系统、内置工具、子Agent、MCP集成
- [ ] Day 5: 内存系统、技能系统
- [ ] Day 6: 模型工厂、网关API
- [ ] Day 7: 配置系统、错误处理、部署、测试

### 实践阶段 (Day 8-14)

- [ ] Day 8: 基础框架搭建 (ThreadState + 最小Agent)
- [ ] Day 9-10: 中间件链完整实现 (9个中间件 + 集成)
- [ ] Day 11: Sandbox系统 (本地提供商 + 工具)
- [ ] Day 12: 工具和子Agent系统
- [ ] Day 13: 网关API + 模型系统
- [ ] Day 14: 测试和打磨

---

## 学习资源汇总

### 官方文档
- [ ] LangGraph官方文档: https://langchain-ai.github.io/langgraph/
- [ ] FastAPI官方文档: https://fastapi.tiangolo.com/
- [ ] LangChain官方文档: https://python.langchain.com/

### DeerFlow文档
- [ ] `backend/README.md`
- [ ] `backend/CLAUDE.md`
- [ ] `backend/docs/ARCHITECTURE.md`
- [ ] `backend/docs/middleware-execution-flow.md`
- [ ] `backend/docs/MEMORY_IMPROVEMENTS.md`

### 源代码重点
```
最重要 (必读):
├─ agents/lead_agent/agent.py
├─ agents/thread_state.py
├─ agents/middlewares/
├─ sandbox/sandbox.py
└─ tools/tools.py

重要 (应读):
├─ sandbox/local/
├─ subagents/executor.py
├─ models/
├─ app/gateway/app.py
└─ tests/

参考 (可选):
├─ skills/
├─ mcp/
└─ community/
```

### 推荐学习顺序
1. **概念理解** → 阅读backendclaude.md和官方文档
2. **源代码学习** → 从lead_agent/agent.py开始，逐个模块深入
3. **本地调试** → 使用make dev启动，修改代码观察行为
4. **单元测试** → 查看backend/tests/下的测试用例学习最佳实践
5. **动手实现** → 从头开始重写项目，不参考原代码

---

## 常见卡点和解决方案

### 卡点1: LangGraph的执行流程理解困难

**现象**：不明白StateGraph是如何执行的，工具调用循环如何工作。

**解决方案**：
1. 从LangGraph官方教程开始，完成3个简单demo
2. 用print()调试：在每个节点中打印state
3. 使用`stream()`而不是`invoke()`，看中间状态

### 卡点2: ThreadState的字段太多

**现象**：记不住所有字段的含义和用途。

**解决方案**：
1. 创建一个表格，列举字段名→用途→由哪个中间件设置
2. 通过代码跟踪：字段从哪里来，流向何处
3. 画一个信息流图

### 卡点3: 虚拟路径映射的实现

**现象**：如何将/mnt/user-data/workspace映射到真实路径。

**解决方案**：
1. 看LocalSandbox的resolve_path()实现
2. 手动测试：创建sandbox，写文件，检查真实位置
3. 理解为什么需要映射（安全和隔离）

### 卡点4: 中间件顺序为什么不能改

**现象**：为什么某个中间件必须在另一个之后执行？

**解决方案**：
1. 看中间件的输入输出
2. 绘制依赖图：谁依赖谁的输出
3. 尝试改变顺序，观察哪里出错

### 卡点5: 子Agent并发执行的复杂性

**现象**：如何正确处理多个子Agent同时运行？

**解决方案**：
1. 用ThreadPoolExecutor或asyncio简单例子热身
2. 看test_subagents.py的测试用例
3. 自己写一个简单的并发任务队列

### 卡点6: API设计中的职责分离

**现象**：为什么某个功能在Gateway中而不在LangGraph中？

**解决方案**：
1. 思考：这个功能是"处理Agent状态"还是"管理系统资源"
2. 前者 → LangGraph，后者 → Gateway
3. 看现有的分离案例

---

## 自我评估标准

### Day 7结束时
- [ ] 能用一页纸说清楚整个系统架构
- [ ] 能指出9个中间件的顺序和作用
- [ ] 能解释虚拟路径隔离的好处
- [ ] 能说出5个关键设计决策和原因
- [ ] 能画出ThreadState的信息流图

### Day 14结束时
- [ ] 能从零开始搭建完整的后端项目
- [ ] 所有单元测试覆盖 >80%
- [ ] 能启动本地环境，Web功能正常
- [ ] 能添加一个新的工具、中间件、子Agent
- [ ] 代码能通过ruff检查和手动review

---

## 继续深化的方向

完成14天学习后，如果还想继续深化：

1. **优化性能**：
   - 添加缓存层
   - 异步I/O优化
   - 消息压缩

2. **扩展功能**：
   - 自定义中间件
   - 新的沙箱提供商（SSH, K8s）
   - 新的工具集成

3. **企业特性**：
   - 多用户和权限管理
   - 审计日志
   - 成本控制和速率限制

4. **研究方向**：
   - 记忆系统优化
   - Agent协作模式
   - 安全和隐私

---

**预期学习成果**：
- 深度理解Agent系统设计
- 掌握LangGraph生产级应用
- 能设计和实现复杂的系统架构
- 提升Python高级编程能力
- 为LLM应用开发打下坚实基础

**时间投入**：约70-100小时
**建议进度**：每天4-6小时，持续14天

---

**文档生成日期**：2025-04-19  
**版本**：1.0  
**作者**：DeerFlow学习计划

