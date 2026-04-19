# Day 08 - Gateway 与多平台适配器

## 目标
理解网关的生命周期、平台适配器的初始化与消息流、以及如何安全地添加新平台支持。

## 关键文件
- `gateway/run.py`（网关核心）
- `gateway/session.py`（会话状态）
- `gateway/platforms/` 中的任意一个适配器（如 telegram.py）

## 学习内容

### 1) 网关的启动顺序
```python
# gateway/run.py - main()

async def main():
    """网关启动流程"""
    
    # 第 1 步：环境准备
    _ensure_ssl_certs()  # CA 证书引导（NixOS 等特殊系统）
    
    # 第 2 步：配置加载
    load_hermes_dotenv()  # .env
    config = load_config_yaml()  # config.yaml → 桥接到 env
    
    # 第 3 步：验证配置
    print_config_warnings()  # 警告不完整的配置
    
    # 第 4 步：初始化 SessionDB
    db = SessionDB()
    
    # 第 5 步：启动平台适配器
    adapters = []
    if config.get("telegram", {}).get("enabled"):
        adapters.append(TelegramAdapter(db))
    if config.get("discord", {}).get("enabled"):
        adapters.append(DiscordAdapter(db))
    if config.get("slack", {}).get("enabled"):
        adapters.append(SlackAdapter(db))
    # ...
    
    # 第 6 步：启动事件循环
    tasks = [adapter.start() for adapter in adapters]
    await asyncio.gather(*tasks)
```

**关键**：
- 环境 > 配置文件 > 代码默认
- 所有平台共享一个 SessionDB
- 异步并发启动多个平台

### 2) 配置桥接：config.yaml → 环境变量
```python
# gateway/run.py 中的一段

# 读取 config.yaml
with open(config_path) as f:
    cfg = yaml.safe_load(f)

# 桥接 terminal 配置到环境变量
terminal_cfg = cfg.get("terminal", {})
for cfg_key, env_var in {
    "backend": "TERMINAL_ENV",
    "cwd": "TERMINAL_CWD",
    "timeout": "TERMINAL_TIMEOUT",
}.items():
    if cfg_key in terminal_cfg:
        os.environ[env_var] = str(terminal_cfg[cfg_key])

# 桥接 agent 配置
agent_cfg = cfg.get("agent", {})
if "max_turns" in agent_cfg:
    os.environ["HERMES_MAX_ITERATIONS"] = str(agent_cfg["max_turns"])

# 这样，AIAgent 启动时直接用 os.getenv() 就能读到
```

**为什么要桥接？** 
- 配置文件是用户友好的（YAML）
- 但下游代码都用 os.getenv()
- 桥接让两个世界对接

### 3) 平台适配器的标准接口
```python
# gateway/platforms/telegram.py（作为示例）

class TelegramAdapter:
    def __init__(self, db: SessionDB):
        self.db = db
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.client = TelegramClient(self.token)
    
    async def start(self):
        """启动适配器"""
        try:
            await self.client.connect()
            await self.handle_updates()
        except Exception as e:
            logger.error(f"Telegram adapter error: {e}")
    
    async def handle_updates(self):
        """处理平台事件"""
        async for update in self.client.get_updates():
            if update.type == "message":
                await self.on_message(update)
            elif update.type == "callback_query":
                await self.on_callback(update)
    
    async def on_message(self, event):
        """处理用户消息"""
        chat_id = event.chat.id
        user_text = event.text
        
        # 1. 检查或创建会话
        session_key = f"telegram_{chat_id}"
        session = self.db.get_session(session_key)
        if not session:
            self.db.create_session(session_key, source="telegram", ...)
        
        # 2. 运行 Agent
        agent = get_or_create_agent(session_key)
        response = agent.chat(user_text)  # 同步调用
        
        # 3. 发送回复
        await self.client.send_message(chat_id, response)
        
        # 4. 会话已自动持久化（agent.chat() 内部）
    
    async def stop(self):
        """停止适配器"""
        await self.client.disconnect()
```

**关键特性**：
- 统一的适配器接口（start / stop）
- 事件驱动（handle_updates）
- 会话隔离（session_key 基于平台 ID）
- 共享 SessionDB

### 4) Agent 缓存与会话管理
```python
# gateway/run.py

_agent_cache = {}  # {session_key: AIAgent}
_agent_cache_max_size = 128
_agent_cache_idle_ttl_secs = 3600.0  # 1 小时

def get_or_create_agent(session_key: str) -> AIAgent:
    """获取或创建会话的 agent（缓存）"""
    
    # 1. 检查缓存
    if session_key in _agent_cache:
        agent, last_used = _agent_cache[session_key]
        agent._last_used = time.time()
        return agent
    
    # 2. 创建新的
    agent = AIAgent(
        model="claude-3-5-sonnet",
        max_iterations=90,
        enabled_toolsets=[...],
        session_id=session_key,
        platform="gateway"
    )
    
    # 3. 缓存
    _agent_cache[session_key] = (agent, time.time())
    
    # 4. 如果缓存满了，LRU 驱逐
    if len(_agent_cache) > _agent_cache_max_size:
        oldest_key = min(
            _agent_cache.keys(),
            key=lambda k: _agent_cache[k][1]
        )
        del _agent_cache[oldest_key]
    
    return agent
```

**设计要点**：
- LRU + 空闲 TTL 双驱逐
- 避免长期网关内存泄漏
- 每个会话的 Agent 是独立的

## 实践任务

### 任务 1: 配置桥接的完整流程
1. 打开 `gateway/run.py` 找到配置桥接代码
2. 列出所有被桥接的配置项（terminal / agent / auxiliary / display）
3. 对每一项，写下：
   - 配置键名（如 "terminal.backend"）
   - 对应的环境变量（如 "TERMINAL_ENV"）
   - 预期的值范围
   - 默认值

**输出**：桥接配置表

### 任务 2: 模拟一个简单的平台适配器
创建 `gateway/platforms/debug_adapter.py`：
```python
import asyncio
import logging
from gateway.session import SessionStore

logger = logging.getLogger(__name__)

class DebugAdapter:
    """模拟一个文本输入的调试适配器"""
    
    def __init__(self, db):
        self.db = db
        self.running = False
    
    async def start(self):
        """启动，然后从 stdin 读取命令"""
        self.running = True
        print("Debug adapter started. Type messages (quit to exit):")
        
        while self.running:
            try:
                # 这里应该是 async stdin，但为简化用 sync 示例
                user_input = input("> ")
                if user_input.lower() == "quit":
                    self.running = False
                    break
                
                # 获取或创建会话
                session_key = "debug_session"
                session = self.db.get_session(session_key)
                if not session:
                    self.db.create_session(
                        session_key, 
                        source="debug",
                        model="test"
                    )
                
                # 运行 agent（这里应该是实际的 agent 调用）
                # response = agent.chat(user_input)
                print(f"[Echo] {user_input}")
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logger.error(f"Debug adapter error: {e}")
    
    async def stop(self):
        """停止适配器"""
        self.running = False
```

**验收**：能从命令行读取输入并打印回复。

### 任务 3: Agent 缓存的压力测试
```python
def test_agent_cache_lru():
    """测试 LRU 驱逐"""
    from gateway.run import get_or_create_agent, _agent_cache
    
    # 清空缓存
    _agent_cache.clear()
    
    # 创建 5 个会话的 agent
    agents = {}
    for i in range(5):
        session_key = f"test_session_{i}"
        agent = get_or_create_agent(session_key)
        agents[session_key] = agent
        time.sleep(0.1)  # 确保时间差
    
    assert len(_agent_cache) == 5
    
    # 记录最旧的会话
    oldest_key = min(_agent_cache.keys(), key=lambda k: _agent_cache[k][1])
    
    # 创建 6 个更多会话，会触发 LRU
    # 假设缓存大小限制是 128，这里只演示概念
    # 实际测试应该设置较小的 max_size
    
    # 验证：最旧的会话应该被驱逐
    # assert oldest_key not in _agent_cache
```

### 任务 4: 多平台并发处理
设计一个测试，同时从 3 个平台发送消息：
```python
async def test_multi_platform_concurrent():
    """模拟多平台并发消息"""
    db = SessionDB()
    
    async def send_from_platform(platform_name, message_count):
        """模拟一个平台发送多条消息"""
        for i in range(message_count):
            session_key = f"{platform_name}_session"
            
            # 创建会话
            db.create_session(session_key, source=platform_name)
            
            # 保存消息
            db.save_message(
                session_id=session_key,
                role="user",
                content=f"Message {i} from {platform_name}"
            )
    
    # 并发执行
    await asyncio.gather(
        send_from_platform("telegram", 10),
        send_from_platform("discord", 10),
        send_from_platform("slack", 10)
    )
    
    # 验证：30 条消息全部保存
    all_sessions = db.get_all_sessions()
    total_messages = sum(s["message_count"] for s in all_sessions)
    assert total_messages == 30
```

## 风险点与注意事项

⚠️ **平台凭证隔离** - 每个平台的 token 应该独立存储，不要混淆。
⚠️ **会话隔离** - 不同平台的同一用户应该有不同的 session_key（如 "telegram_123" vs "discord_456"）。
⚠️ **Agent 缓存泄漏** - 长期运行网关，必须有 TTL 驱逐，否则内存会无限增长。
⚠️ **异步陷阱** - 平台适配器都是异步，但 AIAgent.chat() 是同步的，需要合理过渡。

## 交付物

创建 `notes/day08-gateway.md`：
- 网关启动顺序流程图
- 配置桥接的完整表格
- 平台适配器的标准接口说明
- Agent 缓存管理策略
- 任务 1-4 的代码与验证

## 验收标准

你能够：
1. ✅ 描述网关的 6 个启动步骤
2. ✅ 解释为什么需要配置桥接
3. ✅ 实现一个简单的平台适配器
4. ✅ 分析 Agent 缓存的 LRU 策略
5. ✅ 设计多平台并发安全性测试

**最后检查**：能否同时接收 3 个平台的消息而不互相干扰？

