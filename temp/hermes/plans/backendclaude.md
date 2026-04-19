# Hermes Agent 后端深度学习与实现指南（Claude辅助版）

## 核心目标

在 14 天内完整学习 Hermes Agent 后端架构，并能够独立完成以下任务：
1. **理解能力**：从用户请求到模型响应，再到会话持久化的完整链路
2. **扩展能力**：新增工具、命令、集成点不触发架构崩坏
3. **重写能力**：在理解约束的基础上，有把握地重构或完成功能
4. **质量保证**：代码改动符合现有模式，测试覆盖关键路径

---

## 第一部分：后端分层架构（必读）

### 1.1 架构全景

```
┌─────────────────────────────────────────────────────────────┐
│                     用户交互层                                  │
│  CLI (prompt_toolkit) │ Gateway (Telegram/Discord) │ TUI (Ink)  │
└──────────┬───────────────────────────────────────────┬────────┘
           │                                           │
┌──────────▼───────────────────────────────────────────▼────────┐
│                   编排与业务逻辑层                                │
│  run_agent.py (AIAgent)  - 对话循环                            │
│  model_tools.py          - 工具分发                            │
│  hermes_cli/             - 命令与配置                          │
│  gateway/run.py          - 网关生命周期                        │
└──────────┬───────────────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────────────┐
│                   能力层                                        │
│  ┌─────────────────┬─────────────────┬──────────────┐         │
│  │  工具层         │  Context层       │  模型层      │         │
│  │ tools/          │ agent/           │ (Provider)   │         │
│  │ registry.py     │ prompt_builder   │ retry/       │         │
│  │ terminal_tool   │ compress         │ routing      │         │
│  │ approval.py     │ memory_manager   │              │         │
│  └─────────────────┴─────────────────┴──────────────┘         │
└──────────┬───────────────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────────────┐
│                   数据持久化层                                    │
│  hermes_state.py (SessionDB)  - SQLite + FTS5                 │
│  session_context.py           - 会话上下文                     │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 核心概念梳理

| 概念 | 定义 | 关键文件 | 约束条件 |
|------|------|--------|--------|
| **Agent** | 对话循环控制器，维护消息历史、调用模型、执行工具 | `run_agent.py` | max_iterations / IterationBudget |
| **Tool** | 原子能力单元，自注册到中央注册表 | `tools/*.py` | 必须返回 JSON 字符串；需要 check_fn 验证可用性 |
| **Toolset** | 工具分组，支持按功能/环保对启用/禁用 | `toolsets.py` | 不能中途切换（破坏 prompt cache）|
| **Message** | OpenAI 格式消息（role, content, tool_calls） | `run_agent.py` | 严格遵循 OpenAI schema |
| **Session** | 用户会话，包含元数据与消息历史 | `hermes_state.py` | 按 session_id 分片；支持 parent_session_id 链 |
| **Profile** | 多实例隔离，每个 Profile 有独立 HERMES_HOME | `hermes_cli/config.py` | 禁止硬编码 ~/.hermes 路径 |
| **Command** | 斜杠命令，通过中央注册表分发 | `hermes_cli/commands.py` | 需要在 CommandDef 中注册 + dispatch 中实现 |

---

## 第二部分：关键代码路径解析

### 2.1 请求流入 -> 模型调用 -> 工具执行 -> 持久化

#### 路径 A：CLI 模式下的完整流程

```python
# 1. 用户输入 (cli.py)
user_text = input("> ")

# 2. 创建 AIAgent 并启动对话
agent = AIAgent(model="claude-3-5-sonnet", max_iterations=90)
final_response = agent.chat(user_text)

# 3. Agent 内部 (run_agent.py - run_conversation)
def run_conversation(user_message, system_message, conversation_history):
    while iteration < max_iterations:
        # 3.1 组装 messages
        messages = [system_message] + conversation_history
        
        # 3.2 获取工具 schema (model_tools.py)
        tool_schemas = get_tool_definitions(
            enabled_toolsets=self.enabled_toolsets,
            disabled_toolsets=self.disabled_toolsets
        )
        
        # 3.3 调用模型 API
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tool_schemas,
            max_tokens=self.context_limit
        )
        
        # 3.4 如果没有工具调用，直接返回
        if not response.tool_calls:
            return response.content
        
        # 3.5 执行工具 (这是关键!)
        for tool_call in response.tool_calls:
            result = handle_function_call(
                tool_call.name, 
                tool_call.arguments,
                task_id=self.session_id
            )
            # result 是 JSON 字符串
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # 3.6 循环继续，消息继续堆积

# 4. 工具分发 (model_tools.py - handle_function_call)
def handle_function_call(function_name, function_args, task_id):
    # 4.1 从注册表查询工具 entry
    entry = registry.get_entry(function_name)
    if not entry:
        return json.dumps({"error": "Tool not found"})
    
    # 4.2 检查可用性
    if not entry.check_fn():
        return json.dumps({"error": "Tool unavailable"})
    
    # 4.3 执行 handler (同步或异步)
    try:
        result = entry.handler(function_args, task_id=task_id)
        if asyncio.iscoroutine(result):
            result = _run_async(result)
        return result  # 必须是 JSON 字符串
    except Exception as e:
        return json.dumps({"error": str(e)})

# 5. 持久化 (hermes_state.py)
db.save_message(
    session_id=session_id,
    role="assistant",
    content=response.content,
    tool_calls=response.tool_calls  # JSON
)
```

#### 路径 B：Gateway 模式下的差异

```python
# gateway/run.py
async def _handle_user_message(self, event):
    session_key = event.get("session_key")
    user_text = event.get("text")
    
    # 1. 从 session 缓存获取或新建 AIAgent
    agent = self._get_or_create_agent(session_key)
    
    # 2. 运行对话 (同步阻塞)
    result = agent.run_conversation(user_text)
    
    # 3. 消息会自动持久化 (agent 内部)
    # 4. 通过平台适配器发送回复
    await platform_adapter.send_message(result)
```

### 2.2 工具注册与发现机制

#### 关键：自注册模式避免中央 switch 语句

```python
# tools/web_tools.py (模板)
from tools.registry import registry

def web_search(query: str, num_results: int = 10, task_id: str = None) -> str:
    """Execute web search."""
    try:
        results = perform_search(query, num_results)
        return json.dumps({"results": results})
    except Exception as e:
        return json.dumps({"error": str(e)})

# 关键：在模块级别注册
registry.register(
    name="web_search",
    toolset="web_tools",
    schema={
        "name": "web_search",
        "description": "Search the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "num_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    },
    handler=lambda args, **kw: web_search(
        query=args.get("query", ""),
        num_results=args.get("num_results", 10),
        task_id=kw.get("task_id")
    ),
    check_fn=lambda: bool(os.getenv("SERPER_API_KEY")),
    requires_env=["SERPER_API_KEY"],
    description="Search the web using Serper API"
)

# model_tools.py 的发现流程
def discover_builtin_tools():
    """导入所有 tools/*.py，触发它们的 registry.register() 调用"""
    for module_path in Path("tools").glob("*.py"):
        if module_path.name not in ["__init__.py", "registry.py"]:
            importlib.import_module(f"tools.{module_path.stem}")
```

**关键约束**：
- 禁止硬编码工具列表在某处
- 每次新增工具只需要：`tools/<name>.py` + `toolsets.py` 中挂载 toolset
- 自动反映在所有消费方：`run_agent.py`、`cli.py`、`gateway/run.py`

### 2.3 危险命令检测与审批流

```python
# 工具执行前的安全门禁 (tools/approval.py)
def detect_dangerous_command(command: str):
    """通过 regex 匹配危险模式"""
    command_lower = _normalize_command_for_detection(command).lower()
    for pattern, description in DANGEROUS_PATTERNS:
        if re.search(pattern, command_lower):
            return (True, description)  # 是危险的
    return (False, None)

# 审批流程（同步 CLI 与异步 Gateway）
# CLI: 
#   → detect → 如果危险 → 显示提示 → input() → approve/deny → 继续或中止

# Gateway:
#   → detect → 如果危险 → 创建 _ApprovalEntry → 发送通知 → 等待 event.respond
#   → (用户在 /approve 命令中) → resolve entry → 继续
```

### 2.4 Context 与 Prompt Cache 的交互

**约束**：
- 一旦启用 prompt caching，中途**不能改变** system prompt / tool 列表 / 前文消息
- Context compression 是**唯一允许的异常**，需要特殊处理

```python
# run_agent.py 中的 cache 安全性检查
if self.use_anthropic_cache and iteration > 2:
    # 检测是否需要 context compression
    if estimated_tokens > 0.9 * context_limit:
        # 触发压缩（这会破坏 cache，但是有意的）
        compressed_context = compress_context(messages)
        messages = rebuild_messages_after_compression(compressed_context)
        # 从此时起，cache 重新开始计数
```

---

## 第三部分：Profile 与配置隔离

### 3.1 Profile 的目的

支持在同一台机器上运行多个独立的 Hermes 实例（不同 API keys、不同配置、不同会话）。

```bash
# 启动默认 profile
hermes chat "hello"

# 启动特定 profile
hermes -p work chat "hello"
hermes -p personal chat "hello"

# 每个 profile 有独立的 HERMES_HOME
~/.hermes/             # default profile
~/.hermes/profiles/work/
~/.hermes/profiles/personal/
```

### 3.2 Profile-Safe 代码的原则

**金律：禁止硬编码 `~/.hermes`**

```python
# ❌ 错误
config_path = Path.home() / ".hermes" / "config.yaml"

# ✅ 正确
from hermes_constants import get_hermes_home
config_path = get_hermes_home() / "config.yaml"

# 用户可见的路径字符串，使用 display 版本
from hermes_constants import display_hermes_home
print(f"Config saved to {display_hermes_home()}/config.yaml")
# 默认 profile 输出: ~/.hermes/config.yaml
# work profile 输出: ~/.hermes/profiles/work/config.yaml
```

### 3.3 配置加载的优先级

```python
# hermes_cli/config.py
DEFAULT_CONFIG = {
    "model": "anthropic/claude-opus-4.6",
    "max_iterations": 90,
    "terminal": {
        "backend": "local",
        "cwd": "auto",  # 用户 home 或当前目录
    },
    # ... 许多默认值
}

# 加载优先级（从高到低）：
# 1. ~/.hermes/config.yaml (用户配置最优先)
# 2. ~/.hermes/.env (API key 与密钥)
# 3. 系统环境变量 (os.environ)
# 4. DEFAULT_CONFIG (代码硬编码默认)
```

---

## 第四部分：测试与质量保证关键点

### 4.1 必须理解的测试设置

项目有一个强制性的测试 wrapper：`scripts/run_tests.sh`

```bash
# ✅ 推荐方式（CI 一致性）
scripts/run_tests.sh                                  # 全量

# ⚠️  仅在特定场景使用直接 pytest
python -m pytest tests/tools/test_approval.py -v
```

**为什么不能直接 pytest？**

- 环境隔离：wrapper 清除所有 API key、设置 TZ=UTC、LANG=C.UTF-8
- 并发度：wrapper 用 `-n 4` 强制 xdist 并发度，避免本地 20 核机器的多进程 flake
- Home 目录：wrapper 临时重定向 HERMES_HOME 到 tmp 目录

### 4.2 修改后端代码时的回归检查清单

```
[ ] Profile 路径：没有硬编码 ~/.hermes，测试覆盖多 profile 场景
[ ] 工具分发：registry 中的工具仍能正确分发，test_handle_function_call 通过
[ ] CLI/Gateway 一致：共享命令行为在两端对称
[ ] 危险命令审批：approval 流程不变（除非有意改动）
[ ] 会话持久化：SessionDB 读写正常，schema migration 不崩坏
[ ] Prompt cache 安全：compression 流程未被破坏
[ ] 异步桥接：_run_async() 逻辑在 sync/worker/async context 中都工作
```

### 4.3 常见本地 vs CI 差异（为什么要用 wrapper）

| 问题 | 本地无 wrapper | 用 wrapper 后 |
|------|----------------|-------------|
| 本地 16 核跑 `-n auto`，CI 4 核跑 `-n 4` | 测试顺序不同，flaky 测试在本地通过 | 统一 `-n 4` |
| 本地设置了 OPENAI_API_KEY | 某些测试意外过 | 清除所有 API key |
| 本地时区 PDT，CI UTC | 时间相关测试失败 | 统一 UTC |
| 本地 HOME=/Users/xxx，HERMES_HOME 混淆 | 测试污染用户实际配置 | 隔离到 tmp 目录 |

---

## 第五部分：14 天学习路线图与重点

### Week 1: 架构与基础（Day 1-7）

**Day 1: 项目全景与依赖链**
- 文件：`README.md`, `AGENTS.md`, `backend.zh.md`，本文件
- 任务：画出架构图，列出所有后端入口点
- 交付：`notes/day01-architecture.md`

**Day 2: Agent 循环核心**
- 文件：`run_agent.py`（重点：`__init__`, `run_conversation`, `IterationBudget`）
- 任务：逐行追踪一次完整 run_conversation 流程
- 交付：`notes/day02-agent-loop-trace.md` + 伪代码

**Day 3: 工具注册与分发**
- 文件：`tools/registry.py`, `model_tools.py`, 3-5 个工具实现
- 任务：理解 registry 的并发安全设计；添加一个 dummy tool 验证流程
- 交付：`notes/day03-tool-registry.md` + `test_dummy_tool.py`

**Day 4: 会话持久化**
- 文件：`hermes_state.py` (`SessionDB`)
- 任务：理解 SQLite WAL 模式、FTS5、schema migration；写一个 SessionDB 单元测试
- 交付：`notes/day04-sessiondb.md` + `test_sessiondb_custom.py`

**Day 5: Prompt 与 Context**
- 文件：`agent/prompt_builder.py`, `agent/context_compressor.py`
- 任务：理解 prompt 组件与 cache 约束；用伪代码演示 compression 流程
- 交付：`notes/day05-prompt-context.md`

**Day 6: 危险命令与审批**
- 文件：`tools/approval.py`, `tools/terminal_tool.py`
- 任务：理解所有危险模式；在 approval 中新增 1 个模式
- 交付：`notes/day06-approval.md` + 新增模式的测试

**Day 7: CLI 与命令分发**
- 文件：`cli.py`, `hermes_cli/commands.py`, `hermes_cli/config.py`
- 任务：理解命令注册与分发；新增 1 个简单斜杠命令
- 交付：`notes/day07-cli-commands.md` + 新命令实现与测试

### Week 2: 扩展与运维（Day 8-14）

**Day 8: Gateway 与多平台**
- 文件：`gateway/run.py`, `gateway/session.py`, 1 个平台适配器
- 任务：理解平台适配器与会话生命周期；文档化网关初始化流程
- 交付：`notes/day08-gateway.md`

**Day 9: Profile 与配置治理**
- 文件：`hermes_cli/config.py`, `hermes_constants.py`
- 任务：用 profile 模式运行 hermes，理解隔离机制；修复一个 profile path bug
- 交付：`notes/day09-profiles.md` + bug fix PR

**Day 10: 记忆、技能与轨迹**
- 文件：`agent/memory_manager.py`, `agent/skill_commands.py`, `agent/trajectory.py`
- 任务：理解长期学习机制与轨迹数据
- 交付：`notes/day10-learning-systems.md`

**Day 11: 异步桥接与并发**
- 文件：`model_tools.py` (_run_async), `run_agent.py` (parallel execution)
- 任务：理解 sync/async context 交互；分析并发工具执行的决策逻辑
- 交付：`notes/day11-async-concurrency.md`

**Day 12: 测试策略与质量门**
- 文件：`tests/conftest.py`, `scripts/run_tests.sh`, 选定的测试文件
- 任务：理解测试隔离与 CI 一致性；为你的改动编写 3 个测试用例
- 交付：`notes/day12-testing.md` + 3 个新增测试

**Day 13: 模型路由与元数据**
- 文件：`agent/model_metadata.py`, `agent/smart_model_routing.py`
- 任务：理解不同模型的 context 约束与 fallback 逻辑
- 交付：`notes/day13-model-routing.md`

**Day 14: 综合项目**
- 任务：选择以下其中一项完成：
  1. 新增一个完整的工具（有配置、测试、文档）
  2. 重构一个核心模块的错误处理逻辑
  3. 优化会话压缩或 cache 策略中的一个问题
- 交付：完整的 PR（代码 + 测试 + 文档） + `notes/day14-capstone-report.md`

---

## 第六部分：注意事项 (Critical DO's & DON'Ts)

### 架构约束

**✅ DO：**
- ✅ 用 `get_hermes_home()` 和 `display_hermes_home()` 处理所有路径
- ✅ 在模块级别添加工具，在 `toolsets.py` 中注册 toolset
- ✅ 工具 handler 必须返回 JSON 字符串
- ✅ 使用 `registry.register()` 暴露工具元数据
- ✅ 斜杠命令在 `CommandDef` + `HermesCLI.process_command()` 两处注册
- ✅ 测试使用 `scripts/run_tests.sh` 确保 CI 一致

**❌ DON'T：**
- ❌ 硬编码 `~/.hermes` 或 `Path.home() / ".hermes"`
- ❌ 在运行时中途改变 system prompt / toolset（破坏 cache）
- ❌ 工具 handler 返回非 JSON 对象（会导致模型出错）
- ❌ 创建全局工具列表维护（用 registry）
- ❌ 直接调用 `pytest` 跳过 wrapper（导致 CI 不一致）
- ❌ 在多平台 gateway 中硬编码 CLI-only 的行为

### 代码质量

**✅ DO：**
- ✅ 每个改动都配套测试
- ✅ 用 `asyncio.iscoroutine()` 检测异步工具
- ✅ 在 `check_fn()` 中验证工具前置条件（如 API key）
- ✅ 在 `DANGEROUS_PATTERNS` 中新增防护模式
- ✅ 使用 `contextvars` 管理 gateway 中的会话上下文
- ✅ 记录为什么某个设计决策（注释）

**❌ DON'T：**
- ❌ 在工具 handler 中捕获所有异常，至少要 log
- ❌ 信任用户输入，始终做 normalization
- ❌ 在一个函数中做多个无关的事情
- ❌ 忽视线程安全：registry 的读写、session state、approval queue
- ❌ 假设某个 API key 一定存在（总是检查）

### 向后兼容性

**✅ DO：**
- ✅ 新增配置项时，提供合理的 DEFAULT_CONFIG
- ✅ 改变 Session schema 时，新增 migration（递增版本）
- ✅ 保留旧 toolset 别名，用 `_LEGACY_TOOLSET_MAP`
- ✅ 在 AGENTS.md 中记录新增的架构决策

**❌ DON'T：**
- ❌ 删除已有的 config 键，至少要 deprecation warning
- ❌ 改变消息格式（role/content/tool_calls schema）
- ❌ 不告诉用户就重命名命令或工具
- ❌ 在不提供迁移的情况下改变数据库 schema

---

## 第七部分：实战常见问题

### Q1: 我新增了一个工具，但 agent 看不到它

**排查清单：**
1. ✅ 在 `tools/<name>.py` 中有 top-level `registry.register()` 吗？
2. ✅ `toolsets.py` 中有该 toolset 吗？
3. ✅ 工具的 `check_fn()` 返回 True 吗？（检查 API key）
4. ✅ 启用 toolset 的 enabled_toolsets 包含该 toolset 吗？

```python
# 调试：
from model_tools import get_tool_definitions
schemas = get_tool_definitions(enabled_toolsets=["web_tools"])
print([s["name"] for s in schemas])  # 检查你的工具是否在列表中
```

### Q2: 危险命令检测给了假正或假负

**处理流程：**
1. 在 `tools/approval.py` 的 `DANGEROUS_PATTERNS` 中加入或调整正则
2. 添加测试用例在 `tests/tools/test_approval.py`
3. 用 `_normalize_command_for_detection()` 测试你的模式
4. 运行 `scripts/run_tests.sh tests/tools/test_approval.py` 验证

### Q3: Prompt cache 被破坏了

**症状：** 突然收到 token 用量大幅增加

**根因分析：**
- Context compression？（允许，有意破坏）
- 中途改变 enabled_toolsets？（不允许，需要修复）
- 修改了 system prompt builder？（不允许，需要修复）
- 使用了不同的模型？（不允许，需要修复）

**修复：** 使用 `agent/prompt_caching.py` 的 cache 控制接口

### Q4: 会话保存失败了

**排查：**
```python
from hermes_state import SessionDB
db = SessionDB()
try:
    db.save_message(session_id="test", role="user", content="hi")
except Exception as e:
    print(f"Error: {e}")  # WAL 锁定？permission 错误？磁盘满？
```

**常见原因：**
- WAL 文件被意外删除 → 重启进程，WAL 会重建
- 权限不足 → 检查 `chmod` 与 HERMES_HOME 权限
- 磁盘满 → 清理 ~/.hermes/state.db

### Q5: Profile 隔离不工作

**检查：**
```bash
# 默认 profile
echo $HERMES_HOME  # 应该是 ~/.hermes

# 切换到 work profile
hermes -p work profile list
echo $HERMES_HOME  # 应该是 ~/.hermes/profiles/work

# 确认配置独立
hermes config show
hermes -p work config show  # 不同的值？
```

---

## 第八部分：学习资源与参考

### 推荐的学习方式

1. **Day N：阅读** → 理解概念
2. **Day N：追踪** → 阅读代码，跟踪调用栈
3. **Day N：动手** → 写个小脚本测试理解
4. **Day N：文档** → 写学习笔记
5. **Day N：实现** → 完成 Day N 的任务

### 代码阅读技巧

```python
# 快速定位一个概念的实现
grep -r "IterationBudget" --include="*.py" .
# 输出：run_agent.py:150 class IterationBudget
#       run_agent.py:200 self.iteration_budget = IterationBudget(...)

# 找所有调用某个函数的地方
grep -r "handle_function_call" --include="*.py" .

# 用 IDE 的 "Find Usage" 功能（推荐！）
```

### 提交 PR 的检查清单

在打算提交 PR 前，自检：

- [ ] 代码遵循现有模式（不创新架构）
- [ ] 新增/改动的测试覆盖代码路径
- [ ] `scripts/run_tests.sh` 全部通过
- [ ] 对 AGENTS.md 的改动是否需要更新
- [ ] Profile-safe：没有硬编码路径
- [ ] 工具/命令已注册：不是硬编码分发
- [ ] 向后兼容性：没有破坏性改动
- [ ] 文档/注释解释了 why，不仅仅是 what

---

## 第九部分：模块地图速查表

| 模块 | 职责 | 关键函数/类 | 学习难度 |
|------|------|-----------|--------|
| `run_agent.py` | Agent 循环 | `AIAgent.run_conversation()` | ⭐⭐⭐ |
| `model_tools.py` | 工具编排 | `handle_function_call()`, `_run_async()` | ⭐⭐ |
| `tools/registry.py` | 工具注册 | `ToolRegistry`, `register()` | ⭐ |
| `tools/approval.py` | 危险命令 | `detect_dangerous_command()` | ⭐⭐ |
| `tools/terminal_tool.py` | 终端执行 | `terminal()` handler | ⭐⭐⭐ |
| `hermes_state.py` | 会话存储 | `SessionDB._execute_write()` | ⭐⭐ |
| `cli.py` | CLI 主循环 | `HermesCLI.process_command()` | ⭐⭐ |
| `hermes_cli/commands.py` | 命令注册 | `CommandDef`, `COMMAND_REGISTRY` | ⭐ |
| `gateway/run.py` | 网关生命周期 | `GatewayRunner`, 适配器初始化 | ⭐⭐ |
| `agent/prompt_builder.py` | Prompt 组装 | `build_system_prompt()` | ⭐⭐⭐ |
| `agent/context_compressor.py` | 上下文压缩 | `ContextCompressor.compress()` | ⭐⭐⭐ |
| `agent/memory_manager.py` | 长期记忆 | `build_memory_context_block()` | ⭐⭐ |
| `hermes_cli/config.py` | 配置管理 | `get_hermes_home()`, `load_cli_config()` | ⭐⭐ |

---

## 总结：14 天后的你

完成这个学习计划后，你应该能够：

1. **架构理解**：闭眼画出完整的请求流程，从用户输入到模型响应到持久化
2. **工具开发**：添加新工具而不破坏现有架构，考虑到 profile、config、test、safety
3. **问题排查**：快速定位 bug 的来源（是工具、是 agent 循环、是持久化还是 CLI 分发）
4. **扩展设计**：在理解约束的基础上，提出安全的扩展方案
5. **质量保证**：写出符合项目风格的代码，考虑向后兼容性、并发安全、用户隔离
6. **贡献流程**：独立完成从需求理解到 PR 提交的全流程，包括测试与文档

祝学习顺利！🚀

