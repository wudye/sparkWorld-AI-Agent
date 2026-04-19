# ⚡ Hermes Agent 后端 - 快速参考卡

**打印版本** | 可裁剪为便签卡  
**大小**: A4 纸张  
**用途**: 学习时快速查阅，避免频繁翻文档

---

## 📌 第一周核心概念速查

### Day 01: 架构全景
```
┌─────────────────────────────────────┐
│ 4 层架构                             │
├─────────────────────────────────────┤
│ 交互层: CLI / Gateway / TUI          │
│ 编排层: AIAgent / 工具分发           │
│ 能力层: 工具 / Context / 模型        │
│ 存储层: SessionDB (SQLite + FTS5)    │
└─────────────────────────────────────┘

关键文件:
- run_agent.py (Agent 循环)
- model_tools.py (工具分发)
- tools/registry.py (工具注册)
- hermes_state.py (会话存储)
```

### Day 02: Agent 循环 ⭐ 最重要
```
while iteration < max_iterations:
    ├─ 1️⃣  组装 messages
    ├─ 2️⃣  调用模型 API
    ├─ 3️⃣  检查工具调用
    │  ├─ 有工具 → 执行 → 结果入消息
    │  └─ 无工具 → 直接返回
    └─ 循环继续

关键约束:
- IterationBudget (预算控制)
- Context Limit (文本长度)
- Prompt Cache (不能改)
```

### Day 03: 工具注册
```
自注册模式:
  tools/*.py 
    ↓ (top-level registry.register())
  registry.py 
    ↓ (get_tool_definitions())
  model_tools.py
    ↓ (handle_function_call())
  run_agent.py

工具必须:
✓ 返回 JSON 字符串
✓ 有 check_fn 验证可用性
✓ 在 toolsets.py 中注册
```

### Day 04: 会话存储
```
SQLite + FTS5 + WAL

并发写入:
  BEGIN IMMEDIATE 
    → 随机抖动重试 
    → 避免竞争队列

Schema 版本:
  V1 → V2 → V3 ... → V6
  (迁移时 backward compatible)
```

### Day 05: Prompt 与缓存
```
System Prompt 组件:
1. Agent 身份 (固定)
2. 平台提示 (固定)
3. 工具指导 (固定)
4. 记忆块 (可变)
5. 技能块 (可变)

Cache 约束:
❌ 中途改 system_prompt
❌ 中途改 tool_schemas
✅ 压缩是唯一例外
```

### Day 06: 安全防护
```
危险模式检测:
  command 
    ↓ 归一化 (ANSI/Unicode)
    ↓ 正则匹配
    ↓ 检测结果

审批流:
  CLI: input() 同步
  Gateway: Event 异步
```

### Day 07: CLI 命令
```
中央注册表:
  CommandDef (名称/别名/描述)
    ↓
  COMMAND_REGISTRY 列表
    ↓ (自动生成)
  process_command()
  GATEWAY_KNOWN_COMMANDS
  Telegram/Slack 菜单
```

---

## 📌 第二周进阶概念速查

### Day 08: Gateway 网关
```
启动顺序:
1. SSL 证书引导
2. 配置加载 (.yaml → env)
3. SessionDB 初始化
4. 平台适配器启动
5. 事件循环

配置桥接:
  config.yaml 
    → (terminal.*) 
    → TERMINAL_* env vars
    → 下游代码读取
```

### Day 09: Profile 隔离
```
Profile 目录:
  ~/.hermes/              (default)
  ~/.hermes/profiles/work/
  ~/.hermes/profiles/personal/

关键函数:
  _apply_profile_override()  ← 早期调用
  get_hermes_home()          ← 代码使用
  display_hermes_home()      ← 用户展示

❌ 不要: Path.home() / ".hermes"
✅ 要用: get_hermes_home()
```

### Day 10: 学习系统
```
三种记忆:
1. 会话记忆 (SessionDB)
2. 长期记忆 (MemoryManager)
3. 轨迹数据 (trajectory.py)

技能: ~/.hermes/skills/*.py
  ↓ 自动发现
  ↓ 注入 system prompt
```

### Day 11: 异步并发
```
Sync-Async 桥接:
  场景 1: Gateway 已有循环
    → ThreadPool 中转
  
  场景 2: Worker 线程
    → 独立持久循环
  
  场景 3: CLI 主线程
    → 共享持久循环

并行工具:
  ✓ web_search, read_file
  ❌ clarify (交互式)
```

### Day 12: 测试质量
```
❌ 不要: python -m pytest ...
✅ 要用: scripts/run_tests.sh

隔离三层:
1. HERMES_HOME → tmp
2. API_KEY → 全部清除
3. TZ=UTC, LANG=C.UTF-8

Fixture:
  _isolate_hermes_home
  _clean_environment
  mock_session_db
```

### Day 13: 模型路由
```
Context 溢出处理:
  接近 90%
    ├─ 能降级? → 降低模型
    ├─ 能压缩? → 压缩 context
    └─ 都不行 → 失败

降级链:
  gpt-4-turbo → gpt-3.5-turbo
  claude-opus → claude-haiku
```

### Day 14: 综合实战
```
完整项目流程:
1. 需求分析 (1 h)
2. 设计实现 (3 h)
3. 单元测试 (1.5 h)
4. 文档集成 (0.5 h)

交付物:
✓ 代码 + 测试
✓ 文档说明
✓ 无 bug 无回归
```

---

## 🎯 快速决策树

### 问题: 不知道从哪开始
```
→ 打开 START-HERE.zh.md
→ 5 分钟快速开始
→ 按提示选择学习路径
```

### 问题: 某个概念理解不了
```
查 backendclaude.md
  ↓ (按目录搜索关键词)
  ├─ 没找到 → 找对应的 Day XX
  └─ 找到了 → 阅读 + 代码追踪
```

### 问题: 实践任务不会做
```
Day XX 的"实践任务"
  ↓ (阅读要求)
  ├─ 还不会 → 查"学习内容"
  └─ 明白了 → 打断点调试
```

### 问题: 遇到 bug 或错误
```
错误信息
  ↓ (提取关键词)
  ├─ 工具错误 → Day 03/06
  ├─ 会话错误 → Day 04
  ├─ 网关错误 → Day 08
  └─ 测试错误 → Day 12
```

---

## 📊 学习时间表

| 周 | 日期 | Day | 主题 | 时间 | 累计 |
|----|------|-----|------|------|------|
| W1 | Mon | 01 | 架构 | 3h | 3h |
| W1 | Tue | 02 | 循环 | 4h | 7h |
| W1 | Wed | 03 | 工具 | 3.5h | 10.5h |
| W1 | Thu | 04 | 存储 | 3.5h | 14h |
| W1 | Fri | 05 | Prompt | 3h | 17h |
| W1 | Sat | 06 | 安全 | 3.5h | 20.5h |
| W1 | Sun | 07 | CLI | 3h | 23.5h |
| W2 | Mon | 08 | 网关 | 3.5h | 27h |
| W2 | Tue | 09 | Profile | 3.5h | 30.5h |
| W2 | Wed | 10 | 学习 | 3h | 33.5h |
| W2 | Thu | 11 | 异步 | 4h | 37.5h |
| W2 | Fri | 12 | 测试 | 3.5h | 41h |
| W2 | Sat | 13 | 模型 | 3h | 44h |
| W2 | Sun | 14 | 实战 | 6h | 50h |

---

## 📋 每日清单模板

**Day XX: [主题]**

今日目标:
- [ ] 读"学习内容"
- [ ] 完成 4 个实践任务
- [ ] 运行测试验证
- [ ] 写学习笔记

时间投入: 3-4 小时

进度:
```
[████████░░░░░░░░░░░░] 40% 完成
```

遇到问题:
- _____________________
- _____________________

心得体会:
- _____________________
- _____________________

---

## 🚀 重要提醒

### ⚠️ 必须遵守
1. ✅ **按顺序学**: Day 01 → Day 02 → ...
2. ✅ **动手实践**: 不仅看，还要打代码
3. ✅ **用 wrapper**: `scripts/run_tests.sh` 不要直接 pytest
4. ✅ **避免硬编码**: `get_hermes_home()` 不要 `Path.home() / ".hermes"`

### 💡 高效学习
1. 🎯 **单点突破**: 一天只学一个概念
2. 📖 **多源理解**: 代码 + 文档 + 测试 对比阅读
3. 🐛 **边界测试**: 不仅正常情况，还要测试异常
4. 📝 **记笔记**: 手写能强化记忆

### 🎓 完成后
1. 回顾: 重新走一遍全流程
2. 实践: 改进某个现有功能
3. 贡献: 提交你的第一个 PR
4. 分享: 写学习总结分享他人

---

## 🔗 快速链接

| 需求 | 文件 | 时间 |
|------|------|------|
| 第一次使用 | START-HERE.zh.md | 5 min |
| 学习导航 | LEARNING-INDEX.zh.md | 10 min |
| 深度参考 | backendclaude.md | 按需 |
| 文件清单 | FILE-INVENTORY.zh.md | 15 min |
| 今天任务 | backend-learning-day-XX.zh.md | 3-4 h |

---

## ✨ 成功标志

完成 14 天学习后，你应该:

- ✅ 能解释 Agent 循环的每一步
- ✅ 能添加一个新工具
- ✅ 能设计新功能而不破坏架构
- ✅ 能写出符合规范的代码
- ✅ 能提交生产级 PR
- ✅ 能指导其他人学习这个项目

---

**打印建议**:
- 裁剪成 A5 大小（半张 A4）
- 用便签夹固定
- 学习时放在显示器旁边
- 遇到问题快速查阅

祝学习顺利！🚀

