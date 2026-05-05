# Day 1: 环境准备与项目结构认知

**日期**: Day 1 (第一天)  
**目标**: 建立完整开发环境，理解项目文件结构  
**预计时间**: 4-5 小时  
**难度**: ⭐ (简单)  

---

## 📋 学习概念

1. **Python 3.12 虚拟环境管理**
   - `uv` 包管理器工作流
   - `pyproject.toml` 依赖声明
   - 虚拟环境隔离

2. **Node.js 22 与 pnpm 工作流**
   - pnpm 工作区管理
   - `pnpm-lock.yaml` 锁文件
   - Monorepo 结构

3. **Makefile 自动化**
   - 命令编排
   - 开发流程启动
   - 清理与重置

4. **项目 Monorepo 结构**
   - 前端目录 (`frontend/`)
   - 后端目录 (`backend/`)
   - Docker 配置文件
   - 文档与脚本

---

## 🛠️ 第一步：验证系统依赖

打开 PowerShell，执行以下命令检查所需工具是否已安装：

```powershell
# 检查 Python 版本 (需要 >= 3.12)
python --version
# 期望输出: Python 3.12.x

# 检查 Node.js 版本 (需要 >= 22)
node --version
# 期望输出: v22.x.x 或更高

# 检查 pnpm 版本 (需要 >= 10.15)
pnpm --version
# 期望输出: 10.15.0 或更高

# 检查 uv (Python 包管理)
uv --version
# 期望输出: uv 0.7.20 或更高

# 检查 Docker (可选，但用于完整体验)
docker --version
# 期望输出: Docker version 20.10.x 或更高

# 检查 Nginx (Windows 上通常需要 WSL 或 Docker)
nginx -v
# 如果输出 "not found"，不用担心，Day 3 会说明
```

**如果任何工具缺失**，请参考 [`Install.md`](../../Install.md) 进行安装。

---

## 🛠️ 第二步：克隆并初始化项目

```powershell
# 进入工作目录
cd F:\qbot\deer-flow-main\deer-flow-main

# 查看项目结构
Get-ChildItem -Path . | Select-Object Name, FullName | Format-Table

# 预期看到的目录:
# Name            FullName
# ----            --------
# backend         F:\qbot\deer-flow-main\deer-flow-main\backend
# frontend        F:\qbot\deer-flow-main\deer-flow-main\frontend
# docker          F:\qbot\deer-flow-main\deer-flow-main\docker
# skills          F:\qbot\deer-flow-main\deer-flow-main\skills
# docs            F:\qbot\deer-flow-main\deer-flow-main\docs
# scripts         F:\qbot\deer-flow-main\deer-flow-main\scripts
```

---

## 🛠️ 第三步：运行系统检查

使用项目提供的检查脚本：

```powershell
# 从项目根目录执行
cd F:\qbot\deer-flow-main\deer-flow-main
make check
```

**预期输出**:
```
✓ Python 3.12 found
✓ Node.js 22 found
✓ pnpm 10.x found
✓ uv found
✓ nginx found (或 Optional if using Docker)
✓ All prerequisites satisfied
```

如果任何项显示 ✗，请参考上面的安装指南。

---

## 🛠️ 第四步：安装依赖

执行完整的依赖安装流程（推荐按这个顺序）：

### 4.1 后端依赖安装

```powershell
# 进入后端目录
cd F:\qbot\deer-flow-main\deer-flow-main\backend

# 使用 uv 同步依赖到虚拟环境
uv sync --group dev

# 验证安装成功
python -m pytest --version
# 期望输出: pytest x.x.x

# 验证 LangGraph 安装
python -c "import langgraph; print(langgraph.__version__)"
```

**时间估计**: 3-5 分钟

### 4.2 前端依赖安装

```powershell
# 进入前端目录
cd F:\qbot\deer-flow-main\deer-flow-main\frontend

# 安装 pnpm 依赖
pnpm install

# 验证安装成功
pnpm --version
```

**注意**: 如果遇到代理问题，临时取消设置代理环境变量：
```powershell
# 临时清除代理
$env:HTTP_PROXY = $null
$env:HTTPS_PROXY = $null
# 重新运行
pnpm install
```

**时间估计**: 2-4 分钟

---

## 📁 第五步：理解项目结构

运行以下命令生成结构树（使用 Tree 命令）：

```powershell
# 后端结构
cd F:\qbot\deer-flow-main\deer-flow-main\backend
Get-ChildItem -Recurse -Depth 2 | Select-Object FullName | Format-Table
```

**关键目录说明**:

| 路径 | 用途 | 说明 |
|------|------|------|
| `backend/app/gateway/` | FastAPI 网关入口 | REST API 服务 |
| `backend/packages/harness/deerflow/` | 核心代理系统 | LangGraph 实现 |
| `backend/packages/harness/deerflow/agents/` | 代理定义 | Lead Agent、中间件 |
| `backend/packages/harness/deerflow/sandbox/` | 沙箱执行 | 代码安全执行环境 |
| `backend/packages/harness/deerflow/mcp/` | MCP 集成 | Model Context Protocol |
| `backend/tests/` | 测试套件 | 单元及集成测试 |

```powershell
# 前端结构
cd F:\qbot\deer-flow-main\deer-flow-main\frontend
Get-ChildItem -Recurse -Depth 2 | Select-Object FullName | Format-Table
```

**关键前端目录**:

| 路径 | 用途 | 说明 |
|------|------|------|
| `frontend/src/app/` | Next.js 路由/页面 | 应用主框架 |
| `frontend/src/components/` | React 组件库 | UI 组件集合 |
| `frontend/src/core/` | 应用逻辑 | API、状态管理、类型定义 |
| `frontend/public/` | 静态资源 | 图片、图标等 |

---

## 📄 第六步：理解关键配置文件

### 6.1 查看后端 `pyproject.toml`

```powershell
cd F:\qbot\deer-flow-main\deer-flow-main\backend
# 使用记事本或编辑器打开
notepad pyproject.toml
```

**注意**:
- `requires-python = ">=3.12"`
- 依赖分组: `dev`, `test`, `doc`
- 工作空间含多个包

### 6.2 查看前端 `package.json`

```powershell
cd F:\qbot\deer-flow-main\deer-flow-main\frontend
# 查看 npm scripts
more .\package.json
```

**关键 scripts**:
- `pnpm dev` - 本地开发服务器
- `pnpm build` - 生产构建
- `pnpm lint` - 代码检查
- `pnpm test` - 单元测试

### 6.3 查看根目录 `Makefile`

```powershell
cd F:\qbot\deer-flow-main\deer-flow-main
more Makefile
```

**主要命令**:
- `make check` - 检查环境
- `make install` - 安装全部依赖
- `make dev` - 启动完整应用
- `make stop` - 停止所有服务

---

## 🔍 第七步：验证配置与对接

### 7.1 初始化配置文件

```powershell
cd F:\qbot\deer-flow-main\deer-flow-main

# 查看配置示例
Get-Content config.example.yaml | Select-Object -First 50

# 创建本地配置 (第一次执行会创建)
make config
```

**注意**: `make config` 是一次性的，若 `config.yaml` 已存在，会中止。

### 7.2 检查配置内容

```powershell
# 验证生成的配置
Get-Content config.yaml | Select-Object -First 50
```

`config.yaml` 应包含:
- `backend_host` / `backend_port` - Gateway 服务配置
- `langgraph_host` / `langgraph_port` - LangGraph 服务配置
- `model_provider` - LLM 提供商选择 (OpenAI, Anthropic 等)
- `api_key` - 模型 API 密钥

---

## ✅ 验证清单

运行以下检查确保 Day 1 完成：

```powershell
# 1. 检查 Python 虚拟环境
cd F:\qbot\deer-flow-main\deer-flow-main\backend
python -c "import sys; print(f'Python {sys.version}')"
# 预期: Python 3.12.x ...

# 2. 检查后端关键依赖
python -c "import fastapi, langgraph, pydantic; print('FastAPI, LangGraph, Pydantic OK')"

# 3. 检查前端依赖
cd F:\qbot\deer-flow-main\deer-flow-main\frontend
pnpm list react next
# 预期: react@19.x, next@16.x

# 4. 检查项目结构完整性
cd F:\qbot\deer-flow-main\deer-flow-main
Test-Path backend, frontend, docker, skills -PathType Container
# 期望全部返回 True

# 5. 查看配置文件
Test-Path config.yaml
# 期望返回 True (如果前面执行了 make config)
```

---

## 🎯 Day 1 总结

完成 Day 1 后，你应该：

✅ 安装了 Python 3.12、Node.js 22、pnpm、uv  
✅ 克隆了 DeerFlow 项目  
✅ 安装了所有后端和前端依赖  
✅ 理解了 Monorepo 项目结构  
✅ 自动化命令工作流  
✅ 配置了基本环境变量  

---

## 📚 后续建议

- **Day 2** 前，先通读 [`backend/README.md`](../../backend/README.md) 和 [`frontend/README.md`](../../frontend/README.md)
- 可选：阅读 [`ARCHITECTURE.md`](../ARCHITECTURE.md) 了解系统设计背景
- 如有问题，参考 [`Install.md`](../../Install.md)

---

## ⏱️ 时间记录

| 任务 | 预计时间 | 实际时间 |
|------|---------|---------|
| 系统依赖检查 | 5 分钟 | ___ |
| 项目初始化 | 5 分钟 | ___ |
| 后端依赖安装 | 3-5 分钟 | ___ |
| 前端依赖安装 | 2-4 分钟 | ___ |
| 结构理解与配置 | 30-45 分钟 | ___ |
| 验证检查 | 10-15 分钟 | ___ |
| **总计** | **4-5 小时** | **___** |

---

**下一步**: 完成后，进入 Day 2 - 架构与技术栈深度学习

