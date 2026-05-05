# Hermes Agent 完整技术规范文档

---

## 第一部分：后端详细设计

### 1. Agent 循环详解

#### 1.1 消息组织

```python
messages = [
    {
        "role": "system",
        "content": build_system_prompt(
            agent_identity=AGENT_IDENTITY,
            platform_hints=PLATFORM_HINTS[platform],
            tool_guidance=TOOL_USE_ENFORCEMENT,
            memory_block=build_memory_context(),
            skills_block=build_skills_system_prompt(),
            context_files=optional_context,
        )
    },
    # ... 会话历史 ...
    {
        "role": "user",
        "content": user_input,
    }
]
```

#### 1.2 工具执行的完整流程

```python
# 步骤 1: 模型返回工具调用
response = client.chat.completions.create(
    model=self.model,
    messages=messages,
    tools=schemas,  # 工具定义列表
)

# 步骤 2: 检查工具调用
for tool_call in response.tool_calls:
    # 步骤 3: 危险检测
    is_dangerous, pattern, desc = detect_dangerous_command(tool_call.name)
    if is_dangerous:
        approval_result = request_approval(pattern, session_key)
        if approval_result == "deny":
            continue
    
    # 步骤 4: 分发工具
    result = handle_function_call(
        tool_call.name,
        tool_call.arguments,
        task_id=self.session_id
    )
    
    # 步骤 5: 追加结果
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result  # 必须是 JSON 字符串
    })

# 步骤 6: 继续循环
```

#### 1.3 IterationBudget 的线程安全设计

```python
class IterationBudget:
    def __init__(self, max_total: int):
        self._max_total = max_total
        self._used = 0
        self._lock = threading.RLock()
    
    def consume(self) -> bool:
        """尝试消费一个迭代"""
        with self._lock:
            if self._used >= self._max_total:
                return False
            self._used += 1
            return True
    
    def refund(self) -> None:
        """退回一个迭代（如 execute_code 工具）"""
        with self._lock:
            if self._used > 0:
                self._used -= 1
```

#### 1.4 错误恢复流程

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        response = client.chat.completions.create(...)
        break
    except RateLimitError as e:
        wait_time = jittered_backoff(attempt, base=2, jitter=0.1)
        time.sleep(wait_time)
        continue
    except ContextLengthError as e:
        # 选项 1: 压缩
        messages = compress_context(messages)
        # 选项 2: 降级模型
        self.model = downgrade_model(self.model)
        continue
    except Exception as e:
        logger.error(f"Unrecoverable error: {e}")
        raise
```

### 2. 工具系统深入

#### 2.1 工具注册表的并发安全性

```python
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolEntry] = {}
        self._lock = threading.RLock()
    
    def register(self, entry: ToolEntry) -> None:
        """线程安全的注册"""
        with self._lock:
            if entry.name in self._tools:
                # 检查覆盖权限
                old_toolset = self._tools[entry.name].toolset
                new_toolset = entry.toolset
                
                # 只允许 MCP 对 MCP 覆盖
                if not (old_toolset.startswith("mcp") and new_toolset.startswith("mcp")):
                    raise ValueError(f"Cannot override {entry.name}")
            
            self._tools[entry.name] = entry
    
    def _snapshot_entries(self) -> List[ToolEntry]:
        """返回稳定快照"""
        with self._lock:
            return list(self._tools.values())
    
    def get_enabled_tools(self, enabled_toolsets, disabled_toolsets):
        """获取启用的工具"""
        entries = self._snapshot_entries()
        
        tools_to_include = set()
        for entry in entries:
            if enabled_toolsets and entry.toolset not in enabled_toolsets:
                continue
            if disabled_toolsets and entry.toolset in disabled_toolsets:
                continue
            
            # 检查可用性
            if not entry.check_fn():
                continue
            
            tools_to_include.add(entry.name)
        
        return tools_to_include
```

#### 2.2 工具 Schema 规范

```python
{
    "name": "web_search",
    "description": "Search the web for information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results (default 10)",
                "default": 10
            },
            "include_snippets": {
                "type": "boolean",
                "description": "Include search snippets",
                "default": True
            }
        },
        "required": ["query"]
    }
}
```

### 3. SessionDB 深入

#### 3.1 并发写入控制

```python
def _execute_write(self, fn: Callable) -> Any:
    """
    执行写入事务，处理 WAL 竞争
    
    策略：
    - 使用 BEGIN IMMEDIATE 强制获取写锁
    - 应用层随机抖动重试（避免竞争队列）
    - 指数退避
    """
    for attempt in range(15):
        try:
            with self._lock:  # Python 级锁
                self._conn.execute("BEGIN IMMEDIATE")  # SQL 级锁
                try:
                    result = fn(self._conn)
                    self._conn.commit()
                    return result
                except Exception:
                    self._conn.rollback()
                    raise
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                # WAL 写锁竞争 → 随机等待
                wait_time = random.uniform(0.020 * (2 ** attempt), 0.150)
                time.sleep(wait_time)
                continue
            raise
    
    raise TimeoutError("Database locked after 15 retries")
```

#### 3.2 FTS5 索引维护

```sql
-- 虚表定义
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content,
    content=messages,     -- 同步源表
    content_rowid=id      -- 行 ID 映射
);

-- 自动同步触发器
CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER messages_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content) 
    VALUES('delete', old.id, old.content);
END;

-- 查询
SELECT m.id, m.content, m.timestamp
FROM messages m
JOIN messages_fts fts ON m.id = fts.rowid
WHERE m.session_id = ? AND fts.content MATCH ?
ORDER BY m.timestamp DESC;
```

#### 3.3 会话链的管理

```python
# 会话压缩后的链
session_001
  ↓ parent_session_id
session_001_compressed_1
  ↓ parent_session_id
session_001_compressed_2

# 查询完整历史
def get_full_session_chain(session_id):
    chain = []
    current = session_id
    
    while current:
        session = db.get_session(current)
        chain.append(session)
        current = session.get('parent_session_id')
    
    return chain
```

### 4. Context 管理与缓存

#### 4.1 Token 估算

```python
def estimate_tokens(text: str) -> int:
    """粗略估算（快速，用于实时检查）"""
    # 启发式：英文约 4 字符/token，中文约 1-2 字符/token
    if is_chinese(text):
        return len(text) // 1.5
    else:
        return len(text) // 4

def accurate_token_count(messages: list, model: str) -> int:
    """精确计数（较慢，用于最终确认）"""
    from tiktoken import encoding_for_model
    
    try:
        enc = encoding_for_model(model)
    except KeyError:
        enc = encoding_for_model("gpt-3.5-turbo")  # 后备方案
    
    total = 0
    for msg in messages:
        # 每条消息约 4 token 的开销
        total += 4
        total += len(enc.encode(msg.get("content", "")))
        
        if msg.get("tool_calls"):
            for call in msg["tool_calls"]:
                total += len(enc.encode(json.dumps(call)))
    
    return total
```

#### 4.2 Prompt Cache 的安全性约束

```python
def validate_cache_consistency(messages, system_prompt, tools):
    """检查缓存是否仍然有效"""
    
    # 约束 1: System prompt 不变
    current_system = messages[0].get("content", "")
    if current_system != system_prompt:
        logger.warning("System prompt changed - cache invalidated")
        return False
    
    # 约束 2: 工具列表不变
    current_tools_hash = hash(json.dumps(tools, sort_keys=True))
    if current_tools_hash != self._cached_tools_hash:
        logger.warning("Tools changed - cache invalidated")
        return False
    
    # 约束 3: 消息前缀不变（仅允许追加）
    if len(messages) < len(self._cached_messages):
        logger.warning("Messages were removed - cache invalidated")
        return False
    
    for i, (cached, current) in enumerate(zip(self._cached_messages, messages[:len(self._cached_messages)])):
        if cached != current:
            logger.warning(f"Message {i} changed - cache invalidated")
            return False
    
    return True
```

---

## 第二部分：前端详细设计

### 1. TUI 架构

#### 1.1 React + Ink 的组件模型

```typescript
// TUI 基础组件
function HermesApp() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (text: string) => {
    setLoading(true);
    const response = await gateway.sendMessage(text);
    setMessages([...messages, response]);
    setLoading(false);
  };

  return (
    <Box flexDirection="column" padding={1}>
      <MessageList messages={messages} />
      <InputBox
        value={input}
        onChange={setInput}
        onSubmit={handleSubmit}
        loading={loading}
      />
    </Box>
  );
}
```

#### 1.2 JSON-RPC 协议

```typescript
// 请求格式
interface Request {
  jsonrpc: "2.0";
  id: string;
  method: string;  // "send_message", "get_history", etc.
  params: Record<string, any>;
}

// 响应格式
interface Response {
  jsonrpc: "2.0";
  id: string;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

// 事件流
interface Event {
  type: "message" | "typing" | "error" | "status";
  data: any;
}
```

#### 1.3 状态管理（nanostores）

```typescript
import { atom } from "nanostores";

// 原子状态
export const messagesStore = atom<Message[]>([]);
export const inputStore = atom<string>("");
export const loadingStore = atom<boolean>(false);
export const sessionStore = atom<string>("");

// 派生状态
export const lastMessageStore = computed(
  messagesStore,
  (msgs) => msgs[msgs.length - 1]
);
```

### 2. Web 前端架构

#### 2.1 React Router 路由

```typescript
const router = createBrowserRouter([
  {
    path: "/",
    element: <ChatPage />,
  },
  {
    path: "/history",
    element: <HistoryPage />,
  },
  {
    path: "/settings",
    element: <SettingsPage />,
  },
  {
    path: "/skills",
    element: <SkillsPage />,
  },
]);
```

#### 2.2 Tailwind CSS 组件

```typescript
// 统一的组件库
<Card className="bg-white shadow-lg rounded-lg p-4">
  <h2 className="text-xl font-bold mb-2">Title</h2>
  <p className="text-gray-600">Content</p>
</Card>
```

### 3. TUI Gateway 设计

#### 3.1 双向通信

```
TUI (TypeScript)
  ↓ (JSON-RPC request on stdout)
Python Gateway
  ↓ (处理，调用 AIAgent)
Python Backend
  ↓ (结果)
Python Gateway
  ↓ (JSON-RPC response on stdin)
TUI (TypeScript)
```

#### 3.2 斜杠命令处理

```python
# tui_gateway/slash_worker.py
async def handle_slash_command(command: str, args: list):
    if command == "config":
        if args[0] == "show":
            return load_cli_config()
        elif args[0] == "set":
            return update_config(args[1], args[2])
    elif command == "skill":
        if args[0] == "list":
            return list_skills()
        elif args[0] == "run":
            return run_skill(args[1], args[2:])
    # ... 更多命令
```

---

## 第三部分：集成点与数据绑定

### 1. 请求-响应流程

```
[用户输入]
  ↓
TUI Input Handler
  ↓
RPC 请求: {method: "send_message", params: {text: "..."}}
  ↓
Python Gateway (stdin 读取)
  ↓
Session 管理
  ↓
AIAgent.run_conversation()
  ↓
SessionDB 保存
  ↓
RPC 响应: {result: {text: "...", session_id: "..."}}
  ↓
TUI 显示
  ↓
[消息显示]
```

### 2. 实时流式输出

```typescript
// TUI 的流式处理
async function *streamResponse(sessionId: string) {
  const stream = await gateway.streamMessage(sessionId);
  
  for await (const chunk of stream) {
    switch (chunk.type) {
      case "text":
        yield { type: "text", data: chunk.data };
        break;
      case "tool_call":
        yield { type: "tool", name: chunk.name, args: chunk.args };
        break;
      case "tool_result":
        yield { type: "result", data: chunk.result };
        break;
      case "done":
        yield { type: "complete" };
        break;
    }
  }
}
```

---

## 第四部分：性能优化策略

### 1. Token 优化

```python
# 优化 1: Prompt Cache
# 省 50% token 在后续请求

# 优化 2: Context 压缩
# 当接近 limit 时触发压缩
# 省 30% token

# 优化 3: 工具结果摘要
# 只保留关键信息
def summarize_tool_result(result: str, max_tokens: int = 100) -> str:
    if len(result) < max_tokens * 4:
        return result
    # 调用辅助 LLM 生成摘要
    return auxiliary_client.summarize(result, max_tokens)
```

### 2. 并发优化

```python
# 并行工具执行
async def execute_tools_parallel(tool_calls: list):
    tasks = [
        handle_function_call(call.name, call.arguments)
        for call in tool_calls
    ]
    results = await asyncio.gather(*tasks)
    return results

# 预期加速: 2-3x（取决于工具数量和耗时）
```

### 3. 缓存策略

```python
# 三层缓存
1. Prompt Cache (LLM API 级)
   - 最新 1-2 请求
   - 省 50% token

2. Context 摘要缓存 (内存)
   - LRU 最近 10 个会话
   - 快速恢复

3. SessionDB 索引 (SQLite FTS5)
   - 全部会话
   - 快速搜索
```

---

## 第五部分：扩展与定制

### 1. 添加新工具的完整检查表

- [ ] 创建 `tools/my_tool.py`
- [ ] 实现 `my_handler(args, task_id) -> str`
- [ ] 在 `toolsets.py` 中注册 toolset
- [ ] 调用 `registry.register(...)`
- [ ] 添加 `check_fn()` 验证依赖
- [ ] 添加测试 `tests/tools/test_my_tool.py`
- [ ] 更新文档
- [ ] 运行 `scripts/run_tests.sh` 验证
- [ ] 提交 PR

### 2. 添加新平台的完整检查表

- [ ] 创建 `gateway/platforms/my_platform.py`
- [ ] 继承 `BasePlatformAdapter`
- [ ] 实现 `async def start()`
- [ ] 实现 `async def on_message(event)`
- [ ] 实现 `async def send_message(chat_id, text)`
- [ ] 在 `gateway/run.py` 中集成
- [ ] 添加配置支持
- [ ] 测试消息流
- [ ] 处理错误恢复
- [ ] 提交 PR

---

## 第六部分：部署与运维

### 1. Docker 部署

```dockerfile
FROM python:3.11

WORKDIR /app
COPY . .

# 安装依赖
RUN pip install -e .

# 暴露网关端口（可选）
EXPOSE 5000

# 启动
CMD ["hermes"]
```

### 2. 生产环境建议

```bash
# 使用 systemd 服务
# /etc/systemd/user/hermes-gateway.service
[Unit]
Description=Hermes Agent Gateway
After=network.target

[Service]
Type=simple
ExecStart=/path/to/python -m gateway.run
Restart=always
RestartSec=10
Environment="OPENAI_API_KEY=..."

[Install]
WantedBy=default.target

# 启用
systemctl --user enable hermes-gateway
systemctl --user start hermes-gateway
```

---

**文档完成**  
**版本**: 2.0  
**最后更新**: 2026-04-19

