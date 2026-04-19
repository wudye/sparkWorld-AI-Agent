这份**14天实战学习计划**旨在带你从零开始，按模块逐步构建出 DeerFlow 后端。计划的原则是：**先通主流程，再加固可靠性，最后拓展高级特性**。

每天的学习分为**源码阅读**和**动手复刻**两部分。建议你在本地新建一个空项目（比如 `my-deerflow`），每天完成设定的独立目标。

---

# 🦌 DeerFlow 后端 14天从零复刻实战计划

## 阶段一：基础设施与骨架搭建（Day 1-4）
*目标：搭好项目工程结构，能启动 FastAPI，能动态加载 LLM 模型，并建立基础的沙箱文件管理。*

### Day 1：工程脚手架与配置中心
- **阅读源码**：`pyproject.toml`, `backend/Makefile`, `backend/packages/harness/deerflow/config/app_config.py`
- **复刻任务**：
  1. 使用 `uv` 初始化空项目并配置 dependencies（参考 `pyproject.toml`）。
  2. 实现一个基于 Pydantic 的 `AppConfig` 类。
  3. 实现配置的单例加载、环境变量替换（例如解析 `$OPENAI_API_KEY`）。
- **今日产出**：一个能通过 `AppConfig.from_file()` 正确读取 `config.yaml` 的基础环境。

### Day 2：FastAPI 网关与依赖注入
- **阅读源码**：`backend/app/gateway/app.py`, `backend/app/gateway/deps.py`, `backend/app/gateway/routers/models.py`
- **复刻任务**：
  1. 搭建 FastAPI 基础框架，配置 lifespan 生命周期。
  2. 实现 `/health` 和简单的 `/api/models` 路由。
  3. 创建依赖注入模块（`deps.py`），学会如何在 `app.state` 上挂载全局单例并被路由提取。
- **今日产出**：可以通过 `uvicorn` 启动的 API 网关，并能成功访问健康检查。

### Day 3：模型工厂（Model Factory）与反射
- **阅读源码**：`backend/packages/harness/deerflow/models/factory.py`, `backend/packages/harness/deerflow/reflection/`
- **复刻任务**：
  1. 实现反射加载器 `resolve_class`，支持根据字符串（如 `langchain_openai:ChatOpenAI`）导入类。
  2. 编写 `create_chat_model` 工具函数，解析配置并实例化 LangChain 的 ChatModel。
  3. 增加对 `thinking_enabled` 标志的处理逻辑（比如组装 `reasoning_effort` 参数）。
- **今日产出**：给出一个简单的脚本，能通过读取配置调用 `create_chat_model()` 成功向 OpenAI/Claude 发送一句 "Hello" 并打印回复。

### Day 4：路径隔离与沙箱抽象（Sandbox）
- **阅读源码**：`backend/packages/harness/deerflow/config/paths.py`, `backend/packages/harness/deerflow/sandbox/sandbox_provider.py`
- **复刻任务**：
  1. 编写 `Paths` 类，管理 `{base_dir}/threads/{thread_id}/user-data/...` 的生成与校验。
  2. 实现基于 `Abstract Sandbox` 的 `LocalSandboxProvider`。
  3. 编写虚拟路径 `<->` 真实宿主机路径的映射逻辑函数。
- **今日产出**：给定一个线程 ID，程序能自动创建隔离目录，并能成功拦截尝试访问上层目录（路径穿越）的非法操作。

---

## 阶段二：Agent 引擎与中间件组装（Day 5-8）
*目标：把模型、工具、提示词与 LangGraph 结合，并通过中间件保障运行时的健壮性。*

### Day 5：基础工具实现（Tools）
- **阅读源码**：`backend/packages/harness/deerflow/sandbox/tools.py`
- **复刻任务**：
  1. 基于 `@tool` 装饰器实现 `read_file` 和 `write_file` 工具。
  2. 接入昨日的 Sandbox 路径映射，确保工具只能读写该线程的 `workspace`。
  3. **细节点**：实现同一文件的读写锁防止并发竞争。
- **今日产出**：一套安全的、只能在受限目录内操作的文件工具集。

### Day 6：组装 Lead Agent（LangGraph 核心）
- **阅读源码**：`backend/packages/harness/deerflow/agents/lead_agent/agent.py`, `thread_state.py`, `backend/langgraph.json`
- **复刻任务**：
  1. 定义 `ThreadState` 的 TypedDict（集成 messages, artifacts 等）。
  2. 搭建系统提示词模板，注入当前的时间、能力限制。
  3. 使用 `create_agent` 将模型和昨天写的工具组装成一个可运行的 Agent 图。
- **今日产出**：一个纯后端的脚本，实例化 Agent，输入“帮我写一个 python 脚本保存为 hello.py”，Agent 成功调用工具并完成文件落盘。

### Day 7：中间件开发 - 基础层
- **阅读源码**：`backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`, `sandbox_middleware.py`
- **复刻任务**：
  1. 学习并实现 `AgentMiddleware` 的基类接口。
  2. 编写 `ToolErrorHandlingMiddleware`：捕获工具执行抛出的异常，转化成包含错误信息的 `ToolMessage` 返回给模型。
  3. 编写 `ThreadDataMiddleware` / `SandboxMiddleware` 注入隔离环境 ID。
- **今日产出**：故意触发一个工具报错（比如读取不存在的文件），Agent 不会崩溃退出，而是根据返回的错误 ToolMessage 做出修正回应。

### Day 8：中间件开发 - 进阶业务
- **阅读源码**：`loop_detection_middleware.py`, `dangling_tool_call_middleware.py`
- **复刻任务**：
  1. 实现无限循环检测中间件 `LoopDetectionMiddleware`（当模型连续多次同参数调用同一工具时强行中断）。
  2. 结合图状态处理，学习如何在 `after_agent` 函数中审查模型的输出并修改。
- **今日产出**：构造一个会让普通 Agent 死循环的场景，验证你的中间件能成功拦截。

---

## 阶段三：后端管控与复杂能力（Day 9-11）
*目标：通过 Gateway 暴露 API，管理多线程对话流，并实现子系统调用。*

### Day 9：Gateway 线程与流式执行 API
- **阅读源码**：`backend/app/gateway/routers/thread_runs.py`, `backend/packages/harness/deerflow/runtime/runs/manager.py`
- **复刻任务**：
  1. 在 FastAPI 中实现 `/api/threads/{thread_id}/runs/stream`。
  2. 实现 `RunManager` 以追踪当前正在运行的异步任务，支持多任务策略（如 `reject`, `interrupt`）。
  3. 将 LangGraph 的事件流通过 SSE（Server-Sent Events）格式推送给客户端。
- **今日产出**：可以通过 cURL 或 Postman 向 API 发送请求，并持续看到 `yield` 出来的事件流。

### Day 10：文件上传与伪造 Artifacts 下载
- **阅读源码**：`backend/app/gateway/routers/uploads.py`, `artifacts.py`
- **复刻任务**：
  1. 编写文件上传接口，接收文件并存入对应线程的 `uploads` 目录下。
  2. 实现从 `outputs` 目录读取文件的 API `/artifacts/{path}`。
  3. **安全重点**：编写 MIME 检查逻辑，当检测到 HTML/SVG 格式时，强制返回 `Content-Disposition: attachment` 而不是 inline（防止 XSS）。
- **今日产出**：通过 API 上传文件，让 Agent 读取并处理，然后通过 Artifact API 下载处理后的文件。

### Day 11：并发子代理 Subagent 系统
- **阅读源码**：`backend/packages/harness/deerflow/subagents/executor.py`, `backend/packages/harness/deerflow/tools/builtins/task_tool.py`
- **复刻任务**：
  1. 实现 `task_tool` 并暴露给主 Agent。
  2. 编写 `SubagentExecutor`：在新线程的独立事件循环中启动一个新的 LangGraph Agent 实例。
  3. 让子任务执行时，能将状态写回共享字典中；主 Agent （基于 `task_tool` 内的轮询或 SSE emit）可感知进度。
- **今日产出**：命令主 Agent "启动两个背景任务分别调研 A 和 B"，主 Agent 成功委派任务并在后台并行执行。

---

## 阶段四：拓展生态与打磨（Day 12-14）
*目标：攻克记忆系统和插件协议，打通完整产品体验。*

### Day 12：长期记忆（Memory）抽取与队列
- **阅读源码**：`backend/packages/harness/deerflow/agents/memory/queue.py`, `updater.py`
- **复刻任务**：
  1. 编写一个带 debounce（防抖）的队列：收到对话结束信号后，等待 N 秒再去触发总结。
  2. 编写 Memory Prompt，将这轮对话传递给廉价模型提取 Facts（事实）。
  3. 将总结好的长记忆存储并注入到下一轮 Lead Agent 的 System Prompt 中。
- **今日产出**：与 Agent 交代“我叫张三”，结束对话；开启一个新线程，直接问“我是谁”，Agent 能回答上来。

### Day 13：扩展 MCP 与 Skills
- **阅读源码**：`backend/packages/harness/deerflow/mcp/cache.py`, `backend/packages/harness/deerflow/skills/loader.py`
- **复刻任务**：
  1. 编写 Skills loader，从本地目录扫描 `SKILL.md`（包括提取 YAML Frontmatter 和工具声明）。
  2. 使用 `langchain-mcp-adapters` 集成一个现成的 MCP Server（如 file-system 或 github）。
  3. 动态将这些扩展工具并入 `get_available_tools()` 列表。
- **今日产出**：配置好一个 MCP Server 后，Agent 能直接调用 MCP Server 提供的工具。

### Day 14：回顾、测试与重构
- **阅读源码**：`backend/tests/` 下的各类测试用例。
- **复刻任务**：
  1. 撰写边界测试：验证 Harness 是否无意间引用了 Gateway（App） 的模块。
  2. 编写 Sandbox 安全性单例测试，传入包含 `../../../` 的恶意路径看是否被成功拦截。
  3. 跑通全链路，修复自己复刻过程中留下的 FIXME/TODO。
- **今日产出**：一个具备高可用性、安全性，且架构优雅的个人版 "Mini-DeerFlow" 后端。

---

### 💡 学习建议
在执行这个计划时，**不要想着复制粘贴**。  
看懂源码逻辑后，先关掉原项目，在你的新项目里**默写架构和关键伪代码**，遇到卡壳的地方再回头查阅原代码。这种“主动提取”的方式对提升架构能力最有帮助！