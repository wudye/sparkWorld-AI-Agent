# 第2天：LangGraph和中间件链深度学习

**学习日期**：Day 2  
**预计投入**：5-6小时  
**难度等级**：⭐⭐⭐ (中等)

---

## 📚 学习目标

理解LangGraph基础和DeerFlow的中间件设计模式。

**关键成果**：
- ✅ 理解LangGraph基础概念和执行模型
- ✅ 掌握ThreadState设计思想
- ✅ 完整理解9个中间件的功能和顺序
- ✅ 理解中间件链集成机制
- ✅ 能手动创建简单的中间件

---

## 📋 任务清单

### 任务2.1：学习LangGraph基础（1.5小时）

**学习内容**：

**1. StateGraph概念**
- 图中的节点 (node)
- 图中的边 (edge)
- 条件边 (conditional_edge)
- 状态对象 (state)

**2. 执行流程**
- invoke() 同步执行
- ainvoke() 异步执行
- stream() 流式执行

**3. 检查点机制**
- Checkpointer接口
- 暂停/恢复

**实践代码**：

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

**检验方式**：
- 建立一个3节点的StateGraph
- 使用stream()查看中间状态
- 从检查点恢复一次执行

**学习记录**：
```
StateGraph的5个关键概念：
1. ________________________________________
2. ________________________________________
3. ________________________________________
4. ________________________________________
5. ________________________________________

3个执行方式对比：
invoke()   → _________________________________
ainvoke()  → _________________________________
stream()   → _________________________________

检查点的作用：
_____________________________________________
```

---

### 任务2.2：理解DeerFlow的ThreadState设计（1小时）

**阅读材料**：
```
✓ backend/packages/harness/deerflow/agents/thread_state.py (完整)
✓ backendclaude.md 第2.1.3节
```

**分析重点**：

**1. ThreadState vs AgentState**
- 继承关系
- 扩展字段

**2. 核心字段用途**
- messages: LangGraph标准消息历史
- sandbox: 隔离执行环境信息
- artifacts: 生成的文件
- thread_data: 隔离目录路径
- title: 自动生成的标题
- todos: 任务追踪
- viewed_images: 视觉模型图像

**3. 为什么这样设计？**
- 每个字段对应一个系统功能
- 字段修改由中间件驱动

**代码练习**：
```python
# 创建ThreadState实例
from deerflow.agents.thread_state import ThreadState

state = ThreadState(
    messages=[],
    sandbox={'provider': 'local', 'id': 'thread_123'},
    artifacts=[],
    thread_data={...},
    ...
)
```

**ThreadState字段分析**：
```
字段名           │ 类型          │ 用途
───────────────┼──────────────┼─────────────────
messages       │ list         │ _______________
sandbox        │ dict         │ _______________
artifacts      │ list[str]    │ _______________
thread_data    │ dict         │ _______________
title          │ str|None     │ _______________
todos          │ list[dict]   │ _______________
viewed_images  │ dict         │ _______________
```

**检验方式**：
- 解释ThreadState的5个核心字段
- ThreadState流经所有中间件，最后传给LLM，这样设计的好处是？

---

### 任务2.3：深入学习中间件链（2小时）

**阅读材料**：
```
✓ backend/packages/harness/deerflow/agents/middlewares/*.py (逐个文件)
✓ backendclaude.md 第2.1.2节
✓ backend/docs/middleware-execution-flow.md
```

**分析每个中间件**：

| # | 中间件名 | 功能 | 输入 | 输出 |
|---|----------|------|------|------|
| 1 | ThreadDataMiddleware | 创建隔离目录 | thread_id | state.thread_data |
| 2 | UploadsMiddleware | 处理上传文件 | 文件路径 | state.messages |
| 3 | SandboxMiddleware | 获取沙箱环境 | 配置 | state.sandbox |
| 4 | SummarizationMiddleware | 压缩上下文 | messages | messages(压缩) |
| 5 | TodoListMiddleware | 追踪任务 | LLM输出 | state.todos |
| 6 | TitleMiddleware | 生成标题 | 消息 | state.title |
| 7 | MemoryMiddleware | 异步提取 | 对话 | (无修改) |
| 8 | ViewImageMiddleware | 加载图像 | 图像路径 | state.viewed_images |
| 9 | ClarificationMiddleware | 请求澄清 | 标记 | 提前返回 |

**深度分析：每个中间件完成以下内容**

**1️⃣ ThreadDataMiddleware**
```
功能：为每个thread创建隔离目录
关键实现：
- 使用什么库创建目录？
  答：_______________________________
- 创建哪些目录？
  答：_______________________________
```

**2️⃣ UploadsMiddleware**
```
功能：处理用户上传文件，注入到消息
关键实现：
- 如何避免重复处理同一文件？
  答：_______________________________
- 文件如何注入到messages？
  答：_______________________________
```

**3️⃣ SandboxMiddleware**
```
功能：获取/初始化Sandbox环境
关键实现：
- LocalSandbox vs AioSandbox的区别？
  答：_______________________________
- 如何选择提供商？
  答：_______________________________
```

**4️⃣ SummarizationMiddleware**
```
功能：当token接近上限时，压缩对话历史
关键实现：
- 如何评估token数？
  答：_______________________________
- 调用哪个LLM进行总结？
  答：_______________________________
```

**5️⃣ TodoListMiddleware**
```
功能：在plan_mode下追踪任务列表
关键实现：
- 如何从自由文本中提取结构化任务？
  答：_______________________________
- 任务列表如何更新？
  答：_______________________________
```

**6️⃣ TitleMiddleware**
```
功能：首次对话后自动生成标题
关键实现：
- 调用LLM生成标题的提示词是什么？
  答：_______________________________
- 何时生成标题（第几条消息）？
  答：_______________________________
```

**7️⃣ MemoryMiddleware**
```
功能：将对话加入异步提取队列
关键实现：
- 如何保证不丢失任务？
  答：_______________________________
- 持久化到哪？
  答：_______________________________
```

**8️⃣ ViewImageMiddleware**
```
功能：为视觉模型加载图像数据
关键实现：
- 如何处理大图像？
  答：_______________________________
- 如何转换为base64？
  答：_______________________________
```

**9️⃣ ClarificationMiddleware**
```
功能：拦截澄清请求
关键实现：
- 为什么要放在最后？
  答：_______________________________
- 如何中断执行？
  答：_______________________________
```

**代码深入**：
```python
# 打开middlewares/thread_data.py，逐行理解：
class ThreadDataMiddleware(BaseMiddleware):
    def __call__(self, state: ThreadState) -> ThreadState:
        # 第1步：读取thread_id
        # 第2步：创建目录结构
        # 第3步：更新state.thread_data
        # 第4步：返回修改后的state
        ...
```

**检验方式**：
- [ ] 用表格总结9个中间件的输入、输出、功能
- [ ] 中间件执行顺序能否改变？为什么？
- [ ] 如何调试一个中间件？
- [ ] 如何新增一个中间件（例如：自定义上下文注入中间件）？

---

### 任务2.4：理解中间件链集成（1小时）

**阅读材料**：
```
✓ backend/packages/harness/deerflow/agents/lead_agent/agent.py
  - 特别关注make_lead_agent函数中的middleware应用
```

**理解流程**：

**1. 中间件链的构建**
```python
middleware_chain = [
    ThreadDataMiddleware(...),
    UploadsMiddleware(...),
    SandboxMiddleware(...),
    # ... 其他中间件
]
```

**2. 中间件链如何集成到Agent**
- StateGraph中的pre_process_state
- 或者Runnable包装

**3. 执行顺序**
- 每个middleware.__call__()依次调用
- ThreadState依次流经每个中间件

**代码练习**：
```python
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
```

**检验方式**：
- [ ] 描述ThreadState如何流经中间件链
- [ ] 如何调试整个链？
- [ ] 如果某个中间件抛异常，如何处理？

**集成分析**：
```
中间件集成的3个关键步骤：
1. _____________________________________
2. _____________________________________
3. _____________________________________

ThreadState流转流程：
input → middleware1 → middleware2 → ... → LLM → output
        ↓            ↓
        state修改    state修改
```

---

## ✅ 第2天检验清单

**代码理解**：
- [ ] 能创建一个StateGraph
- [ ] 能解释stream()和invoke()的区别
- [ ] 能指出ThreadState的核心字段
- [ ] 能列举9个中间件的顺序
- [ ] 能解释某个中间件的功能

**实践操作**：
- [ ] 创建了3节点的StateGraph ✓
- [ ] 运行了stream()查看中间状态 ✓
- [ ] 创建了一个简单的中间件 ✓

**理论题**：
```
1. 中间件执行顺序能否改变？
   答：_________________________________
   
2. 为什么ThreadState必须流经所有中间件？
   答：_________________________________
   
3. 哪个中间件调用了LLM？
   答：_________________________________
   
4. 为什么SummarizationMiddleware要在SandboxMiddleware之后？
   答：_________________________________
```

---

## 🎓 Day 2总结

**学到的最重要的3件事**：
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

**还需要进一步理解的**：
1. _____________________________________________
2. _____________________________________________

**Tomorrow计划**：
- [ ] 准备深入学习Sandbox
- [ ] 阅读虚拟路径映射相关文档
- [ ] 理解LocalSandbox实现

---

**Day 2 完成时间**：_____________  
**代码练习完成**：✓ / ✗  
**理解程度评分** (1-10)：_____  

**下一步行动**：开始Day 3的Sandbox深度学习

---

**文档版本**：1.0  
**最后更新**：2025-04-19

