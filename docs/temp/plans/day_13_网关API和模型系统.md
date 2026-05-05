# 第13天：网关API + 模型系统

**学习日期**：Day 13  
**预计投入**：8小时  
**难度等级**：⭐⭐⭐ (中等)

---

## 🎯 今日目标

实现FastAPI网关和模型工厂。

---

## 📋 任务清单

### 任务13.1：模型工厂（2小时）

```python
# deerflow/models/factory.py

from abc import ABC
from typing import Optional

class ModelFactory:
    """模型工厂"""
    
    @staticmethod
    def create_model(config: dict):
        """创建模型实例"""
        provider = config.get('provider')
        
        if provider == 'anthropic':
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=config.get('name'),
                api_key=config.get('api_key'),
                temperature=config.get('temperature', 0.7)
            )
        elif provider == 'openai':
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=config.get('name'),
                api_key=config.get('api_key'),
                temperature=config.get('temperature', 0.7)
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

### 任务13.2：FastAPI应用（1.5小时）

```python
# app/gateway/app.py

from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    print("Gateway starting")
    yield
    # 关闭
    print("Gateway stopping")

app = FastAPI(lifespan=lifespan)

# 健康检查
@app.get("/health")
async def health():
    return {"status": "ok"}
```

### 任务13.3：API路由（3.5小时）

```python
# app/gateway/routers/models.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/models", tags=["models"])

class ModelInfo(BaseModel):
    name: str
    provider: str
    capabilities: list[str]

@router.get("")
async def list_models() -> list[ModelInfo]:
    """列表所有模型"""
    return [
        ModelInfo(name="claude-opus", provider="anthropic", capabilities=["thinking"]),
        ModelInfo(name="gpt-4", provider="openai", capabilities=["vision"]),
    ]

@router.get("/{name}")
async def get_model(name: str) -> ModelInfo:
    """获取模型详情"""
    return ModelInfo(name=name, provider="anthropic", capabilities=[])
```

```python
# app/gateway/routers/uploads.py

from fastapi import APIRouter, UploadFile
import os

router = APIRouter(prefix="/api/threads", tags=["uploads"])

@router.post("/{thread_id}/uploads")
async def upload_file(thread_id: str, file: UploadFile):
    """上传文件"""
    # 简单实现
    return {
        "path": f"/mnt/user-data/uploads/{file.filename}",
        "size": len(await file.read())
    }
```

```python
# app/gateway/routers/artifacts.py

from fastapi import APIRouter

router = APIRouter(prefix="/api/threads", tags=["artifacts"])

@router.get("/{thread_id}/artifacts")
async def list_artifacts(thread_id: str):
    """列表工件"""
    return []

@router.get("/{thread_id}/artifacts/{name}")
async def download_artifact(thread_id: str, name: str):
    """下载工件"""
    return {"path": f"/mnt/user-data/outputs/{name}"}
```

### 任务13.4：集成测试（1小时）

```python
# tests/test_gateway.py

import pytest
from fastapi.testclient import TestClient
from app.gateway.app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_list_models():
    response = client.get("/api/models")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

---

## ✅ Day 13检验清单

**模型系统**：
- [ ] 模型工厂实现 ✓ / ✗
- [ ] 多模型支持 ✓ / ✗

**FastAPI网关**：
- [ ] FastAPI应用启动 ✓ / ✗
- [ ] 所有路由可访问 ✓ / ✗
- [ ] 数据格式正确 ✓ / ✗

**测试**：
- [ ] API测试通过 ✓ / ✗

---

**Day 13 完成时间**：_____________  
**API端点数**：约 ___ 个

---

**文档版本**：1.0

