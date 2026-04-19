# Day 01 - 项目全景与依赖链（基础地基日）

## 目标
在全局视野下理解 Hermes Agent 的后端架构，摸清所有入口点、关键文件、与依赖关系。这是建立心智模型的地基。

## 关键文件
- `backend.zh.md`, `backendclaude.md`（本项目的两份分析）
- `README.md`, `AGENTS.md`
- `run_agent.py`, `cli.py`, `gateway/run.py`
- `model_tools.py`, `toolsets.py`, `tools/registry.py`

## 学习内容

### 1) 后端架构的 4 大层次
```
┌─ 交互层（CLI / Gateway / TUI）
├─ 编排层（AIAgent / 工具分发）
├─ 能力层（工具 / Context / 模型）
└─ 持久化层（SessionDB）
```
画出这个图，在脑子里。

### 2) 每一层的关键职责
| 层 | 负责什么 | 关键文件 | 何时改动 |
|---|---------|--------|--------|
| 交互 | 用户输入接收 + 结果展示 | cli.py, gateway/ | 新增平台或命令 |
| 编排 | 消息循环 + 工具调用 | run_agent.py, model_tools.py | 改进对话策略 |
| 能力 | 执行工具 + 构建 prompt | tools/, agent/ | 新增工具或优化 |
| 持久化 | 存储会话 + 搜索 | hermes_state.py | 扩展会话功能 |

### 3) 追踪一个完整请求流
选择 CLI 模式：
```
用户输入 "hello" 
  → cli.py (input 函数)
  → HermesCLI 实例化
  → agent = AIAgent(...)
  → agent.chat("hello")
  → run_conversation() 内部循环开始
  → 组装 messages
  → 调用模型 API
  → 如果有工具调用 → handle_function_call()
  → 会话保存到 SessionDB
  → 返回回复
```
**务必在 VS Code 中打开这些文件，一个接一个单步追踪。**

## 实践任务

### 任务 1: 架构图绘制
用 ASCII 或 Markdown 表格或简单 graphviz，画出：
- 5 个主要入口点（CLI、Gateway Telegram、Gateway Discord、TUI、Batch）
- 3 个核心模块（AIAgent、工具分发、持久化）
- 他们之间的关系

**验收标准**: 能解释为什么 `run_agent.py` 是核心但不是唯一入口。

### 任务 2: 依赖链拓扑
梳理这个链：
```
tools/registry.py 
  ↑ (被导入)
tools/*.py (自注册)
  ↑ (被导入)
model_tools.py (提供 API)
  ↑ (被消费)
run_agent.py / cli.py / gateway/run.py
```

**关键理解**：为什么 registry.py 是最底层，其他都依赖它？

### 任务 3: 文件清点
列出所有后端核心文件（大约 20-30 个），分类：
- Agent 内核（3 个）
- 工具系统（5 个）
- 会话管理（2 个）
- CLI/Gateway（6 个）
- 辅助（其他）

## 风险点与注意事项

⚠️ **不要** 在这一天试图理解所有细节，这只是导览。
⚠️ **记住** Profile 概念：每个 `hermes -p <name>` 有独立的 `HERMES_HOME`。
⚠️ **注意** 这个项目有 120+ 个文件，只有 20% 是你关心的后端。

## 交付物

创建 `notes/day01-architecture.md`：
- 架构图（ASCII 或 Markdown）
- 5 个入口点列表
- 依赖链的文字说明（200 字）
- 一份 20 行的后端文件清单
- 3 个"我想改进 XXX 功能，应该改哪个文件"的答案

## 验收标准

你能够：
1. ✅ 不看文档，解释 Agent 循环的 4 个阶段
2. ✅ 说出 CLI 与 Gateway 的主要差别（同步 vs 异步）
3. ✅ 描述为什么要用 registry pattern（避免中央 switch）
4. ✅ 列出 5 个关键文件及其职责（单句描述）

