Optimizing tool selection...我会先快速梳理 backend 的入口、核心模块、配置与测试结构，再基于代码和文档产出一份从入门到深入的中文学习路线报告。接下来先读取关键文件（如 `README`、`Makefile`、`pyproject`、核心包目录）建立全局图。我先做一轮只读扫描来定位 backend 的真实启动链路与关键目录，产出“先看哪里、再看哪里”的学习地图。

Search complete: 定位后端入口

Semantic workspace search is not currently available

Semantic workspace search is not currently available

Semantic workspace search is not currently available

Searched for files matching `**/backend/**`, 200 matches

Searched for files matching `**/main.py`, no matches

Searched for files matching `**/app.py`, 2 matches

Searched for files matching `**/entrypoint*.py`, no matches

Searched for text `FastAPI|langgraph|LangGraph|agent.*entry|gateway.*entry` (`**/backend/**`), 200 results

Searched for text `def main\(|async def main\(|if __name__ == "__main__"` (`**/backend/**`), 2 results

Searched for text `config.*load|load.*config|settings.*config` (`**/backend/**`), 200 results

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/app/gateway/app.py#1-1), lines 1 to 220

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/app/gateway/services.py#1-1), lines 1 to 260

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/config/app_config.py#1-1), lines 1 to 220

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/config/extensions_config.py#1-1), lines 1 to 220

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/config/agents_config.py)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/CLAUDE.md#1-1), lines 1 to 220

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/agents/lead_agent/agent.py#1-1), lines 1 to 220

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/docs/ARCHITECTURE.md#260-260), lines 260 to 400

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/agents/lead_agent/agent.py#1-1), lines 1 to 260

我已经定位到主入口和架构骨架，下一步读取几个“学习必读”文件来补齐运行命令、依赖、测试与目录职责，然后输出完整中文学习报告。我先并行读取核心说明与构建文件，目标是把“如何跑起来”和“如何按模块读源码”讲清楚。

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/docs/ARCHITECTURE.md#1-1), lines 1 to 260

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/Makefile)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/langgraph.json)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/README.md#1-1), lines 1 to 260

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/pyproject.toml)

我已经拿到运行与架构文档，接下来补一层“源码真实组织”信息：读取关键目录结构和少量核心源码（agent 工厂、工具汇总、运行时依赖注入），确保报告不仅是文档总结，而是可落地的学习路径。我先抓取这些关键文件来对齐代码与文档。

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/agents)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/app/gateway/routers)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/tools/__init__.py)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/agents/__init__.py)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/agents/lead_agent/agent.py#260-260), lines 260 to 358

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/tools/tools.py)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/app/gateway/deps.py)

入口与工具拼装链路已经清晰了，我再补齐运行时执行层（RunManager/StreamBridge）和状态模型（ThreadState），这样你的学习报告会覆盖“请求如何流到 Agent 再流回前端”的完整闭环。现在读取这几个关键实现文件。

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/runtime)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/runtime/__init__.py)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/packages/harness/deerflow/agents/thread_state.py)

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/app/gateway/routers/thread_runs.py#1-1), lines 1 to 260

Read [](file:///h%3A/deer-flow-main/deer-flow-main/backend/app/gateway/routers/runs.py)

我已经整理出主执行闭环；在输出最终报告前，我会快速检查一次记忆笔记区，确认是否有可复用经验，并记录这次分析中可沉淀的学习要点。现在只读查看 memory 目录。

Read memory

Created memory file [](file:///c%3A/Users/mwu42/AppData/Roaming/Code/User/workspaceStorage/fa1dc95d24f7a60925c89e0e4b1f877e/GitHub.copilot-chat/memory-tool/memories/repo/deerflow-backend-overview.md)

**Backend 学习分析报告（DeerFlow）**

你这个项目的 backend 是一个“可运行的 Agent 平台内核”，不是单点 API 服务。它把以下能力组合在一起：  
1. Agent 推理与编排（LangGraph）  
2. 对外 API 网关（FastAPI）  
3. 工具执行与沙箱  
4. 记忆、技能、子代理、MCP 扩展  
5. 会话运行时（Run/Stream/Checkpoint）

如果你想“从头到尾”学会它，建议按“先跑通，再拆分，再深入源码”的顺序。

---

**1. Backend 总体定位**

核心是双层结构：  
1. Harness 层（可复用 Agent 框架）在 deerflow  
2. App 层（网关和渠道集成）在 app

这层边界在测试里有硬约束，防止 Harness 反向依赖 App，见 test_harness_boundary.py。

---

**2. 启动与入口链路（你先掌握这个）**

后端本地启动命令定义在 Makefile：  
1. make dev：启动 LangGraph 服务  
2. make gateway：启动 FastAPI Gateway  
3. make test、make lint：质量检查

LangGraph 图入口配置在 langgraph.json，关键是：  
1. lead_agent 图指向 deerflow.agents:make_lead_agent  
2. checkpointer 在同文件配置

真正的 Agent 工厂在 agent.py。

Gateway 入口在 app.py，启动时会初始化运行时依赖（StreamBridge、RunManager、checkpointer、store），依赖装配逻辑在 deps.py。

---

**3. 核心目录怎么读**

建议按这个顺序读：

1. README.md  
2. ARCHITECTURE.md  
3. pyproject.toml  
4. app_config.py  
5. agent.py  
6. tools.py  
7. thread_state.py  
8. thread_runs.py  
9. runs.py

这条链路几乎覆盖“配置 -> Agent 创建 -> 工具注入 -> 状态 -> API 运行”。

---

**4. 一次请求的完整生命周期（从前端到模型再回来）**

1. 前端请求到 Nginx，再路由到 LangGraph 或 Gateway（见 README.md 和 ARCHITECTURE.md）。  
2. LangGraph 通过 langgraph.json 调用 make_lead_agent。  
3. make_lead_agent 读取 configurable（模型名、是否 plan mode、是否启用 subagent 等），并在 agent.py 里组装 model、tools、middleware、prompt。  
4. tools 由 tools.py 聚合：配置工具 + 内建工具 + MCP 工具 + ACP 工具。  
5. 状态结构由 thread_state.py 维护（sandbox、artifacts、title、todos、uploaded_files、viewed_images）。  
6. 如果走 Gateway run API，则由 thread_runs.py 和 runs.py 提供 create/stream/wait/cancel/join 等生命周期操作。  
7. 运行时单例来自 deps.py，底层接口在 __init__.py。

---

**5. 你需要重点理解的 6 个技术支柱**

1. 配置系统  
主配置在 app_config.py，支持配置路径优先级、环境变量替换、配置版本检查。MCP/技能扩展配置在 extensions_config.py。

2. Agent 装配工厂  
在 agent.py，它决定模型解析、middleware 顺序、plan mode、subagent 开关、bootstrap 模式。

3. 工具系统  
在 tools.py，关键是按配置与运行时能力动态增删工具，例如视图模型才加图片工具、本地沙箱默认不开放 host bash。

4. 运行时系统  
在 runtime 与 deps.py，核心是 RunManager + StreamBridge + checkpointer + store 的协同。

5. 网关路由层  
看 routers，这里是“平台化 API 面”，包含 models、mcp、memory、skills、uploads、threads、runs 等。

6. 状态与中间件  
状态模型见 thread_state.py，中间件主拼装在 agent.py。

---

**6. 学习路径（从 0 到可改代码）**

第一阶段：跑通与观察（1-2 天）  
1. 在 backend 目录执行 make install、make dev、make gateway、make test。  
2. 用 API 文档页面观察 Gateway 路由。  
3. 对照 README.md 画一张你自己的请求流图。

第二阶段：配置驱动理解（2-3 天）  
1. 深读 app_config.py。  
2. 修改一项可见配置（例如工具组或模型），验证行为变化。  
3. 理解 extensions_config 与主配置的分工。

第三阶段：Agent 内核（3-5 天）  
1. 逐段读 agent.py。  
2. 搞清楚 make_lead_agent 的输入、输出、关键开关。  
3. 跟进到 tools.py 看工具拼装。

第四阶段：运行时与 API（3-4 天）  
1. 读 deps.py 与 __init__.py。  
2. 读 runs 两个路由文件，理解 stream/wait/cancel 的差异。  
3. 手工调用一次 run-stream 与 run-wait，比较结果。

第五阶段：测试反推设计（持续）  
1. 从 tests 选你关心的子系统测试。  
2. 先读测试名和断言，再回到实现文件。  
3. 这能最快形成“改动不破坏系统”的直觉。

---

**7. 这个 backend 的难点与价值**

1. 难点不是语法，而是“编排层”复杂性：Agent、工具、沙箱、运行时、路由都可独立演进。  
2. 价值在于它是一个可扩展平台骨架：你加模型、加工具、加中间件、加路由都可插拔。  
3. 真正掌握标志：你能新增一个工具并让它安全地进入完整链路（配置可控、路由可观测、测试可回归）。

---

**8. 你的下一步建议（可直接执行）**

1. 我可以给你一份“7 天实战学习计划”，每天对应具体文件、具体问题、具体练习。  
2. 我可以带你做一次源码导读：从 make_lead_agent 开始，逐行讲到工具执行与 run streaming。  
3. 我可以给你设计一个小改造任务（例如新增一个内建工具），并配套测试清单。

**继续深入分析（Backend 从头到尾）**

你选了 1 和 3，我把两部分合并成一个“进阶版学习包”：先补齐更深的架构理解，再给你一套可执行学习计划。

**A. 从系统视角看 Backend 的完整闭环**
1. 进程与职责分离  
LangGraph 负责 Agent 运行与状态流转，Gateway 负责平台 API 能力，见 README.md 与 ARCHITECTURE.md。

2. Agent 真实入口  
图入口在 langgraph.json，核心函数是 make_lead_agent，位于 agent.py。

3. 运行时依赖注入  
Gateway 启动时注入 StreamBridge、checkpointer、store、RunManager，见 deps.py 和 app.py。

4. 工具拼装机制  
工具不是写死的，而是动态拼装：配置工具 + 内建工具 + MCP + ACP，见 tools.py。  
这就是项目可扩展性的关键。

5. 状态模型的扩展点  
ThreadState 在标准 AgentState 上扩了 sandbox、artifacts、todos、viewed_images 等，见 thread_state.py。  
你做功能迭代时，状态字段设计比接口更关键。

6. Run API 的平台化抽象  
线程态 run 在 thread_runs.py，无预置线程 run 在 runs.py。  
这两组接口把“创建、流式、等待、取消、加入流”拆得非常清楚，适合前端 SDK 对接。

**B. 你学习时最该抓住的“5 条主线”**
1. 配置主线  
先吃透 app_config.py 和 extensions_config.py。  
项目几乎所有行为都由配置驱动。

2. Agent 主线  
围绕 agent.py 学：模型解析、middleware 顺序、plan mode、subagent 开关。

3. 工具主线  
从 tools.py 逆推工具来源，再延伸到 sandbox 和 mcp。

4. 运行时主线  
先读 __init__.py，再读 deps.py 与 runs 路由文件，建立“谁创建 run，谁消费 stream，谁管理生命周期”的脑图。

5. 测试主线  
用测试反推设计意图。先从 test_harness_boundary.py 开始，再按模块挑测试读。

---

**分阶段学习计划（你要的 3）**

**第 1 周：跑通与认图（目标：能解释系统全貌）**
1. 执行 backend 基础命令并确认通过，参考 Makefile。  
2. 精读 README.md 和 ARCHITECTURE.md。  
3. 输出一页你的“请求流图”：前端请求如何到 LangGraph/Gateway，再回前端。  
4. 验收标准：你能口头讲清楚 4 个组件职责和 2 类 API 路由分工。

**第 2 周：配置与 Agent 内核（目标：能改配置并预测行为）**
1. 深读 app_config.py。  
2. 深读 agent.py。  
3. 做 2 个小实验：切换模型开关、启停 plan mode。  
4. 验收标准：你能说出 make_lead_agent 的输入参数与关键分支。

**第 3 周：工具与运行时（目标：能追踪一次完整 run）**
1. 深读 tools.py。  
2. 补读 __init__.py 及相关运行时目录。  
3. 对照 thread_runs.py 与 runs.py，画 run 生命周期图。  
4. 验收标准：你能解释 stream 与 wait 的语义差异，以及取消策略影响。

**第 4 周：测试驱动理解与微改造（目标：能安全改动）**
1. 选一个子系统，先读测试再读实现。  
2. 做一个“小功能改造”演练：例如新增一个内建工具的开关控制。  
3. 跑 lint/test 验证回归。  
4. 验收标准：你能提交一次不破坏现有测试的改动并解释设计权衡。

---

**建议你每周都产出的学习成果**
1. 一张架构图。  
2. 一份调用链笔记（函数级）。  
3. 一个实验记录（改了什么配置，行为怎么变）。  
4. 一份“我现在还不懂的问题清单”。

---

如果你愿意，我下一步可以直接给你“第 1 周 Day 1 到 Day 7 的每日任务清单”，按文件和问题驱动，做到每天 60-90 分钟可落地。