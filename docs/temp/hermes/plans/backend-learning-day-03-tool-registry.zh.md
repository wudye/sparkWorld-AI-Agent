# Day 03 - 工具注册与分发机制

## 目标
理解为什么用 registry pattern，工具如何自注册，以及 schema 如何被安全地分发给模型。学会添加新工具而不破坏架构。

## 关键文件
- `tools/registry.py`
- `model_tools.py`（重点：`get_tool_definitions()`, `handle_function_call()`）
- `toolsets.py`
- `tools/web_search.py`, `tools/terminal_tool.py`（作为参考实现）

## 学习内容

### 1) Registry 的并发安全设计
```python
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolEntry] = {}  # 工具表
        self._lock = threading.RLock()            # 可重入锁
    
    def _snapshot_entries(self) -> List[ToolEntry]:
        """返回稳定快照，避免读写竞争"""
        with self._lock:
            return list(self._tools.values())
    
    def register(self, name, toolset, schema, handler, ...):
        """线程安全的注册"""
        with self._lock:
            # 检查是否存在
            if name in self._tools:
                # 只允许 MCP 对 MCP 覆盖
                ...
            self._tools[name] = ToolEntry(...)
```

**设计要点**：
- 读取时用快照，避免 iterator invalidation
- 写入时上锁
- 允许 MCP 刷新（重新注册）但禁止跨 toolset 覆盖

### 2) 工具自注册的发现机制
```python
# tools/registry.py 的 discover_builtin_tools()
def discover_builtin_tools():
    """扫描 tools/ 目录，导入含 registry.register() 的模块"""
    for path in Path("tools").glob("*.py"):
        if path.stem not in ["__init__", "registry"]:
            # AST 检查：这个模块有没有顶层 registry.register() 调用？
            if _module_registers_tools(path):
                importlib.import_module(f"tools.{path.stem}")
```

**为什么用 AST 检查？** 避免导入不必要的模块（可能有初始化开销）。

### 3) Toolset 的启用/禁用逻辑
```python
def get_tool_definitions(
    enabled_toolsets: list = None,
    disabled_toolsets: list = None,
    quiet_mode: bool = False
) -> List[Dict]:
    """根据启用/禁用列表过滤工具"""
    
    if enabled_toolsets is not None:
        # 白名单模式：只包含这些 toolset
        tools_to_include = set()
        for ts in enabled_toolsets:
            tools_to_include.update(resolve_toolset(ts))
    
    elif disabled_toolsets:
        # 黑名单模式：从全部中排除这些 toolset
        tools_to_include = get_all_tools()
        for ts in disabled_toolsets:
            tools_to_include.difference_update(resolve_toolset(ts))
    
    else:
        # 默认：全部
        tools_to_include = get_all_tools()
    
    # 检查工具可用性（API key 等）
    available = [
        schema for schema in all_schemas
        if name in tools_to_include and is_tool_available(name)
    ]
    
    return available
```

**关键**：一旦启用 toolset，就不能在运行时改变（破坏 prompt cache）。

## 实践任务

### 任务 1: 新增一个 Dummy 工具
创建 `tools/dummy_tool.py`：
```python
import json
from tools.registry import registry

def dummy_add(a: int, b: int, task_id: str = None) -> str:
    """返回两个数的和"""
    try:
        result = a + b
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

registry.register(
    name="dummy_add",
    toolset="dummy",
    schema={
        "name": "dummy_add",
        "description": "Add two numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"}
            },
            "required": ["a", "b"]
        }
    },
    handler=lambda args, **kw: dummy_add(
        a=args.get("a", 0),
        b=args.get("b", 0),
        task_id=kw.get("task_id")
    ),
    check_fn=lambda: True,  # 总是可用
    description="Add two numbers together"
)
```

在 `toolsets.py` 中挂载：
```python
"dummy": ["dummy_add"]
```

**验收**：能通过这个测试
```python
from model_tools import get_tool_definitions, handle_function_call

schemas = get_tool_definitions(enabled_toolsets=["dummy"])
assert any(s["name"] == "dummy_add" for s in schemas)

result = handle_function_call("dummy_add", {"a": 3, "b": 5})
assert json.loads(result)["result"] == 8
```

### 任务 2: 理解工具 Schema 的约束
选一个现有工具（如 `web_search`），分析其 schema：
1. 参数有哪些必需字段？
2. 参数类型是什么（string/integer/object/array）？
3. 模型如何理解这个描述来决定何时调用？
4. 如果改变描述会怎样（如去掉某个参数）？

**输出**：写一份 Markdown 文档，包括：
- 现有 schema 的完整定义
- 一个"好的"参数描述示例
- 一个"坏的"参数描述示例（模型容易误用）

### 任务 3: 实现工具可用性检查
改进任务 1 的 dummy_add 工具，添加一个环境变量依赖：
```python
def check_dummy_enabled() -> bool:
    """只有设置了 ENABLE_DUMMY_TOOL 才可用"""
    return os.getenv("ENABLE_DUMMY_TOOL") == "1"

registry.register(
    ...
    check_fn=check_dummy_enabled,
    requires_env=["ENABLE_DUMMY_TOOL"],
    ...
)
```

测试：
```python
# 环境变量未设置
schemas = get_tool_definitions(enabled_toolsets=["dummy"])
assert not any(s["name"] == "dummy_add" for s in schemas)

# 设置后
os.environ["ENABLE_DUMMY_TOOL"] = "1"
schemas = get_tool_definitions(enabled_toolsets=["dummy"])
assert any(s["name"] == "dummy_add" for s in schemas)
```

### 任务 4: 追踪工具分发到执行的全流程
1. 从 `run_agent.py` 中找到 `handle_function_call()` 的调用点
2. 追踪到 `model_tools.py` 的 `handle_function_call()` 实现
3. 追踪到 `registry.get_entry()` 与 `entry.handler()` 调用
4. 画出完整的消息流：
```
model response (tool_call)
  → run_agent 解析
  → handle_function_call(name, args)
  → registry lookup
  → check availability
  → run handler
  → return JSON
  → append to messages
```

## 风险点与注意事项

⚠️ **工具 handler 必须返回 JSON 字符串**，不能返回对象或其他类型。
⚠️ **Check function 异常处理**：如果 check_fn 抛异常，会被捕获并当作"不可用"。
⚠️ **Toolset 中途改变 = 破坏 cache**：启用后就锁定，不能改。
⚠️ **工具名冲突**：同一个工具名不能在多个 toolset 中注册。

## 交付物

创建 `notes/day03-tool-registry.md`：
- Registry 的并发设计分析（300 字）
- 工具自注册的 5 个步骤
- Dummy 工具的实现代码 + 测试验证截图
- 工具 Schema 设计的最佳实践（5 个建议）
- 完整的"请求 → 执行 → 返回"流程图

## 验收标准

你能够：
1. ✅ 不看代码，说出工具是如何被发现的
2. ✅ 添加一个新工具并验证它被正确分发
3. ✅ 解释为什么工具 handler 必须返回 JSON
4. ✅ 描述 enabled_toolsets vs disabled_toolsets 的区别
5. ✅ 指出工具可用性检查的时机（何时运行 check_fn）

**最后检查**：能否独立添加一个真实工具（如天气查询）而不引入 bug？

