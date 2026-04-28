# 快速命令参考 - 从零创建 DeerFlow

**快速链接** | 完整详细指南在 [`00-from-scratch-creation.md`](./00-from-scratch-creation.md)

---

## 🚀 一键命令合集

### 初始化项目（5 分钟）

```powershell
# 创建项目目录
mkdir C:\projects\deerflow-new
cd C:\projects\deerflow-new
git init

# 创建文件夹结构
mkdir backend, frontend, docker, docs, scripts, skills

# 初始化 Git
git init
```

### 创建后端（30 分钟）

```powershell
# 进入后端目录
cd backend

# 使用 uv 初始化项目
uv init --name deerflow-backend

# 替换 pyproject.toml（见下文）

# 安装依赖
uv sync --group dev

# 验证
python -c "import fastapi, langgraph; print('✓ OK')"
```

**pyproject.toml 内容**:
```toml
[project]
name = "deerflow-backend"
version = "0.1.0"
description = "DeerFlow Backend"
requires-python = ">=3.12"

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "langgraph>=0.1.0",
    "langchain>=0.1.0",
    "pydantic>=2.5.0",
    "httpx>=0.25.0",
]

[dependency-groups]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
]
```

**创建文件夹**:
```powershell
mkdir app
mkdir app\gateway
mkdir app\gateway\routes
mkdir packages
mkdir packages\harness
mkdir packages\harness\deerflow
mkdir packages\harness\deerflow\agents
mkdir tests

# 创建 __init__.py
@"
"@ | Out-File app\__init__.py
@"
"@ | Out-File app\gateway\__init__.py
@"
"@ | Out-File packages\__init__.py
```

### 创建前端（30 分钟）

```powershell
# 返回项目根目录
cd ..

# 使用 create-next-app
npx create-next-app@latest frontend --ts --tailwind --eslint --app

# 进入前端
cd frontend

# 安装额外依赖
pnpm install zustand @tanstack/react-query next-themes lucide-react
pnpm add -D class-variance-authority clsx tailwind-merge
pnpm add @radix-ui/react-dialog @radix-ui/react-dropdown-menu

# 创建文件夹
mkdir src\core\api
mkdir src\core\store
mkdir src\core\types
mkdir src\core\utils
mkdir src\components\layout
mkdir src\components\chat
```

**创建 `.env.local`**:
```
NEXT_PUBLIC_API_URL=http://localhost:8001
BETTER_AUTH_SECRET=dev-secret
```

### 启动应用（5 分钟）

```powershell
# 终端 1: 后端
cd backend
uv run uvicorn app.gateway.main:app --reload --port 8001

# 终端 2: 前端
cd frontend
pnpm dev

# 终端 3: 测试
curl http://localhost:8001/health
# 浏览器访问 http://localhost:3000
```

---

## 📝 核心文件模板

### `backend/app/gateway/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DeerFlow Gateway", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/models")
async def list_models():
    return {"models": [
        {"id": "gpt-4", "name": "GPT-4", "provider": "openai"},
        {"id": "claude-3", "name": "Claude 3", "provider": "anthropic"},
    ]}

@app.get("/api/skills")
async def list_skills():
    return {"skills": [
        {"id": "web_search", "name": "Web Search"},
        {"id": "code_exec", "name": "Code Execution"},
    ]}

@app.post("/api/langgraph/threads")
async def create_thread(config: dict = None):
    import uuid
    from datetime import datetime
    return {
        "thread_id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### `frontend/src/app/page.tsx`

```typescript
'use client';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export default function Home() {
  const [isHealthy, setIsHealthy] = useState(false);
  const [models, setModels] = useState([]);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${API_URL}/health`);
        setIsHealthy(res.ok);
        if (res.ok) {
          const data = await fetch(`${API_URL}/api/models`);
          setModels((await data.json()).models);
        }
      } catch (e) {
        setIsHealthy(false);
      }
    };
    check();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold">🦌 DeerFlow</h1>
        <p className="text-xl text-gray-600">LangGraph + Next.js</p>
        
        <div className="bg-white rounded-lg shadow-lg p-8 mt-8">
          <div className="flex justify-between mb-4">
            <span className="text-lg">后端:</span>
            <span className={isHealthy ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
              {isHealthy ? '✓ 运行中' : '✗ 离线'}
            </span>
          </div>
          <div>
            <span className="text-lg">模型:</span>
            <div className="mt-3 space-y-2">
              {models.map((m: any) => (
                <div key={m.id} className="bg-blue-50 p-3 rounded border border-blue-200">
                  {m.name}
                </div>
              ))}
            </div>
          </div>
          <Button className="w-full mt-6">开始对话</Button>
        </div>
      </div>
    </div>
  );
}
```

### `frontend/src/components/ui/Button.tsx`

```typescript
'use client';
import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', className = '', ...props }, ref) => {
    const variants = {
      primary: 'bg-blue-500 text-white hover:bg-blue-600',
      secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
      danger: 'bg-red-500 text-white hover:bg-red-600',
    };
    const sizes = {
      sm: 'px-3 py-1 text-sm',
      md: 'px-4 py-2',
      lg: 'px-6 py-3 text-lg',
    };
    return (
      <button
        ref={ref}
        className={`inline-flex items-center gap-2 font-medium transition-colors disabled:opacity-50 ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      />
    );
  }
);
```

### `backend/tests/test_gateway.py`

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

def test_list_models(client):
    response = client.get("/api/models")
    assert response.status_code == 200
    assert len(response.json()["models"]) > 0
```

---

## ✅ 验证清单

### 后端验证
```powershell
# 1. 检查依赖
cd backend
uv run python -c "import fastapi, langgraph; print('✓')"

# 2. 运行测试
uv run pytest tests/ -v

# 3. 启动服务
uv run uvicorn app.gateway.main:app --port 8001

# 4. 测试 API（新终端）
curl http://localhost:8001/health
curl http://localhost:8001/api/models
```

### 前端验证
```powershell
# 1. 检查依赖
cd frontend
pnpm list react next

# 2. 检查类型
pnpm typecheck

# 3. 启动开发服务器
pnpm dev

# 4. 浏览器访问 http://localhost:3000
# 应该看到"✓ 运行中"和模型列表
```

### 集成验证
```powershell
# 两个服务都运行时
# 前端应该显示后端在线
# 没有 CORS 或连接错误
# 模型列表正确显示
```

---

## 🔧 常见问题速查

| 问题 | 解决方案 |
|------|--------|
| `uv: command not found` | 安装 uv: `pip install uv` |
| `pnpm: command not found` | 安装 pnpm: `npm install -g pnpm` |
| 后端启不动 | 检查端口 8001 是否被占用 |
| 前端 CORS 错误 | 确认 `.env.local` 中 `NEXT_PUBLIC_API_URL` 正确 |
| 模块导入错误 | 运行 `uv sync --group dev` 或 `pnpm install` |
| TypeScript 错误 | 运行 `pnpm typecheck` 检查类型 |

---

## 🎯 下一步

完成上述步骤后，你可以：

1. 继续按 Day 14 天计划深化功能
2. 实现聊天界面（Day 7-9）
3. 集成 LangGraph 代理（Day 12）
4. 添加测试与部署（Day 14）

**详细指南**: [`00-from-scratch-creation.md`](./00-from-scratch-creation.md)

---

**时间**: 60-90 分钟从零到有一个完整的工作全栈应用！ ⚡

