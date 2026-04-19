# 第7天：配置系统、错误处理和部署

**学习日期**：Day 7  
**预计投入**：5小时  
**难度等级**：⭐⭐⭐ (中等)

---

## 📚 学习目标

理解配置管理、错误处理策略和部署架构。

**关键成果**：
- ✅ 理解配置系统和加载顺序
- ✅ 理解异常体系和错误处理
- ✅ 理解日志记录
- ✅ 理解4种部署方式
- ✅ 理解测试体系

---

## 📋 任务清单

### 任务7.1：配置系统（1小时）

**配置加载顺序**：
```
1. config.yaml (主配置文件)
   ├─ models配置
   ├─ sandbox配置
   ├─ tools配置
   ├─ memory配置
   └─ ...

2. extensions_config.json (MCP和技能)
   ├─ mcpServers
   └─ skills

3. 环境变量 (覆盖文件配置)
   ├─ ANTHROPIC_API_KEY
   ├─ OPENAI_API_KEY
   └─ ...

4. 运行时修改 (最高优先级)
   └─ API调用修改配置
```

**AppConfig数据类**：
```python
@dataclass
class AppConfig:
    models: list[ModelConfig]
    sandbox: SandboxConfig
    tools: ToolsConfig
    memory: MemoryConfig
    skills: SkillsConfig
    channels: dict[str, ChannelConfig]
    
    def validate(self):
        # 检查必需字段
        # 检查格式
        # 检查API Key存在
        pass
```

**配置验证流程**：
```python
def load_config() -> AppConfig:
    # 1. 读取yaml
    with open('config.yaml') as f:
        yaml_config = yaml.safe_load(f)
    
    # 2. 解析为AppConfig
    config = AppConfig(**yaml_config)
    
    # 3. 验证
    config.validate()
    
    # 4. 环境变量覆盖
    config.override_from_env()
    
    return config
```

**动态重加载**：
```python
@router.post("/api/config/reload")
async def reload_config():
    """重加载配置（无需重启服务）"""
    new_config = load_config()
    global APP_CONFIG
    APP_CONFIG = new_config
    
    return {"status": "reloaded"}
```

**检验方式**：
- [ ] 配置的加载顺序是什么？
- [ ] 如何覆盖一个模型的API Key？
- [ ] 支持动态重加载吗？

---

### 任务7.2：错误处理和日志（1小时）

**异常体系**：
```python
class DeerFlowException(Exception):
    """基础异常"""
    pass

class SandboxException(DeerFlowException):
    """沙箱执行异常"""
    pass

class ToolExecutionException(DeerFlowException):
    """工具执行异常"""
    pass

class ConfigException(DeerFlowException):
    """配置异常"""
    pass

class MemoryException(DeerFlowException):
    """内存系统异常"""
    pass
```

**异常处理策略**：
```python
# 工具执行时
try:
    result = tool.invoke(args)
except ToolExecutionException as e:
    return ToolExecutionResult(
        success=False,
        error=str(e),
        suggestion="可能的解决方案..."
    )

# 中间件中
try:
    state = middleware(state)
except Exception as e:
    if isinstance(e, CriticalException):
        raise  # 中止执行
    else:
        log.error(f"Middleware error: {e}")
        # 继续执行
```

**日志系统**：
```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Starting agent for thread {thread_id}")
logger.warning(f"Model {model_name} not available")
logger.error(f"Failed to execute tool: {e}")
logger.debug(f"ThreadState: {state}")
```

**日志级别**：
```
DEBUG    → 详细执行流
INFO     → 关键事件
WARNING  → 警告但继续
ERROR    → 错误处理
CRITICAL → 系统崩溃
```

---

### 任务7.3：部署架构（1.5小时）

**开发部署 (make dev)**：
```
启动4个进程：

1. LangGraph Server (2024)
   - 运行: python -m langgraph.cli serve
   - 从backend/langgraph.json加载agent

2. Gateway API (8001)
   - 运行: python -m app.gateway.app
   - FastAPI应用

3. Frontend (3000)
   - 运行: pnpm dev
   - Next.js开发服务器

4. Nginx (2026)
   - 运行: nginx
   - 反向代理，统一入口
```

**Docker生产部署**：
```yaml
services:
  langgraph:
    image: deerflow:langgraph
    ports:
      - "2024:2024"
    volumes:
      - ./config.yaml:/app/config.yaml
      - threads_data:/app/thread_data
  
  gateway:
    image: deerflow:gateway
    ports:
      - "8001:8001"
    depends_on:
      - langgraph
  
  frontend:
    image: deerflow:frontend
    ports:
      - "3000:3000"
  
  nginx:
    image: nginx
    ports:
      - "2026:80"
    depends_on:
      - langgraph
      - gateway
      - frontend

volumes:
  threads_data:
```

**Kubernetes部署 (Provisioner模式)**：
```
当Agent需要高隔离任务：

1. Agent调用 provision_sandbox()
2. Provisioner(K8s controller) 收到请求
3. 创建临时Pod
4. Agent连接执行
5. 任务完成删除Pod
```

**Makefile命令**：
```makefile
make dev              # 启动4个进程
make dev-pro          # Gateway mode (嵌入Agent)
make stop             # 停止所有服务
make docker-dev       # Docker开发模式
make docker-prod      # Docker生产模式
```

**检验方式**：
- [ ] make dev启动了哪几个进程？
- [ ] Nginx的作用是什么？
- [ ] Docker部署时如何共享thread数据？

---

### 任务7.4：系统集成和测试（1小时）

**测试分类**：

**单元测试**：
```
- test_sandbox.py: Sandbox操作
- test_middlewares.py: 中间件链
- test_tools.py: 工具执行
```

**集成测试**：
```
- test_agent_e2e.py: Agent完整流程
- test_file_upload.py: 上传到处理
```

**E2E测试**：
```
- test_client_e2e.py: 完整Web流程
```

**测试框架**：
```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sandbox():
    """创建测试用沙箱"""
    return MemorySandbox('test_123')

def test_read_file(sandbox):
    sandbox.write_file('/test.txt', 'hello')
    content = sandbox.read_file('/test.txt')
    assert content == 'hello'

@pytest.mark.asyncio
async def test_agent_execution():
    """异步Agent测试"""
    agent = make_lead_agent(test_config)
    result = await agent.ainvoke({...})
    assert result['success']
```

**Mock和Fixture**：
```python
@pytest.fixture
def mock_model():
    """Mock LLM模型"""
    model = Mock()
    model.invoke.return_value = "Model response"
    return model

@pytest.fixture
def test_config():
    """测试配置"""
    return AppConfig(
        models=[...],
        sandbox=SandboxConfig(provider='local')
    )
```

**检验方式**：
- [ ] 后端的测试覆盖了哪些关键功能？
- [ ] 如何mock一个外部服务？
- [ ] 如何测试异步流程？

---

## ✅ 第7天总结

**Day 1-7的核心学习成果**：

1. 项目架构和定位
2. LangGraph和中间件链
3. Sandbox隔离机制
4. 工具系统和子Agent
5. 内存系统和技能系统
6. 模型工厂和网关API
7. 配置、错误处理和部署

**现在你已经准备好**：
- ✅ 理解整个系统设计
- ✅ 能从头重写项目
- ✅ 理解关键设计决策

---

## 🎯 Day 8开始实践重写！

**准备工作**：
- [ ] 回顾Day 1-7的核心概念
- [ ] 准备一个新项目目录
- [ ] 安装必要的依赖

**Day 8目标**：
- 项目初始化
- ThreadState定义
- 最小Agent创建

---

**Day 7 完成时间**：_____________  
**理论学习完成**：✓ / ✗  
**理解程度评分** (1-10)：_____  

**准备进入实践阶段！**

---

**文档版本**：1.0  
**最后更新**：2025-04-19

