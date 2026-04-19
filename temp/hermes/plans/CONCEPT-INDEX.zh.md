# 🎓 Hermes Agent 后端 - 核心概念索引

**用途**: 快速定位特定概念、理解架构关系、查找学习资源

---

## 🏛️ 架构层级索引

### 交互层（User-Facing）
```
┌─────────────────────────────────────────────┐
│              交互层                         │
├─────────────────────────────────────────────┤
│ CLI              Gateway         TUI        │
│ (prompt_toolkit) (async)         (Ink)     │
└─────────────────────────────────────────────┘

概念:
  - HermesCLI class
  - GatewayRunner async
  - TUI server + frontend

对应文件:
  - cli.py
  - gateway/run.py
  - tui_gateway/

学习资源:
  - Day 07 (CLI)
  - Day 08 (Gateway)
  - backendclaude.md 第 5.5 部分
```

### 编排层（Business Logic）
```
┌─────────────────────────────────────────────┐
│              编排层                         │
├─────────────────────────────────────────────┤
│ AIAgent         Model Tools    Prompt     │
│ (run_conversation) (dispatch)   (build)   │
└─────────────────────────────────────────────┘

概念:
  - Agent 循环
  - 工具分发
  - 消息组装

对应文件:
  - run_agent.py
  - model_tools.py
  - agent/prompt_builder.py

学习资源:
  - Day 02 (Agent)
  - Day 03 (Tools)
  - Day 05 (Prompt)
  - backendclaude.md 第 2-5 部分
```

### 能力层（Features & Tools）
```
┌─────────────────────────────────────────────┐
│              能力层                         │
├─────────────────────────────────────────────┤
│ 工具      Context/Memo  模型/路由 安全   │
│ (registry) (builder)     (metadata) (approval) │
└─────────────────────────────────────────────┘

概念:
  - 自注册工具
  - Context 压缩
  - 模型元数据
  - 危险命令检测

对应文件:
  - tools/
  - agent/context_compressor.py
  - agent/model_metadata.py
  - tools/approval.py

学习资源:
  - Day 03-06
  - Day 10, 13
  - backendclaude.md 第 5.2-5.7 部分
```

### 存储层（Data Persistence）
```
┌─────────────────────────────────────────────┐
│              存储层                         │
├─────────────────────────────────────────────┤
│ SessionDB           State Management      │
│ (SQLite + FTS5)     (memory, skills)     │
└─────────────────────────────────────────────┘

概念:
  - WAL 模式
  - FTS5 索引
  - 会话链
  - 并发安全

对应文件:
  - hermes_state.py
  - agent/memory_manager.py
  - gateway/session.py

学习资源:
  - Day 04
  - Day 10
  - backendclaude.md 第 5.4 部分
```

---

## 🔄 关键流程索引

### 请求处理流程
```
用户输入
  ↓ (解析)
HermesCLI / GatewayRunner
  ↓ (创建或获取)
AIAgent instance
  ↓ (调用)
run_conversation()
  ├─ 组装 messages
  ├─ 调用模型
  ├─ 分发工具 (handle_function_call)
  ├─ 执行工具 (registry.dispatch)
  └─ 返回结果
    ↓ (持久化)
SessionDB
  ↓ (展示)
用户结果

相关文件:
  - cli.py (CLI 路径)
  - gateway/run.py (Gateway 路径)
  - run_agent.py (Agent 循环)
  - model_tools.py (工具分发)

学习资源:
  - Day 01 (全流程)
  - Day 02 (循环)
  - Day 03 (工具分发)
  - Day 04 (持久化)
```

### 工具执行流程
```
Agent 决定调用工具
  ↓
response.tool_calls 列表
  ↓ (遍历每个调用)
handle_function_call(name, args)
  ↓ (查询注册表)
registry.get_entry(name)
  ↓ (检查可用性)
entry.check_fn()
  ├─ 不可用 → 返回错误
  └─ 可用 → 执行
    ↓
entry.handler(args)
  ├─ 同步 → 直接运行
  └─ 异步 → _run_async()
    ↓ (结果必须是 JSON)
返回 JSON 字符串
  ↓ (追加到 messages)
继续循环

相关文件:
  - run_agent.py (调用点)
  - model_tools.py (分发)
  - tools/registry.py (查询)
  - tools/*.py (实现)

学习资源:
  - Day 03 (注册)
  - Day 06 (执行)
  - Day 11 (异步)
  - backendclaude.md 第 2.2 部分
```

### 会话持久化流程
```
Agent 循环运行
  ↓ (每个 turn 后)
构建消息结构
  {
    session_id: "xxx",
    role: "user/assistant/tool",
    content: "...",
    timestamp: 1234567890
  }
  ↓ (加入队列)
db.save_message()
  ├─ 获取 WAL 写锁
  ├─ INSERT INTO messages
  ├─ 自动更新 FTS5
  └─ 释放锁
    ↓
消息持久化完成
  ↓ (可用于搜索/回溯)

相关文件:
  - run_agent.py (save 调用)
  - hermes_state.py (SessionDB)
  - SQLite schema

学习资源:
  - Day 04 (存储)
  - backendclaude.md 第 5.4 部分
```

---

## 💾 关键概念速查表

### Agent 相关
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| AIAgent | 对话循环控制器 | run_agent.py | 02 |
| run_conversation | 主循环函数 | run_agent.py L8668 | 02 |
| IterationBudget | 迭代预算管理 | run_agent.py L150 | 02 |
| iteration | 循环计数 | run_agent.py | 02 |
| message | 单条对话消息 | run_agent.py | 02 |

### 工具相关
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| registry | 工具注册表 | tools/registry.py | 03 |
| ToolEntry | 工具元数据 | tools/registry.py L27 | 03 |
| toolset | 工具分组 | toolsets.py | 03 |
| handler | 工具执行函数 | tools/*.py | 03 |
| schema | 工具参数定义 | tools/*.py | 03 |

### 存储相关
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| SessionDB | 会话存储 | hermes_state.py | 04 |
| WAL | Write-Ahead Log | hermes_state.py | 04 |
| FTS5 | 全文搜索 | hermes_state.py | 04 |
| session_id | 会话标识 | hermes_state.py | 04 |
| schema_version | 数据库版本 | hermes_state.py | 04 |

### Prompt 相关
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| system_prompt | 系统提示 | agent/prompt_builder.py | 05 |
| prompt_cache | 缓存机制 | agent/prompt_caching.py | 05 |
| ContextCompressor | 压缩工具 | agent/context_compressor.py | 05 |
| cache_control | 缓存标记 | agent/prompt_caching.py | 05 |

### 安全相关
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| DANGEROUS_PATTERNS | 危险模式 | tools/approval.py L67 | 06 |
| detect_dangerous | 检测函数 | tools/approval.py | 06 |
| _ApprovalEntry | 待审批条目 | tools/approval.py L203 | 06 |
| allowlist | 永久白名单 | tools/approval.py | 06 |

### 网关相关
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| GatewayRunner | 网关主类 | gateway/run.py | 08 |
| platform adapter | 平台适配器 | gateway/platforms/*.py | 08 |
| session_key | 会话键 | gateway/session.py | 08 |
| _agent_cache | Agent 缓存 | gateway/run.py | 08 |

### Profile 相关
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| HERMES_HOME | 实例主目录 | hermes_constants.py | 09 |
| get_hermes_home | 获取路径 | hermes_constants.py | 09 |
| display_hermes_home | 展示路径 | hermes_constants.py | 09 |
| _apply_profile_override | Profile 应用 | hermes_cli/main.py | 09 |

### 学习系统
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| MemoryManager | 记忆管理 | agent/memory_manager.py | 10 |
| Trajectory | 轨迹数据 | agent/trajectory.py | 10 |
| skill | 自定义技能 | agent/skill_commands.py | 10 |

### 异步并发
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| _run_async | 异步桥接 | model_tools.py L38 | 11 |
| _get_tool_loop | 工具循环 | model_tools.py L52 | 11 |
| _PARALLEL_SAFE_TOOLS | 并行工具 | run_agent.py L216 | 11 |

### 测试质量
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| scripts/run_tests.sh | CI wrapper | scripts/run_tests.sh | 12 |
| conftest.py | 测试配置 | tests/conftest.py | 12 |
| _isolate_hermes_home | 隔离 fixture | tests/conftest.py | 12 |

### 模型路由
| 概念 | 定义 | 文件 | Day |
|------|------|------|-----|
| MODEL_METADATA | 模型元数据 | agent/model_metadata.py | 13 |
| context_length | Context 长度 | agent/model_metadata.py | 13 |
| estimate_tokens | Token 估算 | agent/model_metadata.py | 13 |
| classify_api_error | 错误分类 | agent/error_classifier.py | 13 |

---

## 🔍 按主题分类索引

### 如果你想学...

#### ...如何添加新工具
```
学习顺序:
1. Day 03 (工具注册) - 基础
2. 参考 tools/web_tools.py - 实例
3. backendclaude.md 第 8 部分 - 扩展
4. Day 14 综合项目 - 实战

关键文件:
- tools/registry.py (注册机制)
- toolsets.py (分组)
- model_tools.py (分发)
```

#### ...如何改进性能
```
学习顺序:
1. Day 04 (会话存储)
2. Day 05 (Prompt 压缩)
3. Day 13 (模型路由)
4. backendclaude.md 第 7 部分

关键瓶颈:
- SessionDB 查询
- 消息序列化
- Context 大小
- 模型选择
```

#### ...如何支持新平台
```
学习顺序:
1. Day 08 (Gateway)
2. 参考 gateway/platforms/telegram.py
3. 继承 platform adapter 接口
4. 与 SessionDB 集成

关键文件:
- gateway/run.py
- gateway/platforms/*.py
- gateway/session.py
```

#### ...如何确保多实例隔离
```
学习顺序:
1. Day 09 (Profile)
2. backendclaude.md 第 6 部分
3. hermes_constants.py 代码
4. hermes_cli/config.py 代码

黄金规则:
- 用 get_hermes_home() 不要硬编码路径
- 每个 profile 独立 HERMES_HOME
- 配置/密钥/数据全部隔离
```

#### ...如何保证测试稳定
```
学习顺序:
1. Day 12 (测试)
2. scripts/run_tests.sh 脚本
3. tests/conftest.py fixture
4. backendclaude.md 第 9 部分

关键约束:
- 用 scripts/run_tests.sh
- 环境完全隔离 (TZ, LANG, API_KEY)
- 并发度固定 (-n 4)
```

---

## 🎯 问题解决索引

### 常见问题与对应资源

| 问题 | 症状 | 原因 | 解决方案 | 资源 |
|------|------|------|--------|------|
| 工具不被识别 | Agent 看不到工具 | toolset 未启用 | 检查 enabled_toolsets | Day 03 |
| Agent 卡住 | 循环不终止 | iteration >= max | 检查终止条件 | Day 02 |
| 会话丢失 | 重启后消息没了 | SessionDB 未保存 | 检查 save_message | Day 04 |
| Cache 破坏 | Token 成本猛增 | 中途改 system prompt | 使用 compression | Day 05 |
| 权限拒绝 | 危险命令被拒 | 在 approval allowlist | 使用 /approve | Day 06 |
| 命令找不到 | /unknown 命令 | CommandDef 未注册 | 检查 registry | Day 07 |
| 平台连接错 | Gateway 无消息 | adapter 未启动 | 检查日志 | Day 08 |
| 配置冲突 | 多 profile 互相影响 | HERMES_HOME 混淆 | 检查路径隔离 | Day 09 |
| 测试不稳定 | 本地通过 CI 失败 | 环境不一致 | 用 wrapper 脚本 | Day 12 |

---

## 📚 文件交叉引用

```
run_agent.py
  ├─ 依赖: model_tools.py
  ├─ 依赖: agent/prompt_builder.py
  ├─ 依赖: tools/approval.py
  └─ 调用: SessionDB.save_message()

model_tools.py
  ├─ 导入: tools/registry.py
  ├─ 调用: discover_builtin_tools()
  └─ 提供: handle_function_call()

gateway/run.py
  ├─ 依赖: hermes_cli/config.py
  ├─ 导入: gateway/platforms/*.py
  ├─ 创建: AIAgent instance
  └─ 使用: SessionDB

hermes_cli/commands.py
  ├─ 定义: CommandDef registry
  ├─ 被消费: cli.py
  ├─ 被消费: gateway/run.py
  └─ 被消费: 各平台 adapter
```

---

## 🎓 学习路径推荐

### 如果你是...

**初学者**（需要 3 小时）
```
START-HERE.zh.md (5 min)
  ↓
backendclaude.md 第 1-2 部分 (30 min)
  ↓
IDE 追踪 run_agent.py (120 min)
  ↓
基本理解项目
```

**进阶学习者**（需要 49 小时）
```
LEARNING-INDEX.zh.md (10 min)
  ↓
Day 01-14 按顺序 (49 h)
  ↓
掌握完整后端
```

**专业贡献者**（需要 57 小时）
```
完整 14 天学习 (49 h)
  ↓
backendclaude.md 深度阅读 (2 h)
  ↓
Day 14 综合项目 (6 h)
  ↓
准备贡献 PR
```

---

## ✨ 本索引的使用方式

1. **遇到陌生概念** → 在本索引中查找
2. **找到相关概念** → 查看对应文件和 Day
3. **打开对应资源** → 深入学习
4. **遇到类似问题** → 回到本索引快速参考

**打印建议**: 裁剪成 A4 大小，与 QUICK-REFERENCE.zh.md 一起保存。

祝学习顺利！🚀

