# 🚀 快速开始 - 5分钟入门

这是最快速的入门方式。选择你想做的事：

---

## 选项 1：我想从零创建完整项目（60-90 分钟）

如果你想从**完全空白状态**创建一个全新的 DeerFlow 项目：

### 第一步：查看快速参考

```
👉 打开: docs/plan/quick-reference.md
```

这个文件包含所有你需要的命令和代码片段。

### 第二步：按照命令执行

```powershell
# 创建项目
mkdir C:\projects\deerflow-new
cd C:\projects\deerflow-new

# 初始化后端
cd backend
uv init --name deerflow-backend

# 初始化前端  
cd ..
npx create-next-app@latest frontend --ts --tailwind --eslint --app

# 启动
# 终端 1
cd backend
uv run uvicorn app.gateway.main:app --reload --port 8001

# 终端 2
cd frontend
pnpm dev
```

### 结果
✅ 后端运行在 http://localhost:8001  
✅ 前端运行在 http://localhost:3000  
✅ 可以调用 API 并显示数据  

### 时间
⏱️ **60-90 分钟** 从零到工作的应用

---

## 选项 2：我想按 14 天计划学习和深化（50-61 小时）

如果你想**系统地学习**并理解整个项目架构：

### 第一步：查看计划总览

```
👉 打开: docs/plan/README.md

这里有学习路线的完整说明
```

### 第二步：从 Day 1 开始

```
👉 打开: docs/plan/day-01-environment-setup.md

按照每天的计划逐步学习
```

### 第三步：依次完成 Day 1-14

| Day | 内容 | 时间 |
|-----|------|------|
| 1 | 环境准备 | 4-5h |
| 2 | 架构学习 | 3-4h |
| 3 | Docker | 3-4h |
| 4-5 | 前端基础 | 6-8h |
| 6 | 页面布局 | 5-6h |
| 7-9 | 集成通信 | 8-10h |
| 10-11 | 后端网关 | 6-7h |
| 12 | LangGraph | 5-6h |
| 13 | 高级功能 | 5-6h |
| 14 | 测试部署 | 4-5h |

### 结果
✅ 完全理解系统架构  
✅ 能独立修改和扩展代码  
✅ 学会完整的全栈开发  

### 时间
⏱️ **50-61 小时** 系统的专业级学习路径

---

## 选项 3：我只想快速看一下怎么做（10 分钟）

快速浏览最关键的步骤：

### 后端 5 行代码启动

```powershell
cd backend
uv init
uv sync
uv run uvicorn app.gateway.main:app --reload --port 8001
# 访问: http://localhost:8001/health
```

### 前端 5 行代码启动

```powershell  
cd frontend
npx create-next-app@latest . --ts --tailwind
pnpm dev
# 访问: http://localhost:3000
```

### 结果
✅ 最小化的工作项目  
✅ 前后端能通信  

### 时间
⏱️ **10-15 分钟** 最快速原型

---

## 我应该选哪一个？

```decision tree
你想从零创建项目吗?
├─ 是，我要快速构建原型
│  └─→ 选项 1 或 3
│      (60-90 分钟或 10-15 分钟)
│
└─ 不，我想修改学习现有项目
   └─→ 选项 2
       (50-61 小时，系统学习)
```

---

## 📚 完整指南

### 从零创建项目
- [快速参考](./quick-reference.md) - 命令速查
- [完整详细指南](./00-from-scratch-creation.md) - 分步教程

### 14 天系统学习
- [总览](./README.md) - 计划说明
- [Day 1](./day-01-environment-setup.md) - 开始

---

## 命令速查表

```powershell
# 后端
uv init                              # 初始化项目
uv sync --group dev                  # 安装依赖
uv run pytest tests/ -v              # 运行测试
uv run uvicorn app.gateway.main:app  # 启动 API

# 前端
npx create-next-app@latest .         # 初始化项目
pnpm install                         # 安装依赖
pnpm dev                            # 启动开发
pnpm build                          # 生产构建
pnpm lint                           # 代码检查
pnpm typecheck                      # 类型检查

# 测试
curl http://localhost:8001/health    # 测试后端
curl http://localhost:8001/api/models # 获取模型列表
# 浏览器: http://localhost:3000      # 打开前端
```

---

## 🆘 遇到问题？

| 问题 | 解决方案 |
|------|--------|
| `uv: command not found` | `pip install uv` |
| `node: command not found` | 安装 Node.js 22+ |
| `pnpm: command not found` | `npm install -g pnpm` |
| 端口被占用 | 改用其他端口或杀死占用进程 |
| CORS 错误 | 检查 `.env.local` 中的 API URL |

---

## ✨ 下一步

完成初始化后，你可以：

1. ✅ 启动两个服务
2. ✅ 测试前后端通信
3. ✅ 按 14 天计划深化学习
4. ✅ 添加更多功能（API、聊天、LLM 等）

---

**现在就开始吧！选择上面的一个选项，进入相应的文件。** 🎉

```
选项 1: docs/plan/quick-reference.md
选项 2: docs/plan/README.md  
选项 3: 上面的"选项 3"命令
```

