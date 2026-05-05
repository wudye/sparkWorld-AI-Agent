# 🎯 DeerFlow 学习快速参考卡

> 打印这个文件，贴在你的电脑旁边。在学习和实践中随时查看。

---

## 快速事实表

### DeerFlow是什么？
```
超级Agent框架 (Super Agent Harness)
= LangGraph + FastAPI + Sandbox + 内存 + 工具生态
用途：构建生产级的AI Agent系统
```

### 核心特性 (3个)
```
1. Per-thread隔离 → 每个会话完全独立
2. 虚拟路径系统 → Agent无法逃逸沙箱
3. 异步内存系统 → 跨会话知识保留
```

### 4层架构
```
┌──────────────────────────┐
│   Nginx反向代理 (2026)    │ ← 统一入口
├──────────────────────────┤
│ LangGraph (2024) │ Gateway (8001) │ ← 后端核心
├──────────────────────────┤
│ 模块库 + 配置 + 存储      │ ← 支撑层
├──────────────────────────┤
│ 文件系统 + Docker + DB    │ ← 基础设施
└──────────────────────────┘
```

### 9个中间件（执行顺序）
```
1. ThreadDataMiddleware      → 创建隔离目录
2. UploadsMiddleware         → 处理上传文件
3. SandboxMiddleware         → 获取沙箱
4. SummarizationMiddleware   → 压缩上下文
5. TodoListMiddleware        → 追踪任务
6. TitleMiddleware           → 生成标题
7. MemoryMiddleware          → 异步提取记忆
8. ViewImageMiddleware       → 加载图像
9. ClarificationMiddleware   → 请求澄清(最后)
```

### ThreadState关键字段
```
messages: list[BaseMessage]    ← 消息历史
sandbox: dict                  ← 沙箱配置
thread_data: dict              ← 隔离目录
artifacts: list[str]           ← 生成文件
title: str | None              ← 对话标题
todos: list[dict]              ← 任务列表
viewed_images: dict            ← 图像数据
```

---

## 虚拟路径映射

### 路径转换规则
```
虚拟路径                        物理路径
/mnt/user-data/workspace/  →  /threads/{id}/workspace/
/mnt/user-data/uploads/    →  /threads/{id}/uploads/
/mnt/user-data/outputs/    →  /threads/{id}/outputs/
/mnt/skills/               →  /opt/deerflow/skills/
```

### 为什么需要？
```
✓ 防止目录穿越攻击
✓ 隐藏系统架构
✓ 支持灵活的存储后端
✓ 多用户隔离
```

---

## Sandbox隔离方式

### LocalSandbox (开发环境)
```
虚拟路径转换 → 文件系统权限
✓ 快速 (无开销)
✗ bash工具禁用
✗ 多用户隔离弱
```

### AioSandbox (生产环境)
```
Docker Volume挂载 → 容器隔离执行
✓ 完全进程隔离
✓ 支持任何bash命令
✓ 容器销毁后无痕迹
✗ 启动慢 (500ms-2s)
```

### Docker隔离原理
```
即使Agent执行：rm -rf /
也只删除容器内的文件
主机文件系统完全安全 ✓
```

---

## 常用命令

### 开发环境
```bash
make check              # 检查工具链
make install           # 安装依赖
make dev               # 启动所有服务
make stop              # 停止所有服务
```

### 后端操作
```bash
cd backend

make lint              # 代码检查
make test              # 运行测试
make serve             # 启动LangGraph
```

### 前端操作
```bash
cd frontend

pnpm lint              # 代码检查
pnpm typecheck         # 类型检查
BETTER_AUTH_SECRET=x pnpm build  # 生产构建
```

---

## 端口分配

```
LangGraph Server    →  2024
Gateway API         →  8001
Frontend Dev        →  3000
Nginx (统一入口)    →  2026
Provisioner (可选)  →  8002
```

---

## 关键概念速查

### ThreadState流转
```
用户输入
  ↓
[中间件链修改]
  ↓
Agent节点处理
  ↓
[工具调用]
  ↓
LLM响应
  ↓
返回给用户
```

### 工具执行循环
```
LLM生成ToolCall
  ↓
执行工具获得结果
  ↓
将结果回复给LLM
  ↓
LLM继续推理
  ↓
直到返回消息(不是ToolCall)
```

### 子Agent执行
```
主Agent: task(description, agent_type)
  ↓
异步提交到ThreadPool
  ↓
返回立即 (不等待)
  ↓
前端通过SSE看到进度
  ↓
子Agent完成后返回结果
  ↓
主Agent继续
```

---

## 常见错误快速诊断

### 问题：Agent找不到工具
**检查**：
1. 工具是否加入tools列表？
2. 工具是否在系统提示词中声明？
3. 工具的参数schema是否正确？

### 问题：文件操作失败
**检查**：
1. 虚拟路径是否正确？(应以/mnt/开头)
2. 目录是否存在？(需要先创建)
3. 权限是否正确？

### 问题：中间件顺序错误
**检查**：
1. 不能改变中间件顺序
2. ThreadData必须第一个
3. Clarification必须最后

### 问题：内存提取不工作
**检查**：
1. 内存系统是否启用？(config中)
2. 是否有足够的对话内容？
3. 异步队列是否消费？

### 问题：Sandbox权限被拒
**检查**：
1. 是否尝试访问/mnt/外的路径？
2. 是否尝试执行危险命令？(LocalSandbox禁bash)
3. 使用AioSandbox了吗？

---

## 调试技巧

### 打印ThreadState
```python
import json
print(json.dumps({
    "messages": len(state.messages),
    "sandbox": state.sandbox,
    "thread_data": state.thread_data,
    "artifacts": state.artifacts,
    "title": state.title
}, indent=2))
```

### 跟踪中间件执行
```python
# 在每个中间件中添加日志
logger.info(f"Before {middleware_name}: {len(state.messages)} messages")
# 执行中间件
logger.info(f"After {middleware_name}: {len(state.messages)} messages")
```

### 查看工具调用
```python
# 在agent_node中打印
for message in state.messages[-5:]:
    if message.tool_calls:
        print(f"Tool: {message.tool_calls[0].name}")
        print(f"Args: {message.tool_calls[0].args}")
```

### 检查虚拟路径映射
```python
sandbox = state.sandbox['instance']
virtual_path = '/mnt/user-data/workspace/file.txt'
physical_path = sandbox.resolve_path(virtual_path)
print(f"Virtual: {virtual_path}")
print(f"Physical: {physical_path}")
```

---

## 14天学习节奏

### 第1周：理论 (每天5小时)
```
Day 1: 项目概览 + 架构 + 本地启动
Day 2: LangGraph + ThreadState + 中间件
Day 3: Sandbox隔离机制
Day 4: 工具系统 + 子Agent
Day 5: 内存系统 + 技能系统
Day 6: 模型工厂 + 网关API
Day 7: 配置 + 错误 + 部署 + 测试
```

### 第2周：实践 (每天6小时)
```
Day 8:  基础框架 (ThreadState + 最小Agent)
Day 9-10: 中间件链 (9个中间件完整实现)
Day 11: Sandbox系统 (LocalSandbox + 工具)
Day 12: 工具和子Agent系统
Day 13: 网关API + 模型系统
Day 14: 测试 + 集成 + 打磨
```

---

## 代码框架快速参考

### ThreadState定义
```python
from langgraph.graph import GraphState
from typing import Annotated

class ThreadState(GraphState):
    messages: Annotated[list, ...] = []
    sandbox: dict = {}
    thread_data: dict = {}
    artifacts: list[str] = []
    title: str | None = None
    todos: list[dict] = []
    viewed_images: dict = {}
```

### 中间件基类
```python
class BaseMiddleware(ABC):
    @abstractmethod
    def __call__(self, state: ThreadState) -> ThreadState:
        pass

class MyMiddleware(BaseMiddleware):
    def __call__(self, state: ThreadState) -> ThreadState:
        # 修改state
        return state
```

### 工具定义
```python
from langchain.tools import tool

@tool(name="my_tool")
def my_tool(param: str) -> str:
    """工具说明"""
    return result

# 加入tools列表
tools = [existing_tool1, my_tool, ...]
```

---

## 测试模板

### 单元测试
```python
import pytest

def test_middleware():
    state = ThreadState(messages=[])
    middleware = MyMiddleware()
    result = middleware(state)
    assert result.thread_data != {}

@pytest.mark.asyncio
async def test_agent():
    agent = make_lead_agent(test_config)
    result = await agent.ainvoke({"messages": [...]})
    assert result["success"]
```

---

## 性能检查清单

- [ ] ThreadState的消息列表是否太长？(考虑SummarizationMiddleware)
- [ ] 子Agent是否超过3个？(限制为max_workers=3)
- [ ] Sandbox操作是否频繁？(考虑缓存)
- [ ] LLM调用是否太多？(考虑缓存响应)
- [ ] 内存提取是否堵塞？(应该异步)

---

## 生产检查清单

- [ ] 所有API都有认证吗？
- [ ] Sandbox是否使用Docker隔离？
- [ ] 日志是否记录了关键操作？
- [ ] 错误是否被妥善处理？
- [ ] 测试覆盖率是否>70%？
- [ ] 代码是否通过ruff检查？
- [ ] 性能是否满足SLA？
- [ ] 安全审计通过了吗？

---

## 重要链接

### 官方文档
- LangGraph: https://langchain-ai.github.io/langgraph/
- FastAPI: https://fastapi.tiangolo.com/
- Docker: https://docs.docker.com/

### 本项目文档
- 后端分析报告: backendclaude.md
- 14天学习计划: learning_plan_14days.md
- Sandbox深度解析: sandbox_detailed_analysis.md
- 资源导航: README_LEARNING_RESOURCES.md
- 快速索引: INDEX.md (本文件)

---

## 关键文件位置

```
后端核心包：backend/packages/harness/deerflow/
  agents/          → Agent和中间件
  sandbox/         → Sandbox系统
  tools/           → 工具定义
  subagents/       → 子Agent
  models/          → 模型工厂
  mcp/             → MCP集成
  skills/          → 技能加载
  config/          → 配置系统

网关API：backend/app/gateway/
  app.py           → FastAPI应用
  routers/         → API路由

测试：backend/tests/
  test_*.py        → 测试用例

配置文件：
  config.yaml      → 主配置
  extensions_config.json → MCP和技能
  langgraph.json   → LangGraph入口
```

---

## 15秒速记

**记住这个就够了**：
```
DeerFlow = 
  LangGraph (Agent编排) 
  + FastAPI (API网关)
  + Sandbox (隔离执行)
  + 内存 (知识保留)
  + 工具生态 (功能扩展)

中间件链 → 修改ThreadState → LLM处理 → 返回

虚拟路径 → 防止逃逸 → 安全隔离

Docker容器 → 恶意命令无损 → 生产安全
```

---

## 一页纸的DeerFlow

```
DeerFlow是一个AI Agent框架。

用户发送消息 → 
中间件修改ThreadState (注入文件、初始化沙箱等) →
LLM处理 (可调用工具) →
Sandbox隔离执行 (虚拟路径映射到真实目录) →
可选调用子Agent (异步并行×3) →
内存系统记录对话 (后续注入提示词) →
返回给用户

关键设计：
1. Per-thread隔离 (用户数据完全分离)
2. 虚拟路径 (防止逃逸)
3. 中间件链 (清晰的职责分离)
4. 异步内存 (不阻塞主流程)
```

---

## 打印建议

**推荐打印**：
- [ ] 这个文件 (快速参考卡)
- [ ] INDEX.md (快速导航)

**打印后**：
- 贴在电脑旁边
- 学习时随时查看
- 用荧光笔标记重点

---

**参考卡生成日期**：2025-04-19  
**用途**：随时随地快速查阅  
**最佳使用场景**：学习中卡住时、快速复习时、考试前冲刺时

