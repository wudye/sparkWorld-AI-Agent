# Day 3: Docker 容器化与本地启动

**日期**: Day 3 (第三天)  
**目标**: 成功在本地启动完整应用（Docker 或本地开发模式）  
**预计时间**: 3-4 小时  
**难度**: ⭐ (简单)  
**前置**: 完成 Day 1-2  

---

## 📋 学习概念

### 1. Docker 基本概念

**什么是 Docker?**
- 轻量级容器化平台
- 打包应用及其依赖
- 确保"在我的机器上工作"在任何地方工作

**核心概念**:
- **Image**: 应用蓝图（只读）
- **Container**: Image 的运行实例
- **Dockerfile**: Image 构建脚本
- **docker-compose**: 多容器编排工具

### 2. Docker Compose（Multi-Container）

**DeerFlow 的容器栈**:
```yaml
services:
  langgraph:     # LangGraph 服务 (Python)
  gateway:       # FastAPI Gateway (Python)
  frontend:      # Next.js Frontend (Node.js)
  nginx:         # 反向代理 / 负载均衡
  postgres:      # (可选) 数据库
```

### 3. Nginx 反向代理

**作用**:
- 统一入口 (http://localhost:2026)
- 路由转发:
  - `/` → 前端 (localhost:3000)
  - `/api/langgraph` → Gateway (localhost:8001)
  - `/lsync` → LangGraph (localhost:2024)

**配置示例**:
```nginx
server {
    listen 2026;
    
    location / {
        proxy_pass http://frontend:3000;
    }
    
    location /api/ {
        proxy_pass http://gateway:8001;
    }
    
    location /lsync/ {
        proxy_pass http://langgraph:2024;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 4. 本地开发模式 vs 生产模式

| 模式 | 使用方式 | 适用场景 | 优点 | 缺点 |
|------|---------|---------|------|------|
| **本地开发** | `make dev` | 发开发阶段 | 快速热重载、易调试 | 需要本地工具链 |
| **Docker** | `make docker-dev` | 隔离环境测试 | 环境一致性 | 启动较慢 |
| **生产** | `docker-compose up` | 生产部署 | 高性能、安全 | 可观测性复杂 |

---

## 🎯 第一部分：选择启动模式

### 决策树

```
┌─ 系统是否支持 Nginx?
│  ├─ YES (macOS/Linux) → 选项 A
│  └─ NO (Windows) → 检查是否有 Docker Desktop
│     ├─ YES → 选项 B (Docker)
│     └─ NO → 选项 C (本地无代理启动)
```

---

## 🗂️ 选项 A: 本地完整启动（Linux/macOS，Windows WSL2）

**要求**: 
- Nginx 已安装
- Python 3.12、Node.js 22、pnpm 已配置（完成 Day 1）

### Step 1: 验证 Nginx 安装

```powershell
# Windows 上如果有 WSL 或 Nginx for Windows:
nginx -v
# 预期: nginx version: nginx/1.x.x

# 如果无 Nginx，建议改用选项 B (Docker)
```

### Step 2: 启动完整应用

```powershell
cd F:\qbot\deer-flow-main\deer-flow-main

# 一键启动 (包括 Nginx、后端、前端)
make dev

# 预期输出:
# Starting LangGraph service on port 2024...
# Starting Gateway service on port 8001...
# Starting Frontend service on port 3000...
# Starting Nginx on port 2026...
# ✓ All services started. Visit http://localhost:2026
```

### Step 3: 验证服务

```powershell
# 在新的 PowerShell 终端验证

# 1. 检查 Nginx 是否运行
netstat -ano | Select-String ":2026"
# 预期: 某个 PID

# 2. 检查 Gateway
curl http://localhost:8001/health
# 预期: {"status": "ok"}

# 3. 检查 LangGraph
curl http://localhost:2024/health
# 或查看日志
Get-Content logs/langgraph.log -Tail 20

# 4. 检查前端
curl http://localhost:3000
# 预期: HTML 内容

# 5. 通过 Nginx 访问 (统一入口)
curl http://localhost:2026
# 预期: HTML 内容 (打开浏览器看 UI)
```

### Step 4: 打开浏览器

```powershell
# 在 PowerShell 中：
Start-Process http://localhost:2026
# 或手动输入: http://localhost:2026

# 预期看到:
# - DeerFlow UI 加载
# - 没有明显错误
# - 可以输入消息
```

### Step 5: 测试端到端流程

1. 在 Web UI 输入框输入: "Hello, DeerFlow!"
2. 检查浏览器控制台 (F12) 是否有错误
3. 检查后端日志

```powershell
# 查看 Gateway 日志
Get-Content logs/gateway.log -Tail 50

# 查看 LangGraph 日志
Get-Content logs/langgraph.log -Tail 50
```

---

## 🐳 选项 B: Docker 容器化启动

**优点**: 避免本地工具链复杂性  
**缺点**: 启动稍慢（首次 5-10 分钟）

### Step 1: 验证 Docker

```powershell
docker --version
docker-compose --version

# 如果无 Docker Desktop，安装:
# https://www.docker.com/products/docker-desktop
```

### Step 2: 启动 Docker Compose

```powershell
cd F:\qbot\deer-flow-main\deer-flow-main

# 使用 Docker 启动后端堆栈
make docker-dev

# 或手动：
docker-compose -f docker/docker-compose-dev.yaml up --build

# 首次启动会:
# 1. 构建 Python 镜像 (backend) - 2-3 分钟
# 2. 构建 Node.js 镜像 (frontend) - 2-3 分钟
# 3. 启动依赖 (Postgres、Redis 等) - 1 分钟
# 4. 启动应用容器 - 1-2 分钟
```

### Step 3: 检查容器状态

```powershell
# 查看运行中的容器
docker ps

# 预期输出：
# CONTAINER ID  IMAGE  PORTS  STATUS
# abc123xx      langgraph  0.0.0.0:2024->2024/tcp  Up 1 minute
# def456xx      gateway    0.0.0.0:8001->8001/tcp  Up 1 minute
# ghi789xx      frontend   0.0.0.0:3000->3000/tcp  Up 1 minute
# jkl012xx      nginx      0.0.0.0:2026->2026/tcp  Up 1 minute
```

### Step 4: 访问应用

```powershell
# 前端统一入口 (Nginx 反向代理)
Start-Process http://localhost:2026

# 或逐个检查：
# - Gateway: http://localhost:8001/health
# - Frontend: http://localhost:3000
```

### Step 5: 查看容器日志

```powershell
# Gateway 日志
docker logs -f <gateway_container_id>
# 或 (如果容器名已知)
docker logs -f deerflow-gateway-1

# LangGraph 日志
docker logs -f deerflow-langgraph-1

# 查看 Compose 日志 (所有容器)
docker-compose -f docker/docker-compose-dev.yaml logs -f
```

---

## 🛑 选项 C: 本地启动（无 Nginx 代理）

**场景**: 无法使用 Nginx，想快速启动后端  
**注意**: 需要分别访问不同端口

### Step 1: 启动后端服务

```powershell
cd F:\qbot\deer-flow-main\deer-flow-main\backend

# 终端 1: 启动 LangGraph
uv run langgraph up

# 或使用脚本
python -m deerflow.langgraph_server

# 检查日志：
# Uvicorn running on http://0.0.0.0:2024
```

```powershell
# 终端 2: 启动 Gateway (FastAPI)
cd F:\qbot\deer-flow-main\deer-flow-main\backend

uv run fastapi run app/gateway/main.py --host 0.0.0.0 --port 8001

# 检查日志：
# Uvicorn running on http://0.0.0.0:8001
```

### Step 2: 启动前端服务

```powershell
# 终端 3: 启动前端
cd F:\qbot\deer-flow-main\deer-flow-main\frontend

# 设置必要的环境变量
$env:BETTER_AUTH_SECRET = "dev-secret-key"

pnpm dev

# 检查日志：
# ▲ Next.js 16.x
#   Local:        http://localhost:3000
```

### Step 3: 配置 CORS 以允许跨域请求

编辑 `frontend/src/core/api/client.ts`，确保 API 基址指向 Gateway:

```typescript
const API_BASE = 'http://localhost:8001';

export async function createThread(...) {
    return fetch(`${API_BASE}/api/langgraph/threads`, ...)
}
```

### Step 4: 测试

```powershell
# 打开浏览器
Start-Process http://localhost:3000

# 检查浏览器控制台 (F12)
# 如果有 CORS 错误，需要配置 Gateway CORS:
#   app/gateway/__init__.py 中添加 CORS 中间件
```

---

## ✅ 验证清单

无论使用哪个选项，完成以下验证：

### 临界路径检查

```powershell
# 1. 所有服务运行（检查端口）
# Windows 上查看占用的端口：
netstat -ano | Select-String ":2026|:8001|:2024|:3000"
# 预期: 所有 4 个端口都有 LISTENING

# 或 Docker 环境：
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
# 预期: 4 个容器都在 Up 状态
```

### Web UI 检查

1. **打开 http://localhost:2026**
2. **查看页面元素**:
   - [ ] 侧边栏加载（模型选择、设置）
   - [ ] 消息输入框存在
   - [ ] 没有红色错误信息
   - [ ] 系统状态显示为"Ready"

### API 连接检查

```powershell
# 测试创建对话线程
$headers = @{ "Content-Type" = "application/json" }
$body = '{"config": {}}'

$response = Invoke-WebRequest `
    -Uri "http://localhost:8001/api/langgraph/threads" `
    -Method POST `
    -Headers $headers `
    -Body $body

$response.Content | ConvertFrom-Json

# 预期返回:
# {
#   "thread_id": "abc-123-def",
#   "created_at": "2026-04-01T10:00:00Z"
# }
```

### 流式消息测试

```powershell
# 创建线程后，测试流式事件
$threadId = "abc-123-def"  # 从上面的响应获取

$headers = @{ "Accept" = "text/event-stream" }
$body = '{"input": "Hello, DeerFlow!"}'

$response = Invoke-WebRequest `
    -Uri "http://localhost:8001/api/langgraph/threads/$threadId/events" `
    -Method POST `
    -Headers $headers `
    -Body $body

# 应该看到流式事件
$response.Content | Select-Object -First 500
```

### 浏览器检查

切换到浏览器，打开开发者工具 (F12):

1. **Console 标签**:
   - 应该没有红色错误
   - 可能有警告（这是正常的）

2. **Network 标签**:
   - 监视 `/api/langgraph/threads` 请求
   - 应该看到 `200 OK` 响应

3. **发送测试消息**:
   - 在 UI 中输入: "Test message"
   - 检查消息是否出现在聊天框中
   - 查看 Network 标签中的 EventStream 请求

---

## 🐛 常见问题排查

### 问题 1: Port 已占用

```powershell
# 检查哪个进程占用端口 2026
Get-Process | Where-Object { $_.Handles -match ... } # PowerShell 限制，用下面替代

netstat -ano | Select-String ":2026"
# 输出示例: TCP    0.0.0.0:2026    0.0.0.0:0    LISTENING    1234

# 查看进程
tasklist | Select-String "1234"

# 杀死进程
taskkill /PID 1234 /F
```

### 问题 2: Docker 镜像构建失败

```powershell
# 清理旧镜像
docker system prune -a

# 尝试重新构建
docker-compose -f docker/docker-compose-dev.yaml build --no-cache

# 查看构建日志
docker-compose -f docker/docker-compose-dev.yaml logs build
```

### 问题 3: 前端加载空白

```powershell
# 检查 Next.js 构建
cd frontend
pnpm build

# 设置环境变量
$env:BETTER_AUTH_SECRET = "dev-secret-key"

# 重新启动
pnpm dev
```

### 问题 4: 无法连接到后端 API

```powershell
# 1. 检查 Gateway 是否运行
curl http://localhost:8001/health
# 如果超时，Gateway 未运行

# 2. 检查防火墙
# Windows Defender 可能阻止端口
# 允许 Python.exe 和 Node.exe 通过防火墙

# 3. 检查 API 基础 URL
# frontend/src/core/api/client.ts
# 确保 API_BASE 正确
```

### 问题 5: SSE 连接中断

```powershell
# 检查 nginx 配置是否支持流式响应
# nginx/conf.d/default.conf 中应该有：
# proxy_buffering off;
# proxy_request_buffering off;

# 检查 Gateway 中间件是否干扰 SSE
# app/gateway/__init__.py 中应该有正确的中间件顺序
```

---

## 📊 Docker Compose 文件理解

打开并理解 Docker 配置:

```powershell
code docker/docker-compose-dev.yaml
# 或
notepad docker/docker-compose-dev.yaml
```

**关键部分**:

```yaml
services:
  langgraph:
    build:
      context: backend
      dockerfile: Dockerfile
    ports:
      - "2024:2024"
    environment:
      - PYTHONUNBUFFERED=1
      - LANGGRAPH_PORT=2024
    depends_on:
      - postgres  # (可选) 依赖数据库

  gateway:
    build:
      context: backend
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - LANGGRAPH_URL=http://langgraph:2024
      - API_KEY=${OPENAI_API_KEY}
    depends_on:
      - langgraph

  frontend:
    build:
      context: frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    depends_on:
      - gateway

  nginx:
    image: nginx:latest
    ports:
      - "2026:2026"
    volumes:
      - ./docker/nginx:/etc/nginx/conf.d
    depends_on:
      - frontend
      - gateway
      - langgraph
```

**关键理解**:
- `depends_on`: 启动顺序（但不保证就绪）
- `environment`: 环境变量传递
- `volumes`: 挂载本地文件（nginx 配置）
- `ports`: 端口映射

---

## 🔧 配置调优 (可选)

如果性能不佳，尝试以下调整:

### 增加资源限制

编辑 `docker-compose-dev.yaml`:

```yaml
services:
  langgraph:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
  gateway:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### 启用 Buildkit 加速

```powershell
$env:DOCKER_BUILDKIT = 1
docker-compose build --parallel
```

---

## 📝 记录初始配置

为了后续参考，保存以下信息:

```markdown
# Day 3 启动成功记录

**启动方式**: [选择 A/B/C]

**启动时间**: ___

**访问 URL**:
- 统一入口: http://localhost:2026
- Gateway: http://localhost:8001
- LangGraph: http://localhost:2024
- Frontend: http://localhost:3000

**进程/容器列表**:
```

(粘贴上面的 `netstat` 或 `docker ps` 输出)

```

**观察到的 UI 行为**:
- [ ] 页面加载完毕
- [ ] 能输入消息
- [ ] 收到响应

**已验证的 API 端点**:
- [ ] POST /api/langgraph/threads
- [ ] POST /api/langgraph/threads/{id}/events
```

---

## 📚 后续步骤

### 保持服务运行

```powershell
# 选项 A/C: 保持终端打开
# 选项 B: 后台运行
docker-compose -f docker/docker-compose-dev.yaml up -d

# 停止服务
make stop
# 或
docker-compose -f docker/docker-compose-dev.yaml down
```

### 准备 Day 4

- 关闭或后台保持服务
- 准备了解 React 19 + TypeScript 基础
- 阅读 `frontend/README.md`

---

## ⏱️ 时间记录

| 任务 | 预计时间 | 实际时间 |
|------|---------|---------|
| 选择启动模式 | 5 分钟 | ___ |
| 启动服务 (选项 A) | 5-10 分钟 | ___ |
| 启动服务 (选项 B/Docker) | 10-15 分钟 | ___ |
| 启动服务 (选项 C) | 10 分钟 | ___ |
| 验证与测试 | 20-30 分钟 | ___ |
| 排查问题 (如需) | 10-30 分钟 | ___ |
| **总计** | **3-4 小时** | **___** |

---

**下一步**: 完成后，进入 Day 4-5 - 前端基础与组件系统

---

**✓ Day 3 完成标志**:
- 应用成功启动
- 浏览器能访问 http://localhost:2026
- 控制台无错误
- 能与后端 API 通信

