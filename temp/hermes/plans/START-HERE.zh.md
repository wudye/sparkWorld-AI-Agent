# 🚀 Hermes Agent 后端学习 - 快速开始

> 你有：1 份深度分析 + 14 份学习计划 + 完整的工程指南

## ⚡ 5 分钟快速开始

### 第 0 步：了解你得到什么
- ✅ `backendclaude.md` - 11,000 字深度分析
- ✅ 14 份学习计划 - `plans/backend-learning-day-01-14.zh.md`
- ✅ 学习索引 - `LEARNING-INDEX.zh.md`

### 第 1 步：打开 LEARNING-INDEX.zh.md
这是你的**导航地图**，5 分钟了解全貌。

### 第 2 步：选择你的学习时间
```
有 3 小时？   → Day 01（今天开始）
有 1 周？     → Day 01-07（第一周核心）
有 2 周？     → Day 01-14（完整学习）
```

### 第 3 步：按顺序开始
```
Day 01 → 打开 backend-learning-day-01-foundations.zh.md
         按"学习内容"读
         完成 4-5 个"实践任务"
         写学习笔记

Day 02 → 重复上面的流程
...
```

---

## 📋 17 份文档的快速检索

| 需求 | 文件 |
|------|------|
| 想要完整参考 | `backendclaude.md` |
| 想要中文快速版 | `backend.zh.md` |
| 想要全体系指南 | `LEARNING-INDEX.zh.md` |
| 想要今天的任务 | `backend-learning-day-XX.zh.md` |

---

## 🎯 今天应该做什么

### 如果你有 3 小时
```
1. 打开 LEARNING-INDEX.zh.md（5 分钟）
2. 打开 backendclaude.md（20 分钟）
3. 打开 backend-learning-day-01-foundations.zh.md（120 分钟）
   ├─ 阅读"学习内容"
   ├─ 完成"实践任务 1"（架构图绘制）
   ├─ 完成"实践任务 2"（依赖链拓扑）
   └─ 完成"实践任务 3"（文件清点）
4. 写学习笔记（30 分钟）

总结：今天你能理解项目的 4 层架构与依赖链
```

### 如果你有 30 分钟
```
1. 打开 LEARNING-INDEX.zh.md（5 分钟）
2. 打开 backendclaude.md，读"第一部分：后端分层架构"（15 分钟）
3. 打开 backend-learning-day-01-foundations.zh.md，读"学习内容"（10 分钟）

总结：了解项目的基本架构
```

---

## 📚 14 天的高层路线图

```
Week 1: 基础知识
├─ Day 01: 架构全景
├─ Day 02: Agent 循环 ⭐ （最核心）
├─ Day 03: 工具注册
├─ Day 04: 会话存储
├─ Day 05: Prompt 管理
├─ Day 06: 安全防护
└─ Day 07: CLI 命令

Week 2: 深度与实战
├─ Day 08: Gateway 网关
├─ Day 09: Profile 隔离
├─ Day 10: 学习系统
├─ Day 11: 异步并发
├─ Day 12: 测试质量 ⭐
├─ Day 13: 模型路由
└─ Day 14: 综合实战 ⭐ （完成一个真实工具）
```

---

## 🔥 3 个核心重点

### ⭐ Day 02 - Agent 循环
- 最重要的一天
- 理解 `run_conversation()` 的每一步
- 如果你只看一个，看这个

### ⭐ Day 12 - 测试质量
- 学会用 `scripts/run_tests.sh`
- 理解为什么不能直接 pytest
- 避免"本地通过，CI 失败"

### ⭐ Day 14 - 综合实战
- 完整的工程项目
- 从需求到部署的全流程
- 完成后能提交真实 PR

---

## 💾 文件位置与导航

```
项目根目录/
├── backendclaude.md             ← 从这里开始
├── backend.zh.md
├── LEARNING-INDEX.zh.md
└── plans/
    ├── backend-learning-day-01-foundations.zh.md
    ├── backend-learning-day-02-agent-loop.zh.md
    ├── backend-learning-day-03-tool-registry.zh.md
    ... （Day 04-14）
    └── backend-learning-day-14-capstone.zh.md

+ 项目源码/
  ├── run_agent.py
  ├── model_tools.py
  ├── tools/
  ├── hermes_cli/
  ├── gateway/
  └── ... （其他）
```

---

## 🎓 学习方式

### 推荐（最有效）
```
1️⃣  读 Day XX 的计划（20 分钟）
2️⃣  参考 backendclaude.md 的相关章节（30 分钟）
3️⃣  在 IDE 中追踪源码（60 分钟）
4️⃣  完成实践任务（90 分钟）
5️⃣  写学习笔记（30 分钟）

总计：3-3.5 小时/天，持续 14 天
```

### 快速版（基础理解）
```
1️⃣  读 backendclaude.md（2 小时）
2️⃣  浏览 Day 01-07 的计划（1 小时）

总计：3 小时，获得基本理解
```

### 深度版（完全精通）
```
1️⃣  完整学习 Day 01-14（49 小时）
2️⃣  做 Day 14 的综合项目（6 小时）
3️⃣  提交真实 PR（2 小时）

总计：57 小时，成为项目贡献者
```

---

## ❓ 我应该选哪个版本？

### 你是初学者？
→ **推荐：快速版**（3 小时）
- 先快速了解全貌
- 再按需深入学习

### 你想深入掌握？
→ **推荐：标准版**（14 天）
- 每天 3 小时的投入
- 获得完整的知识体系

### 你想成为贡献者？
→ **推荐：完全版**（2 周 + 实战）
- 完整 14 天学习
- + Day 14 的综合项目
- = 能提交生产 PR

---

## 🚀 现在就开始

### 第一步：打开这些文件

**在你的 IDE 中按这个顺序打开：**

1. `LEARNING-INDEX.zh.md` - 了解全貌（5 分钟）
2. `backendclaude.md` - 深度参考（根据需求查阅）
3. `backend-learning-day-01-foundations.zh.md` - 今天的任务

### 第二步：按照 Day 01 的计划

遵循这个流程：
```
📖 读"学习内容" 
  ↓
💻 打开 VS Code
  ↓
📝 追踪 run_agent.py 代码
  ↓
✅ 完成 4 个实践任务
  ↓
📋 写学习笔记
```

### 第三步：明天继续 Day 02

重复相同的流程，学习 Agent 循环。

---

## 💡 成功的秘诀

1. ✅ **按顺序学** - 不要跳过
2. ✅ **有时间表** - 每天 3 小时
3. ✅ **手脑并用** - 不仅读，还要打断点调试
4. ✅ **写笔记** - 强化记忆
5. ✅ **做实践** - 不仅看例子，还要写代码

---

## 📞 需要帮助？

| 问题 | 解决方案 |
|------|--------|
| 不知道从哪开始 | → 打开 `LEARNING-INDEX.zh.md` |
| 某个概念不理解 | → 查 `backendclaude.md` 的对应章节 |
| 实践任务不会做 | → 打断点调试 + 查看项目的测试文件 |
| 想要快速了解 | → 读 `backendclaude.md` 的"第一部分" |
| 想要深入学习 | → 按 Day 01-14 的顺序学习 |

---

## ✨ 预期收获

完成这个学习套件后，你将能够：

- ✅ 理解 Hermes Agent 的完整后端架构
- ✅ 独立添加新工具或功能
- ✅ 遵循项目约束编写高质量代码
- ✅ 通过完整的工程流程（设计→实现→测试→文档）
- ✅ 提交生产级的 PR
- ✅ 成为项目的活跃贡献者

---

## 🎊 开始吧！

你已经准备好了。

现在：
1. 打开 `LEARNING-INDEX.zh.md`
2. 打开 `backend-learning-day-01-foundations.zh.md`
3. 开始学习

**14 天后，你将成为 Hermes Agent 后端的专家。**

祝你学习顺利！🚀

