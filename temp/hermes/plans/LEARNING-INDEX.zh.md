# Hermes Agent 后端完整学习指南 - 索引

## 📚 核心文档

| 文件 | 说明 | 用途 |
|------|------|------|
| **backendclaude.md** | 深度分析报告（9000+ 字） | 14 天学习的完整参考指南 |
| **backend.zh.md** | 中文版本（简化） | 快速参考架构 |

---

## 🎯 14 天学习计划（完整版）

### **第一周：核心知识基础**

#### Day 01 - 项目全景与依赖链（基础地基日）
📄 `plans/backend-learning-day-01-foundations.zh.md`
- **学习目标**：建立全局心智模型
- **关键概念**：4 层架构、5 个入口点、依赖链拓扑
- **实践**：架构图绘制、文件清点
- **时间**：3 小时
- **前置**：无

#### Day 02 - Agent 循环核心解剖（最重要的一天）
📄 `plans/backend-learning-day-02-agent-loop.zh.md`
- **学习目标**：完全理解 run_conversation() 内部机制
- **关键概念**：消息循环、IterationBudget、工具分发
- **实践**：流程追踪、单元测试、错误处理改进
- **时间**：4 小时
- **前置**：Day 01

#### Day 03 - 工具注册与分发机制
📄 `plans/backend-learning-day-03-tool-registry.zh.md`
- **学习目标**：学会添加新工具而不破坏架构
- **关键概念**：自注册模式、Registry、Toolset 机制
- **实践**：创建 Dummy 工具、理解 Schema 约束
- **时间**：3.5 小时
- **前置**：Day 02

#### Day 04 - 会话持久化与 SessionDB
📄 `plans/backend-learning-day-04-sessiondb.zh.md`
- **学习目标**：掌握 SQLite + FTS5 + WAL 的并发安全设计
- **关键概念**：WAL 模式、FTS5 索引、竞争控制
- **实践**：并发测试、Schema 迁移、高级查询
- **时间**：3.5 小时
- **前置**：Day 01

#### Day 05 - Prompt 构建与 Context 压缩
📄 `plans/backend-learning-day-05-prompt-context.zh.md`
- **学习目标**：理解 Prompt 与 Cache 的交互
- **关键概念**：System Prompt 组件、Cache 约束、压缩流程
- **实践**：组件分析、简单压缩器实现、Cache 测试
- **时间**：3 小时
- **前置**：Day 02

#### Day 06 - 危险命令检测与审批机制
📄 `plans/backend-learning-day-06-approval.zh.md`
- **学习目标**：掌握安全防护的核心机制
- **关键概念**：模式识别、审批流、CLI vs Gateway 差异
- **实践**：模式覆盖分析、新增模式、集成测试
- **时间**：3.5 小时
- **前置**：Day 03

#### Day 07 - CLI 命令分发与配置管理
📄 `plans/backend-learning-day-07-cli-commands.zh.md`
- **学习目标**：理解命令中央注册表与配置优先级
- **关键概念**：CommandDef、配置加载链、Profile 隔离
- **实践**：新增命令、配置优先级演示、Profile 测试
- **时间**：3 小时
- **前置**：Day 01

---

### **第二周：扩展与运维深度**

#### Day 08 - Gateway 与多平台适配器
📄 `plans/backend-learning-day-08-gateway.zh.md`
- **学习目标**：理解网关生命周期与平台适配
- **关键概念**：启动序列、配置桥接、Agent 缓存、适配器接口
- **实践**：配置表、Debug 适配器、并发测试
- **时间**：3.5 小时
- **前置**：Day 01, 07

#### Day 09 - Profile 隔离与多实例架构
📄 `plans/backend-learning-day-09-profiles.zh.md`
- **学习目标**：掌握多实例安全隔离
- **关键概念**：Profile 目录、get_hermes_home()、路径隔离
- **实践**：多 Profile 创建、路径隔离验证、Bug 修复
- **时间**：3.5 小时
- **前置**：Day 01, 07

#### Day 10 - 记忆、技能与轨迹系统
📄 `plans/backend-learning-day-10-learning-systems.zh.md`
- **学习目标**：理解长期学习机制
- **关键概念**：MemoryManager、技能发现、轨迹数据
- **实践**：记忆管理、自定义技能、轨迹分析
- **时间**：3 小时
- **前置**：Day 02

#### Day 11 - 异步桥接与并发模型
📄 `plans/backend-learning-day-11-async-concurrency.zh.md`
- **学习目标**：掌握 sync-async 交互与资源管理
- **关键概念**：事件循环、并行工具执行、子代理隔离
- **实践**：异步工具实现、并发压力测试、资源泄漏识别
- **时间**：4 小时
- **前置**：Day 02, 03

#### Day 12 - 测试策略与质量保证
📄 `plans/backend-learning-day-12-testing-quality.zh.md`
- **学习目标**：掌握 CI 一致性与测试驱动开发
- **关键概念**：测试隔离、wrapper 脚本、fixture 设计
- **实践**：环境隔离验证、单元测试编写、覆盖率分析
- **时间**：3.5 小时
- **前置**：Day 01

#### Day 13 - 模型路由与元数据管理
📄 `plans/backend-learning-day-13-model-routing.zh.md`
- **学习目标**：理解模型选择与成本优化
- **关键概念**：模型元数据、Context 溢出处理、智能路由
- **实践**：模型对比表、成本估算、降级策略设计
- **时间**：3 小时
- **前置**：Day 02

#### Day 14 - 综合实战：完成一个真实功能
📄 `plans/backend-learning-day-14-capstone.zh.md`
- **学习目标**：整合前 13 天知识，完成端到端功能
- **推荐项目**：添加 JSON Validator 工具
- **交付物**：完整的工具实现 + 测试 + 文档
- **时间**：6 小时
- **前置**：Day 02, 03, 12

---

## 🗂️ 文件结构总览

```
H:\hermes-agent-main\hermes-agent-main\
├── backendclaude.md                          # ⭐ 深度分析报告
├── backend.zh.md                             # 中文快速参考
└── plans/
    ├── backend-learning-day-01-foundations.zh.md
    ├── backend-learning-day-02-agent-loop.zh.md
    ├── backend-learning-day-03-tool-registry.zh.md
    ├── backend-learning-day-04-sessiondb.zh.md
    ├── backend-learning-day-05-prompt-context.zh.md
    ├── backend-learning-day-06-approval.zh.md
    ├── backend-learning-day-07-cli-commands.zh.md
    ├── backend-learning-day-08-gateway.zh.md
    ├── backend-learning-day-09-profiles.zh.md
    ├── backend-learning-day-10-learning-systems.zh.md
    ├── backend-learning-day-11-async-concurrency.zh.md
    ├── backend-learning-day-12-testing-quality.zh.md
    ├── backend-learning-day-13-model-routing.zh.md
    └── backend-learning-day-14-capstone.zh.md
```

---

## 📋 每天的学习结构

每份计划包含：

1. **目标** - 今天要学会什么
2. **关键文件** - 需要阅读的源码
3. **学习内容** - 概念讲解 + 代码示例
4. **实践任务** - 4-5 个具体任务
5. **风险点** - 注意什么
6. **交付物** - 要完成什么
7. **验收标准** - 如何判断学懂了

---

## 💡 学习建议

### 时间分配
```
周一-周五：每天 3-4 小时
周末：可选补课或深入研究

总计：14 天 × 3.5 小时 ≈ 49 小时
```

### 学习方式
```
1. 先读对应的 Day 计划（20 分钟）
2. 阅读 backendclaude.md 的相关章节（30 分钟）
3. 在 IDE 中打开源码，单步追踪（60 分钟）
4. 完成 4-5 个实践任务（120-150 分钟）
5. 写学习笔记（30 分钟）
```

### 工具准备
```
必需：
- VS Code / PyCharm / Vim
- Python 3.10+
- Git

可选但推荐：
- SQLite Browser（查看数据库）
- Postman 或 curl（测试 API）
- Claude 或 ChatGPT（辅助理解）
```

---

## 🚀 14 天后的预期产出

### 知识维度
- ✅ 理解完整的 Agent 循环与工具调用机制
- ✅ 掌握工具注册、分发与执行的全流程
- ✅ 理解会话持久化与并发安全
- ✅ 学会 Prompt 构建与 Context 管理
- ✅ 理解多平台网关的设计与实现
- ✅ 掌握 Profile 隔离与配置治理
- ✅ 学会测试驱动开发与质量保证

### 能力维度
- ✅ 能独立新增一个完整的后端工具
- ✅ 能改进现有功能而不破坏架构
- ✅ 能诊断和修复 bug
- ✅ 能优化性能和成本
- ✅ 能遵循项目约束编写高质量代码

### 贡献准备
- ✅ 理解项目的设计理念与架构约束
- ✅ 遵循编码规范与最佳实践
- ✅ 能编写清晰的 commit message 与 PR 说明
- ✅ 能独立完成从需求到交付的全流程

---

## ❓ 常见问题

### Q: 可以跳过某些天吗？
**A**: 强烈不建议。Day 02（Agent 循环）和 Day 03（工具注册）是基础中的基础。其他天可以根据兴趣调整顺序，但不要跳过。

### Q: 如果某天卡住了怎么办？
**A**: 
1. 再读一遍该天的"学习内容"部分
2. 用 Claude 或 ChatGPT 提问（参考 backendclaude.md 的问题示例）
3. 在 IDE 中打断点调试，单步执行
4. 查看项目的测试文件（tests/）获得更多例子

### Q: 能在 Windows 上学习吗？
**A**: 可以，但项目主要在 Linux/macOS 上运行。建议：
- 用 WSL 2（Windows Subsystem for Linux）
- 或者用 Docker 容器
- 或者在 Linux 虚拟机上

### Q: 14 天后能直接提交生产 PR 吗？
**A**: 可以！Day 14 就是完成一个端到端的功能。建议：
- 先提交一个小功能（如新工具）
- 等待 Review 与反馈
- 在第二轮改进中学到更多

### Q: 有视频教程吗？
**A**: 没有，这个项目太新了。但：
- 代码本身就是最好的教程
- backendclaude.md 中的伪代码很详细
- 项目的 AGENTS.md 有补充说明

---

## 📞 获取帮助

如果你：
- 对某个概念有疑问 → 查阅 backendclaude.md 的对应章节
- 不知道怎么开始 → 从 Day 01 开始，按顺序
- 想更深入理解 → 查看项目的测试文件（tests/）
- 遇到代码问题 → 在 IDE 中打断点，单步调试
- 需要额外资源 → 参考每天计划中的"关键文件"列表

---

## 🎓 学完后的建议

1. **回顾** - 花 1-2 小时重新走一遍完整的请求流程
2. **实践** - 尝试改进一个现有功能（优化性能、加强安全等）
3. **贡献** - 找一个 issue，提交你的第一个真实 PR
4. **分享** - 写一篇学习笔记，分享给团队

---

## ✨ 最后的话

Hermes Agent 是一个设计精良、约束明确的项目。这 14 天的学习不仅仅是学习一个项目，更是学习：
- 如何设计可扩展的架构
- 如何编写可维护的代码
- 如何在复杂系统中思考
- 如何从零快速成长为贡献者

祝你学习顺利！🚀

有任何问题或反馈，欢迎随时提问。

