# Hermes Agent 后端项目分析

## 1）后端范围与学习目标

本报告聚焦 Hermes Agent 的 Python 后端：
- 核心 Agent 循环与模型调用
- 工具发现、注册、分发与安全控制
- 会话持久化与检索
- CLI 与网关编排
- 工具、命令与集成扩展点

如果你的目标是从零学习并达到可提交生产级贡献，请将本文件作为架构地图，并配合 `plans/` 下的 14 天学习计划一起使用。

## 2）后端架构总览

后端主要分层：
- Agent 运行时：`run_agent.py`（`AIAgent`）负责对话循环、工具调用轮次、重试、预算与用量统计。
- 工具编排层：`model_tools.py` + `tools/registry.py` 提供 schema 解析与工具安全分发。
- 工具实现层：`tools/*.py` 按能力拆分（terminal、web、browser、file、delegate、mcp 等）。
- 会话存储层：`hermes_state.py`（`SessionDB`）使用 SQLite + FTS5 存储会话元数据与消息。
- CLI 运行层：`cli.py` + `hermes_cli/*` 处理交互体验、斜杠命令、配置生命周期与初始化流程。
- 消息网关层：`gateway/run.py` + `gateway/platforms/*` 处理 Telegram/Discord/Slack 等并路由到 `AIAgent`。
- Prompt/上下文内核：`agent/*` 负责 prompt 构建、压缩、缓存、模型元数据、记忆与轨迹辅助。

设计风格：
- 以同步编排为主，强调确定性和兼容性
- 通过注册表与命令注册中心提供显式扩展点
- 运行时行为按环境区分（CLI vs gateway vs profile）
- 对危险命令与会话隔离有较强安全护栏

## 3）关键依赖链

后端工具依赖链：
1. `tools/registry.py`（不依赖模型编排模块）
2. `tools/*.py` 在导入时通过 `registry.register(...)` 自注册
3. `model_tools.py` 执行发现逻辑并暴露 API（`get_tool_definitions`、`handle_function_call`）
4. `run_agent.py`/`cli.py`/`gateway/run.py` 消费 `model_tools.py`

这条链路的重要性：
- 新增工具不需要维护巨型 switch 语句
- schema 与 handler 元数据与工具实现同文件共置
- 注册中心可统一执行防覆盖与可用性检查

## 4）端到端请求与工具数据流

A）用户请求进入系统：
- CLI 路径：用户文本 -> `HermesCLI` -> `AIAgent.run_conversation(...)`
- Gateway 路径：平台事件 -> `GatewayRunner` -> 会话路由 -> `AIAgent.run_conversation(...)`

B）Agent 模型循环：
- `AIAgent` 组装消息栈与工具 schema 列表
- 调用模型 completion API
- 若无工具调用：直接返回助手文本
- 若有工具调用：执行工具，把结果追加到消息，再继续循环

C）工具执行流水线：
- `run_agent.py` 调用 `model_tools.py` 的 `handle_function_call(...)`
- `model_tools.py` 从 registry 解析工具并分发到 handler
- 结果标准化为 JSON 字符串并注入为 `tool` 角色消息

D）持久化：
- 会话元数据与消息通过 `SessionDB`（`hermes_state.py`）保存
- 文本自动进入 FTS5 索引，用于检索类场景

## 5）核心模块分析

## 5.1 `run_agent.py`（`AIAgent`）

职责：
- 基于 `max_iterations` 与 `IterationBudget` 运行对话循环
- 准备并维护消息历史
- 将工具调用集成到迭代回合
- 管理重试、故障切换提示、上下文压缩与用量计费
- 协调中断、spinner 回调与输出格式化

关键机制：
- 线程安全迭代预算与 refund 语义（用于特定工具流程）
- 对安全/不安全工具分组做受控并行执行决策
- 针对破坏性终端命令和重定向覆盖的防护
- prompt 缓存与压缩之间必须保持 cache-safe

学习陷阱：
- 文件体量大，建议按功能切片阅读，而不是从上到下通读。

## 5.2 `model_tools.py`

职责：
- 触发工具发现（`discover_builtin_tools`、MCP、插件）
- 按启用/禁用 toolset 过滤并提供工具 schema
- 在同步编排下安全桥接异步工具 handler
- 统一分发函数调用并做错误封装

关键机制：
- `_run_async(...)` 正确处理 sync-in-async 场景：
  - 常规 CLI 线程
  - worker 线程
  - 已存在运行中 event loop 的上下文
- 兼容旧 toolset 名称映射，避免历史配置失效
- 进程级最近解析工具名可供下游工具逻辑参考

## 5.3 `tools/registry.py`

职责：
- 集中管理工具元数据与 handler
- 发现自注册工具模块
- 为并发读取提供稳定快照
- 阻止不安全工具名覆盖（shadowing）

关键机制：
- 导入期 AST 检测顶层 `registry.register(...)`
- 锁保护写入 + 快照读，保证线程安全
- MCP 刷新场景仅允许 MCP 对 MCP 覆盖

## 5.4 `hermes_state.py`（`SessionDB`）

职责：
- 会话与消息的 SQLite 持久化
- FTS5 索引与触发器维护
- schema 版本迁移
- 并发写入竞争控制

关键机制：
- WAL 模式 + 较短 sqlite timeout
- 应用层抖动重试（`BEGIN IMMEDIATE`）避免锁竞争队列效应
- 周期性被动 checkpoint 控制 WAL 增长

## 5.5 `gateway/run.py`

职责：
- 启动并管理多平台适配器
- 维护会话到 agent 的生命周期
- 网关运行时环境/配置桥接
- 异步编排与长生命周期进程治理

关键机制：
- 非标准系统下的 CA 证书引导
- config.yaml -> env 桥接（terminal/auxiliary/agent/display）
- `AIAgent` 缓存受控（容量 + 空闲 TTL）
- 网关安全模式开关（quiet mode、exec approval）

## 5.6 `hermes_cli/config.py`

职责：
- 配置与环境路径的规范入口（profile-aware）
- setup 与配置编辑流程
- managed mode 行为与升级命令建议
- 权限加固与容器场景例外处理

关键机制：
- 禁止硬编码 `~/.hermes`，必须使用 profile-safe helper
- 明确区分 config.yaml 与 .env 的职责

## 5.7 `tools/approval.py`

职责：
- 通过稳健归一化识别危险命令
- 维护会话级审批状态与队列
- 同时支持 CLI 与 gateway 审批流程
- 对接永久 allowlist 持久化

关键机制：
- 正则匹配前先做 ANSI 清洗 + Unicode 归一化
- 上下文局部 session key 降低跨会话竞争风险
- 覆盖 shell/script/git/gateway 自杀式操作等风险模式

## 6）配置、Profiles 与运行时隔离

配置来源：
- `HERMES_HOME/config.yaml`：运行参数
- `HERMES_HOME/.env`：密钥与供应商凭据

Profile 安全模型：
- 主要模块导入前先覆盖 `HERMES_HOME`
- 状态/配置/记忆/技能/会话数据按 profile 隔离
- 用户可见路径输出应使用 profile-aware 的展示 helper

工程影响：
- 后端功能实现不得硬编码 `~/.hermes`
- profile 相关测试应同时设置 `Path.home()` 与 `HERMES_HOME`

## 7）安全与可靠性评估

安全控制：
- 危险命令识别与审批门禁
- 会话级审批上下文隔离
- 可选脱敏与环境变量控制

可靠性控制：
- 迭代预算与超时控制
- 混合同步/异步调用栈下的防御式桥接
- 面向多进程访问优化的 sqlite 锁竞争策略
- 配置/环境加载失败时的兜底，减少硬崩溃

已知后端风险区域：
- 大型单体文件带来更高回归面
- 兼容性全局状态在委派/子代理路径中需谨慎隔离
- 长生命周期网关会话需要严格内存/缓存治理

## 8）如何安全扩展后端

新增工具：
1. 在 `tools/<name>.py` 实现并 `registry.register(...)`
2. 配置 toolset 与依赖需求元数据
3. 在 `toolsets.py` 挂载对应 toolset
4. 补充/调整测试

新增斜杠命令：
1. 在 `hermes_cli/commands.py` 新增 `CommandDef`
2. 在 `HermesCLI.process_command()` 增加分发
3. 如需网关支持，在 `gateway/run.py` 增加处理分支

新增配置项：
1. 更新 `hermes_cli/config.py` 的 `DEFAULT_CONFIG`
2. 需要密钥/交互输入时更新 `OPTIONAL_ENV_VARS`
3. 必要时补迁移逻辑与版本更新

## 9）后端学习的测试策略

建议节奏：
- 先跑你改动模块的聚焦测试
- 再跑相关目录级测试
- 最后通过项目 wrapper 跑全量

修改后端时重点验证：
- profile 路径行为无回归
- 工具分发仍然确定可控
- CLI 与 gateway 的共享命令行为一致
- 未改动审批策略时，危险命令审批行为保持不变

## 10）建议阅读顺序（对应 14 份学习文件）

按以下顺序学习：
1. `plans/backend-learning-day-01-foundations.md`
2. `plans/backend-learning-day-02-agent-loop.md`
3. `plans/backend-learning-day-03-prompt-context.md`
4. `plans/backend-learning-day-04-model-routing.md`
5. `plans/backend-learning-day-05-tool-registry.md`
6. `plans/backend-learning-day-06-tool-execution.md`
7. `plans/backend-learning-day-07-terminal-security.md`
8. `plans/backend-learning-day-08-sessiondb.md`
9. `plans/backend-learning-day-09-cli-runtime.md`
10. `plans/backend-learning-day-10-gateway-core.md`
11. `plans/backend-learning-day-11-tui-gateway-rpc.md`
12. `plans/backend-learning-day-12-memory-skills-trajectories.md`
13. `plans/backend-learning-day-13-testing-quality.md`
14. `plans/backend-learning-day-14-capstone.md`

## 11）14 天后你应达到的能力

你应能够：
- 解释从用户输入到工具结果再到会话持久化的完整后端链路
- 新增一个可上线工具（含配置、测试与异常处理）
- 排查 gateway 会话问题与审批流程问题
- 识别并处理 profile-safe 路径与配置迁移兼容问题
- 提交符合架构约束与运维约束的后端 PR

