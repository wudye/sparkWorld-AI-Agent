# Day 04 - 会话持久化与 SessionDB

## 目标
掌握 SQLite WAL 模式、FTS5 全文索引、并发写入竞争控制，以及会话压缩后的链式结构。这涉及数据一致性与可靠性。

## 关键文件
- `hermes_state.py`（重点：`SessionDB` 类）
- `gateway/session.py`（会话上下文）

## 学习内容

### 1) Schema 结构分析
```sql
-- 会话表
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    source TEXT,                    -- 来源：CLI / telegram / discord
    model TEXT,                     -- 使用的模型
    parent_session_id TEXT,        -- 压缩后的父会话
    started_at REAL NOT NULL,
    ended_at REAL,
    message_count INTEGER,
    input_tokens, output_tokens,   -- 统计用量
    estimated_cost_usd REAL,
    title TEXT,
    -- ... 其他字段
);

-- 消息表
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,      -- 外键
    role TEXT,                     -- user / assistant / tool
    content TEXT,                  -- 消息内容
    tool_calls TEXT,               -- JSON 数组（工具调用）
    timestamp REAL,
    token_count INTEGER,
    reasoning TEXT,                -- 思维过程
);

-- 全文搜索
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content,
    content=messages,              -- 同步来源表
    content_rowid=id
);
```

**关键理解**：
- `parent_session_id` 链表示压缩历史
- FTS5 自动同步 messages 表的新增/删除/更新
- schema_version 用于迁移控制

### 2) 并发写入竞争的处理
```python
class SessionDB:
    def _execute_write(self, fn):
        """写入事务，处理 WAL 锁竞争"""
        for attempt in range(15):  # 最多 15 次重试
            try:
                with self._lock:  # Python 级别的锁
                    self._conn.execute("BEGIN IMMEDIATE")  # SQL 级别的锁
                    try:
                        result = fn(self._conn)
                        self._conn.commit()
                    except:
                        self._conn.rollback()
                        raise
                return result
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower():
                    # WAL 写锁竞争，随机等待后重试
                    jitter = random.uniform(0.020, 0.150)
                    time.sleep(jitter)
                else:
                    raise
```

**为什么这么复杂？**
- WAL 模式允许多个读者，但只有一个写者
- 多个 agent 进程竞争同一个 WAL 写锁会产生"队列效应"
- 应用层用随机抖动替代 SQLite 内置的确定性退避（避免队列）
- `BEGIN IMMEDIATE` 强制在事务开始时获取锁（不是等到 COMMIT）

### 3) FTS5 的自动索引与查询
```python
def search_messages(self, session_id: str, query: str, limit: int = 20):
    """全文搜索"""
    cursor = self._conn.cursor()
    cursor.execute("""
        SELECT m.id, m.role, m.content, m.timestamp
        FROM messages m
        JOIN messages_fts fts ON m.id = fts.rowid
        WHERE m.session_id = ? AND fts.content MATCH ?
        ORDER BY m.timestamp DESC
        LIMIT ?
    """, (session_id, query, limit))
    return cursor.fetchall()
```

**FTS5 的好处**：
- 快速模糊搜索（比 LIKE 快 100 倍）
- 支持布尔操作符（AND / OR / NOT）
- 自动分词

### 4) 会话压缩与链式结构
```python
# 当一个会话变得太长时
old_session_id = "session_001"

# 压缩：生成摘要，创建新会话
new_session_id = "session_001_compressed_1"

# 创建新会话，指向旧会话作为父
cursor.execute("""
    INSERT INTO sessions (id, parent_session_id, ...)
    VALUES (?, ?, ...)
""", (new_session_id, old_session_id))

# 结果：session_001 ← session_001_compressed_1 ← session_001_compressed_2
```

**为什么要链？** 
- 可以随时回溯到任何压缩点
- 分析压缩的效果
- 恢复误删的会话

## 实践任务

### 任务 1: SessionDB 的基本操作测试
```python
from hermes_state import SessionDB
from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    db = SessionDB(db_path=Path(tmpdir) / "test.db")
    
    # 创建会话
    session_id = "test_session_001"
    db.create_session(
        session_id=session_id,
        source="cli",
        model="claude-3-5-sonnet"
    )
    
    # 添加消息
    db.save_message(
        session_id=session_id,
        role="user",
        content="hello",
        token_count=5
    )
    
    # 查询消息
    messages = db.get_session_messages(session_id)
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    
    # 搜索
    results = db.search_messages(session_id, "hello")
    assert len(results) > 0
    
    print("✅ All basic operations passed")
```

**验收**：脚本能运行且通过所有断言。

### 任务 2: 并发写入压力测试
```python
from concurrent.futures import ThreadPoolExecutor
import uuid

def stress_test_concurrent_writes():
    """多线程并发写入，检查数据一致性"""
    db = SessionDB()
    session_id = str(uuid.uuid4())
    db.create_session(session_id, "cli", "test-model")
    
    def add_message(i):
        try:
            db.save_message(
                session_id=session_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                token_count=i
            )
            return True
        except Exception as e:
            print(f"Error in thread {i}: {e}")
            return False
    
    # 10 个线程，每个添加 10 条消息
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(add_message, i) for i in range(100)]
        results = [f.result() for f in futures]
    
    # 验证
    messages = db.get_session_messages(session_id)
    assert len(messages) == 100
    assert all(results)  # 所有写入都成功
    print(f"✅ Concurrent writes OK: {len(messages)} messages")
```

**验收**：能处理 100+ 并发写入而不崩溃或丢数据。

### 任务 3: Schema 迁移流程理解
查看 `hermes_state.py` 的 `_init_schema()` 和 `_migrate_*` 方法：
1. 当前 schema version 是多少？
2. 一共有多少个 migration 函数？
3. 每个 migration 改了什么？
4. 如果你要新增一个字段，应该怎么做？

**输出**：写一份文档，包括：
- 当前 schema version 及每个版本的改动
- 添加新字段的标准流程（4 步）
- 向后兼容性检查清单

### 任务 4: FTS5 查询优化
在 SessionDB 中新增一个方法：
```python
def search_messages_advanced(
    self, 
    session_id: str, 
    keywords: list,  # 必须包含的关键词
    exclude: list = None,  # 要排除的词
    limit: int = 20
):
    """高级全文搜索：必须含 keywords，不含 exclude"""
    # FTS5 布尔查询语法：
    # "keyword1 AND keyword2 NOT keyword3"
    query_terms = " AND ".join(keywords)
    if exclude:
        query_terms += " NOT " + " NOT ".join(exclude)
    
    cursor = self._conn.cursor()
    cursor.execute("""
        SELECT m.id, m.content, m.timestamp
        FROM messages m
        JOIN messages_fts fts ON m.id = fts.rowid
        WHERE m.session_id = ? AND fts.content MATCH ?
        ORDER BY m.timestamp DESC
        LIMIT ?
    """, (session_id, query_terms, limit))
    return cursor.fetchall()
```

**测试**：
```python
# 创建含多个关键词的消息
db.save_message(session_id, "user", "Tell me about Python and machine learning")
db.save_message(session_id, "user", "JavaScript is also great")

# 查询
results = db.search_messages_advanced(
    session_id,
    keywords=["python", "learning"],
    exclude=["javascript"]
)
assert len(results) == 1
```

## 风险点与注意事项

⚠️ **WAL 文件管理**：如果 WAL 文件被意外删除，数据库需要重建。生产环境要定期 checkpoint。
⚠️ **FTS5 同步延迟**：虽然有触发器，但在高并发下可能短暂不同步。
⚠️ **Schema 迁移的原子性**：ALTER TABLE 在 SQLite 中不是原子的，多个更新可能失败。
⚠️ **Disk 满**：WAL checkpoint 失败会导致 WAL 无限增长，最终写入失败。

## 交付物

创建 `notes/day04-sessiondb.md`：
- Schema ER 图
- 并发写入策略分析（200 字）
- WAL 模式的 3 个关键特性
- FTS5 查询语法速查表
- 任务 1-4 的验证截图或日志

## 验收标准

你能够：
1. ✅ 说出 WAL 与直接模式的主要区别
2. ✅ 解释为什么需要应用层重试与抖动
3. ✅ 实现一个并发安全的写入操作
4. ✅ 用 FTS5 布尔查询实现一个复杂搜索
5. ✅ 添加一个 schema 字段并编写 migration

**最后检查**：能否在 100 并发下保证数据一致性？

