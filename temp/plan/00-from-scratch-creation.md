# 从零开始创建 DeerFlow 项目 - 完整指南

**目标**: 使用 `uv` (Python) 和 `next` (Node.js) 从零开始重建整个项目  
**预计时间**: 2-3 小时  
**难度**: ⭐⭐⭐  

---

## 📋 概述

本指南将指导你如何从零开始创建 DeerFlow 项目的完整结构，包括：

1. **项目初始化** - 创建 Monorepo 结构
2. **后端创建** - 使用 `uv` 和 FastAPI 创建 Python 项目
3. **前端创建** - 使用 `next` 创建 Next.js 项目
4. **集成验证** - 确保两端能协同工作

---

## 🎯 Part 1: 项目初始化（15 分钟）

### Step 1.1: 创建项目根目录

```powershell
# 创建项目根目录
mkdir C:\projects\deerflow-new
cd C:\projects\deerflow-new

# 初始化 Git（可选但推荐）
git init
```

### Step 1.2: 创建 Monorepo 结构

```powershell
# 创建目录结构
mkdir backend
mkdir frontend
mkdir docker
mkdir docs
mkdir scripts
mkdir skills

# 创建根级 Makefile
New-Item -Path "Makefile" -ItemType File
```

### Step 1.3: 创建根级配置文件

创建 `README.md`:
```markdown
# DeerFlow - 从零开始的项目

一个完整的 Python + Next.js 全栈应用，集成 LLM 代理系统。

## 项目结构

```
deerflow/
├── backend/          # Python FastAPI + LangGraph
├── frontend/         # Next.js 16 + React 19
├── docker/           # Docker 配置
├── docs/             # 文档
└── scripts/          # 工具脚本
```

## 快速开始

### 后端
```bash
cd backend
uv sync --group dev
uv run python -m app.gateway.main
```

### 前端
```bash
cd frontend
pnpm install
pnpm dev
```

### 完整应用
```bash
make dev
```

## 系统要求

- Python >= 3.12
- Node.js >= 22
- pnpm >= 10.15
```

创建 `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
.ruff_cache/

# Node
node_modules/
.next/
out/
*.log
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Env
.env
.env.local
config.yaml

# Docker
.dockerignore
```

---

## 🐍 Part 2: Backend 从零创建（60-75 分钟）

### Step 2.1: 初始化 Python 项目

```powershell
cd backend

# 使用 uv 创建项目
uv init --name deerflow-backend

# 预期生成的结构:
# backend/
# ├── pyproject.toml
# ├── README.md
# ├── uv.lock
# └── src/
#     ├── __init__.py
#     └── main.py
```

### Step 2.2: 配置 pyproject.toml

编辑 `backend/pyproject.toml`:

```toml
[project]
name = "deerflow-backend"
version = "0.1.0"
description = "DeerFlow - Python LangGraph Backend"
requires-python = ">=3.12"
authors = [
    {name = "DeerFlow", email = "team@deerflow.dev"}
]

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "langgraph>=0.1.0",
    "langchain>=0.1.0",
    "langchain-core>=0.1.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
]

[dependency-groups]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "black>=23.0.0",
    "mypy>=1.7.0",
]

[tool.uv]
dev-dependencies = [
    "pytest",
    "pytest-asyncio",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Step 2.3: 安装依赖

```powershell
# 从 backend 目录执行
cd backend

# 同步所有依赖（包括 dev）
uv sync --group dev

# 验证安装
python -c "import fastapi, langgraph; print('✓ Dependencies OK')"
```

**预期时间**: 3-5 分钟

### Step 2.4: 创建项目结构

```powershell
# 从 backend 目录执行

# 创建应用目录结构
mkdir app
mkdir app\gateway
mkdir app\gateway\routes
mkdir app\channels
mkdir packages
mkdir packages\harness
mkdir packages\harness\deerflow
mkdir packages\harness\deerflow\agents
mkdir packages\harness\deerflow\sandbox
mkdir packages\harness\deerflow\mcp
mkdir packages\harness\deerflow\memory
mkdir tests

# 创建空的 __init__.py 文件
New-Item app\__init__.py, app\gateway\__init__.py, app\gateway\routes\__init__.py
```

### Step 2.5: 创建启动文件

创建 `backend/app/gateway/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="DeerFlow Gateway",
    description="LangGraph 代理网关",
    version="0.1.0",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "gateway"}

@app.get("/")
async def root():
    return {"message": "DeerFlow Gateway v0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Step 2.6: 创建 LangGraph 模块

创建 `backend/packages/harness/deerflow/agents/__init__.py`:

```python
from .agent_state import ThreadState
from .lead_agent import make_lead_agent

__all__ = ["ThreadState", "make_lead_agent"]
```

创建 `backend/packages/harness/deerflow/agents/agent_state.py`:

```python
from typing import Annotated, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

class ThreadState(BaseModel):
    """代理线程状态"""
    messages: Sequence[BaseMessage] = Field(default_factory=list)
    artifacts: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
```

创建 `backend/packages/harness/deerflow/agents/lead_agent.py`:

```python
from langchain_core.language_model import BaseLLM
from langgraph.graph import StateGraph, START, END
from .agent_state import ThreadState
import logging

logger = logging.getLogger(__name__)

def make_lead_agent(model: BaseLLM, tools: list = None):
    """构建 Lead Agent"""
    
    graph = StateGraph(ThreadState)
    
    # 简单的 echo 节点
    async def echo_node(state: ThreadState) -> dict:
        if state.messages:
            last_msg = state.messages[-1]
            logger.info(f"Received: {last_msg.content}")
        return {}
    
    graph.add_node("echo", echo_node)
    graph.add_edge(START, "echo")
    graph.add_edge("echo", END)
    
    return graph.compile()
```

### Step 2.7: 创建测试文件

创建 `backend/tests/test_gateway.py`:

```python
import pytest
from fastapi.testclient import TestClient
from app.gateway.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
```

创建 `backend/tests/conftest.py`:

```python
import pytest

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

### Step 2.8: 测试后端

```powershell
cd backend

# 运行测试
uv run pytest tests/ -v

# 启动应用
uv run python -m app.gateway.main
# 或
uv run uvicorn app.gateway.main:app --reload --port 8001
```

**验证**: 访问 http://localhost:8001/health 应返回 `{"status": "ok"}`

---

## ⚛️ Part 3: Frontend 从零创建（60-75 分钟）

### Step 3.1: 使用 create-next-app 初始化

```powershell
# 回到主目录
cd ..

# 使用 Next.js 脚手架创建前端
npx create-next-app@latest frontend --typescript --tailwind --eslint

# 选择选项时的建议答案:
# ✔ Would you like to use TypeScript? › Yes
# ✔ Would you like to use ESLint? › Yes
# ✔ Would you like to use Tailwind CSS? › Yes
# ✔ Would you like to use `src/` directory? › Yes
# ✔ Would you like to use App Router? › Yes
# ✔ Would you like to customize the import alias? › No
```

### Step 3.2: 安装前端依赖

```powershell
cd frontend

# 使用 pnpm 安装（如果还没有 pnpm）
npm install -g pnpm

# 安装项目依赖
pnpm install

# 添加额外依赖
pnpm add zustand @tanstack/react-query zod next-themes lucide-react

# 添加 Radix UI
pnpm add @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-accordion @radix-ui/react-icons

# 添加工具库
pnpm add class-variance-authority clsx tailwind-merge
```

### Step 3.3: 配置环境变量

创建 `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8001
BETTER_AUTH_SECRET=dev-secret-key-change-in-production
```

### Step 3.4: 创建应用结构

```powershell
# 创建目录结构
mkdir src\app\(dashboard)
mkdir src\components\layout
mkdir src\components\chat
mkdir src\components\ui
mkdir src\core\api
mkdir src\core\store
mkdir src\core\utils
mkdir src\core\types
```

### Step 3.5: 创建核心类型文件

创建 `frontend/src/core/types/index.ts`:

```typescript
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface Thread {
  id: string;
  title?: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Model {
  id: string;
  name: string;
  provider: string;
}
```

### Step 3.6: 创建 API 客户端

创建 `frontend/src/core/api/client.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export async function createThread(config?: Record<string, any>) {
  const response = await fetch(`${API_BASE}/api/langgraph/threads`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ config: config || {} }),
  });

  if (!response.ok) throw new Error('创建线程失败');
  return response.json();
}

export async function listModels() {
  const response = await fetch(`${API_BASE}/api/models`);
  if (!response.ok) throw new Error('获取模型列表失败');
  return response.json();
}

export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
```

### Step 3.7: 创建 Zustand Store

创建 `frontend/src/core/store/useThreadStore.ts`:

```typescript
import { create } from 'zustand';
import { Message, Thread } from '@/core/types';

interface ThreadStore {
  threads: Thread[];
  currentThreadId: string | null;
  addThread: (thread: Thread) => void;
  setCurrentThread: (id: string | null) => void;
  addMessage: (threadId: string, message: Message) => void;
}

export const useThreadStore = create<ThreadStore>((set) => ({
  threads: [],
  currentThreadId: null,
  addThread: (thread) => set((state) => ({ threads: [thread, ...state.threads] })),
  setCurrentThread: (id) => set({ currentThreadId: id }),
  addMessage: (threadId, message) =>
    set((state) => ({
      threads: state.threads.map((t) =>
        t.id === threadId ? { ...t, messages: [...t.messages, message] } : t
      ),
    })),
}));
```

### Step 3.8: 创建 UI 组件

创建 `frontend/src/components/ui/Button.tsx`:

```typescript
'use client';

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-blue-500 text-white hover:bg-blue-600',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        danger: 'bg-red-500 text-white hover:bg-red-600',
      },
      size: {
        sm: 'px-3 py-1 text-sm',
        md: 'px-4 py-2',
        lg: 'px-6 py-3 text-lg',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className: _, variant, size, ...props }, ref) => (
    <button
      ref={ref}
      className={buttonVariants({ variant, size })}
      {...props}
    />
  )
);

Button.displayName = 'Button';
```

### Step 3.9: 创建主页

编辑 `frontend/src/app/page.tsx`:

```typescript
'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { healthCheck, listModels } from '@/core/api/client';

export default function Home() {
  const [isHealthy, setIsHealthy] = useState(false);
  const [models, setModels] = useState([]);

  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await healthCheck();
      setIsHealthy(healthy);

      if (healthy) {
        try {
          const data = await listModels();
          setModels(data.models || []);
        } catch (error) {
          console.error('Failed to load models:', error);
        }
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🦌 DeerFlow
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          LangGraph + Next.js 构建的智能代理应用
        </p>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4">系统状态</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-lg">后端服务:</span>
              <span
                className={`px-4 py-2 rounded font-bold ${
                  isHealthy
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {isHealthy ? '✓ 运行中' : '✗ 离线'}
              </span>
            </div>

            <div>
              <span className="text-lg">可用模型:</span>
              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2">
                {models.length > 0 ? (
                  models.map((model: any) => (
                    <div
                      key={model.id}
                      className="bg-blue-50 p-3 rounded border border-blue-200"
                    >
                      <p className="font-medium">{model.name}</p>
                      <p className="text-sm text-gray-600">{model.id}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500">
                    {isHealthy
                      ? '暂无模型'
                      : '无法加载模型（后端离线）'}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        <Button size="lg" className="w-full">
          开始对话
        </Button>
      </div>
    </div>
  );
}
```

### Step 3.10: 测试前端

```powershell
cd frontend

# 启动开发服务器
pnpm dev

# 访问 http://localhost:3000
```

---

## 🔗 Part 4: 集成与验证（30 分钟）

### Step 4.1: 创建根 Makefile

编辑项目根目录的 `Makefile`:

```makefile
.PHONY: help check install dev stop clean

help:
	@echo "DeerFlow Development Commands"
	@echo ""
	@echo "make check    - 检查环境"
	@echo "make install  - 安装所有依赖"
	@echo "make dev      - 启动完整应用"
	@echo "make stop     - 停止所有服务"
	@echo "make clean    - 清理构建文件"

check:
	@echo "✓ Checking Python..."
	@python --version
	@echo "✓ Checking Node.js..."
	@node --version
	@echo "✓ Checking pnpm..."
	@pnpm --version
	@echo "✓ Checking uv..."
	@uv --version

install:
	@echo "Installing backend dependencies..."
	@cd backend && uv sync --group dev
	@echo "Installing frontend dependencies..."
	@cd frontend && pnpm install

dev:
	@echo "Starting DeerFlow services..."
	@echo "Backend: http://localhost:8001"
	@echo "Frontend: http://localhost:3000"
	@echo ""
	@start cmd /k "cd backend && uv run uvicorn app.gateway.main:app --reload --port 8001"
	@start cmd /k "cd frontend && pnpm dev"
	@echo "Services started in separate windows"

stop:
	@echo "Stopping services..."
	@taskkill /F /IM python.exe /T 2>nul || true
	@taskkill /F /IM node.exe /T 2>nul || true
	@echo "✓ Services stopped"

clean:
	@echo "Cleaning up..."
	@cd backend && rm -r __pycache__ .pytest_cache .ruff_cache dist build *.egg-info 2>nul || true
	@cd frontend && rm -r node_modules .next out 2>nul || true
	@echo "✓ Cleaned"
```

### Step 4.2: 创建 Docker 配置（可选）

创建 `docker/docker-compose.yaml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - PYTHONUNBUFFERED=1
    command: uv run uvicorn app.gateway.main:app --host 0.0.0.0 --port 8001

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8001
    depends_on:
      - backend
```

创建 `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync

COPY . .

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "app.gateway.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

创建 `frontend/Dockerfile`:

```dockerfile
FROM node:22-alpine

WORKDIR /app

RUN npm install -g pnpm

COPY pnpm-lock.yaml package.json ./
RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm build

EXPOSE 3000

CMD ["pnpm", "start"]
```

### Step 4.3: 测试集成

```powershell
# 终端 1: 启动后端
cd backend
uv run uvicorn app.gateway.main:app --reload --port 8001

# 终端 2: 启动前端
cd frontend
pnpm dev

# 终端 3: 测试 API
curl http://localhost:8001/health
# 期望: {"status":"ok","service":"gateway"}

# 浏览器访问
# http://localhost:3000
# 应该显示 "✓ 运行中"
```

### Step 4.4: 创建 API 端点

编辑 `backend/app/gateway/main.py`，添加更多路由：

```python
# ...existing code...

@app.get("/api/models")
async def list_models():
    return {
        "models": [
            {"id": "gpt-4", "name": "GPT-4", "provider": "openai"},
            {"id": "claude-3", "name": "Claude 3", "provider": "anthropic"},
        ],
        "total": 2,
    }

@app.get("/api/skills")
async def list_skills():
    return {
        "skills": [
            {"id": "web_search", "name": "Web Search"},
            {"id": "code_exec", "name": "Code Execution"},
        ],
        "total": 2,
    }

@app.post("/api/langgraph/threads")
async def create_thread(config: dict = None):
    import uuid
    from datetime import datetime
    
    return {
        "thread_id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(),
    }
```

---

## ✅ 完成检查清单

### 后端检查
- [ ] `backend/app/gateway/main.py` 能启动
- [ ] `/health` 返回 200
- [ ] `/api/models` 返回模型列表
- [ ] `/api/langgraph/threads` 能创建线程
- [ ] 所有测试通过

### 前端检查
- [ ] `pnpm dev` 能启动
- [ ] http://localhost:3000 能访问
- [ ] 显示"✓ 运行中"（后端连接成功）
- [ ] 显示可用模型列表
- [ ] 没有控制台错误

### 集成检查
- [ ] 后端和前端都能运行
- [ ] 前端能调用后端 API
- [ ] 响应数据正确显示
- [ ] 没有 CORS 错误

---

## 📊 项目结构最终样子

```
deerflow/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── gateway/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   ├── channels/
│   │   └── models.py
│   ├── packages/
│   │   └── harness/
│   │       └── deerflow/
│   │           ├── agents/
│   │           ├── sandbox/
│   │           └── mcp/
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_gateway.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── Dockerfile
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   └── Button.tsx
│   │   │   ├── layout/
│   │   │   └── chat/
│   │   ├── core/
│   │   │   ├── api/
│   │   │   ├── store/
│   │   │   ├── types/
│   │   │   └── utils/
│   │   └── styles/
│   ├── public/
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── Dockerfile
│   └── README.md
│
├── docker/
│   └── docker-compose.yaml
│
├── docs/
│   └── plan/
│
├── Makefile
├── README.md
├── .gitignore
└── docker-compose.yaml
```

---

## 🚀 后续步骤

完成本指南后，你可以：

1. **集成 LangGraph** → Day 12 计划
2. **实现聊天功能** → Day 7-9 计划
3. **添加认证系统** → 可选扩展
4. **部署到生产** → Day 14 计划

---

## 📚 参考资源

| 资源 | 链接 |
|------|------|
| uv 文档 | https://docs.astral.sh/uv/ |
| FastAPI 文档 | https://fastapi.tiangolo.com/ |
| Next.js 16 文档 | https://nextjs.org/docs |
| LangGraph 文档 | https://langchain-ai.github.io/langgraph/ |

---

**恭喜！你已完成从零开始创建完整的 DeerFlow 项目！** 🎉

下一步：按照 Day 14 天重写计划深化项目功能。

