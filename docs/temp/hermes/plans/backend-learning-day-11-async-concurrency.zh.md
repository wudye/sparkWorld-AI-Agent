# Day 11 - 异步桥接与并发模型

## 目标
深入理解 sync/async 的交互、工具的并行执行决策、以及如何避免死锁和资源泄漏。

## 关键文件
- `model_tools.py`（`_run_async()` 函数）
- `run_agent.py`（并行工具执行逻辑）
- `tools/delegate_tool.py`（子代理的并发处理）

## 学习内容

### 1) Sync-Async 桥接的三个场景
```python
# model_tools.py - _run_async()

def _run_async(coro):
    """从同步上下文调用异步协程"""
    
    # 场景 1：已有运行中的事件循环（Gateway 中）
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # ❌ 不能直接 await，会阻塞循环
            # ✅ 在新线程中创建新循环
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result(timeout=300)
    except RuntimeError:
        loop = None
    
    # 场景 2：Worker 线程（并行工具执行）
    if threading.current_thread() is not threading.main_thread():
        # 为这个线程创建持久循环
        worker_loop = _get_worker_loop()
        return worker_loop.run_until_complete(coro)
    
    # 场景 3：主 CLI 线程
    tool_loop = _get_tool_loop()
    return tool_loop.run_until_complete(coro)
```

**为什么这么复杂？**
- `asyncio.run()` 每次创建-销毁循环，导致缓存的 httpx 客户端在已关闭的循环上崩溃
- 持久循环让缓存客户端活着
- 但不能在已有循环中递归调用
- Worker 线程需要独立循环避免竞争

### 2) 工具的并行执行决策
```python
# run_agent.py - 并行工具执行的条件

_NEVER_PARALLEL_TOOLS = frozenset({"clarify"})  # 交互式工具不能并行
_PARALLEL_SAFE_TOOLS = frozenset({               # 只读工具安全并行
    "read_file", "web_search", "vision_analyze",
    "session_search", "skills_list", ...
})
_PATH_SCOPED_TOOLS = frozenset({"read_file", "write_file", "patch"})

def should_parallelize(tool_calls: list) -> bool:
    """决定是否并行执行工具"""
    
    # 规则 1：如果有交互式工具，禁用并行
    if any(call.name in _NEVER_PARALLEL_TOOLS for call in tool_calls):
        return False
    
    # 规则 2：如果都是安全的只读工具，可以并行
    if all(call.name in _PARALLEL_SAFE_TOOLS for call in tool_calls):
        return True
    
    # 规则 3：文件工具如果操作不同路径，可以并行
    # 复杂的逻辑...
    
    # 默认：保守，序列执行
    return False

def execute_tool_calls_parallel(tool_calls, task_id):
    """并行执行工具调用"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(handle_function_call, call.name, call.args, task_id): call
            for call in tool_calls
        }
        
        for future in as_completed(futures):
            call = futures[future]
            try:
                result = future.result(timeout=60)
                results[call.id] = result
            except Exception as e:
                results[call.id] = json.dumps({"error": str(e)})
    
    return results
```

### 3) 子代理的隔离
```python
# tools/delegate_tool.py

def delegate_task(
    task_description: str,
    required_tools: list,
    task_id: str = None
) -> str:
    """委派任务给子代理"""
    
    # 保存全局状态
    global _last_resolved_tool_names
    saved_tool_names = _last_resolved_tool_names.copy()
    
    try:
        # 创建子 Agent（独立的 IterationBudget）
        child_agent = AIAgent(
            model="claude-3-5-sonnet",
            max_iterations=50,  # 子代理预算更小
            enabled_toolsets=required_tools,  # 只启用指定工具
            session_id=f"{task_id}_child",
            platform="internal"
        )
        
        # 运行子代理
        response = child_agent.run_conversation(task_description)
        
        return json.dumps({"result": response})
    
    finally:
        # 恢复全局状态
        _last_resolved_tool_names = saved_tool_names
```

**关键**：
- 子代理有独立的 IterationBudget（不消耗父代理的）
- 工具列表受限（安全性）
- 完成后恢复全局状态（避免污染）

### 4) 资源泄漏的检测
```python
# 常见泄漏源：

# ❌ 问题 1：未关闭的异步客户端
class WebSearchTool:
    def __init__(self):
        self.client = aiohttp.ClientSession()  # 永不关闭！

# ✅ 解决：使用生命周期管理
class WebSearchTool:
    def __init__(self):
        self.client = None
    
    async def setup(self):
        self.client = aiohttp.ClientSession()
    
    async def teardown(self):
        if self.client:
            await self.client.close()

# ❌ 问题 2：事件循环未关闭
def tool_handler():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(coro())
    # loop 永不关闭！

# ✅ 解决：使用持久循环
_tool_loop = None

def _get_tool_loop():
    global _tool_loop
    if _tool_loop is None or _tool_loop.is_closed():
        _tool_loop = asyncio.new_event_loop()
    return _tool_loop
```

## 实践任务

### 任务 1: 理解三个 sync-async 场景
1. 读 `_run_async()` 的代码注释
2. 为每个场景画一个时序图：
   - 场景 1：Gateway 中的 await（需要 ThreadPool 中转）
   - 场景 2：Worker 线程（独立循环）
   - 场景 3：CLI 主线程（共享持久循环）
3. 标注关键变量：`loop`, `coro`, `future`, `result`

**输出**：3 个时序图（可用 ASCII 或简单图表）

### 任务 2: 编写一个并行安全的工具
创建 `tools/fetch_multiple.py`：
```python
"""
Fetch multiple URLs in parallel.
"""
import json
import asyncio
import aiohttp

async def fetch_url(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                return {
                    "url": url,
                    "status": resp.status,
                    "content_length": len(await resp.text())
                }
        except Exception as e:
            return {"url": url, "error": str(e)}

async def fetch_multiple_impl(urls: list) -> str:
    """并发获取多个 URL"""
    tasks = [fetch_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return json.dumps({"results": results})

def fetch_multiple(urls_str: str, task_id: str = None) -> str:
    """Fetch multiple URLs concurrently"""
    try:
        urls = urls_str.split(",")
        # 用 _run_async() 桥接
        from model_tools import _run_async
        result = _run_async(fetch_multiple_impl(urls))
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})

# 注册
from tools.registry import registry
registry.register(
    name="fetch_multiple",
    toolset="fetch_tools",
    schema={...},
    handler=lambda args, **kw: fetch_multiple(
        urls_str=args.get("urls", ""),
        task_id=kw.get("task_id")
    ),
    check_fn=lambda: True,
    is_async=True,
    description="Fetch multiple URLs in parallel"
)
```

**验收**：工具能正确并发获取多个 URL。

### 任务 3: 并行工具执行的压力测试
```python
def test_parallel_tool_execution():
    """测试并行工具执行的稳定性"""
    from run_agent import AIAgent
    import time
    
    agent = AIAgent(
        model="claude-3-5-sonnet",
        max_iterations=5
    )
    
    # 构造一个会触发多个 web_search 工具调用的 prompt
    # （这需要模型配合，实际测试中可能需要 mock）
    
    start = time.time()
    response = agent.chat("""
        Search for these topics in parallel:
        - Python performance
        - Rust async
        - Go concurrency
    """)
    elapsed = time.time() - start
    
    print(f"Response: {response[:100]}...")
    print(f"Time: {elapsed:.2f}s")
    
    # 如果串行会更慢（3 个查询 × 5s 每个 = 15s）
    # 如果并行会快得多（5s 左右）
    assert elapsed < 10, "Should be parallelized"
```

### 任务 4: 子代理隔离的验证
```python
def test_subagent_isolation():
    """验证子代理状态隔离"""
    from tools.delegate_tool import delegate_task
    
    # 模拟一个高级任务
    result = delegate_task(
        task_description="Analyze this Python code",
        required_tools=["read_file", "vision_analyze"],
        task_id="main_task_001"
    )
    
    result_dict = json.loads(result)
    assert "result" in result_dict
    
    # 验证：
    # 1. 子代理的 session_id 包含 "_child"
    # 2. 子代理的工具集只有指定的两个
    # 3. 完成后全局 _last_resolved_tool_names 已恢复
```

## 风险点与注意事项

⚠️ **事件循环递归** - 在已有循环的上下文中调用 `asyncio.run()` 会崩溃。
⚠️ **资源泄漏** - 每个 `asyncio.run()` 创建一个循环但不清理，导致 unclosed loop 警告。
⚠️ **线程竞争** - 多线程同时写入同一个文件可能导致数据损坏。
⚠️ **超时与死锁** - 子代理卡住会阻塞父代理，需要设置合理超时。

## 交付物

创建 `notes/day11-async-concurrency.md`：
- 三个 sync-async 场景的时序图
- 工具并行执行的决策规则
- 子代理隔离机制
- 任务 1-4 的代码与验证
- 资源泄漏的常见源与修复

## 验收标准

你能够：
1. ✅ 解释三个 sync-async 场景的区别
2. ✅ 实现一个并行安全的异步工具
3. ✅ 分析工具调用的并行可行性
4. ✅ 理解子代理的状态隔离
5. ✅ 识别和修复资源泄漏

**最后检查**：能否在并发 10 个工具调用的压力下保持稳定？

