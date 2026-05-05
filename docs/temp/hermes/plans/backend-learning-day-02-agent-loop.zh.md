# Day 02 - Agent 循环核心解剖（最重要的一天）

## 目标
完全理解 `AIAgent.run_conversation()` 的内部机制，包括消息构建、模型调用、工具执行、重试、预算控制。这是所有改造工作的基础。

## 关键文件
- `run_agent.py`（重点部分：300-500 行）
- `agent/retry_utils.py`
- `agent/error_classifier.py`

## 学习内容

### 1) AIAgent 的三个关键属性
```python
class AIAgent:
    def __init__(self, 
        model: str,              # 哪个模型
        max_iterations: int,     # 最多循环几次
        enabled_toolsets: list,  # 哪些工具可用
        ... 其他参数
    ):
        self.iteration_budget = IterationBudget(max_iterations)
        self.context_limit = 自动估算或从配置读取
        self.conversation_history = []  # 消息历史
```

**需要理解的问题**：
- 为什么需要 `IterationBudget` 而不是简单的计数器？（答：并发下可能 refund）
- `context_limit` 是硬约束还是软建议？（答：软建议，但超过会触发 fallback）
- `conversation_history` 何时清空？（答：会话结束时，不中途清空）

### 2) run_conversation() 的生命周期
```
入口: run_conversation(user_message, system_message, conversation_history)
  ↓
第 1 步: 初始化
  - 为这个 turn 准备 messages 列表
  - 组装 system message
  - 追加 conversation_history
  - 追加新的 user_message
  ↓
第 2 步: 预执行检查
  - 计算当前 tokens 数量
  - 如果接近 context_limit，决定是否压缩
  - 构建工具 schema
  ↓
第 3 步: 模型循环 (while iteration < max_iterations)
  a. 调用模型 API
     - POST /v1/chat/completions
     - 携带 messages 与 tools
  b. 解析响应
  c. 如果有 stop_reason="tool_calls"
     - 对每个 tool_call 执行工具
     - 把结果作为 "tool" role message 追加
     - 继续循环
  d. 如果有 stop_reason="end_turn" 或 content 非空
     - 直接返回 content
     ↓
第 4 步: 事后处理
  - 记录会话到 SessionDB
  - 返回最终 response
```

**你需要烙印在心的：** 消息永远在累积，循环就是"调用模型 → 执行工具 → 往消息里加结果 → 再调用"。

### 3) IterationBudget 的线程安全设计
```python
class IterationBudget:
    def consume(self) -> bool:
        """消费一次迭代，如果还有预算返回 True"""
        with self._lock:
            if self._used >= self.max_total:
                return False
            self._used += 1
            return True
    
    def refund(self) -> None:
        """退回一次迭代（用于 execute_code 等特殊工具）"""
        with self._lock:
            if self._used > 0:
                self._used -= 1
```

**为什么要 refund？** `execute_code` 工具是代理代码执行，它消耗迭代预算但不算"模型思考"，所以要退回。

### 4) 错误分类与重试策略
`error_classifier.py` 根据模型返回的错误类型决定是否重试：
- `RateLimitError` → 等待后重试（jittered backoff）
- `ContextLengthError` → 触发压缩或降级模型
- `InvalidRequestError` → 修复 schema 后重试
- 其他 → 失败

**关键**：这个分类决定了整个系统的韧性。

## 实践任务

### 任务 1: 完整流程追踪（最重要）
打开 `run_agent.py`，找到 `run_conversation()` 方法：
1. 从 `def run_conversation(` 开始
2. 逐行读代码（500-800 行代码）
3. 在代码边上标注关键检查点：
   ```
   # [检查 1] messages 组装完成
   # [检查 2] 调用模型前的 tokens 估算
   # [检查 3] 工具分发点
   # [检查 4] 循环终止条件
   ```

**输出**：画一个伪代码版本，用 Python-like 语法但去掉所有框架代码，只保留逻辑框架。

### 任务 2: IterationBudget 的单元测试
写一个 Python 脚本测试：
```python
def test_iteration_budget():
    budget = IterationBudget(max_total=3)
    
    assert budget.consume() == True   # 1st
    assert budget.consume() == True   # 2nd
    assert budget.consume() == True   # 3rd
    assert budget.consume() == False  # 预算用尽
    
    budget.refund()
    assert budget.consume() == True   # 退回了一个
    
    # 多线程测试
    from concurrent.futures import ThreadPoolExecutor
    budget2 = IterationBudget(max_total=10)
    consumed = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(lambda: budget2.consume()) for _ in range(15)]
        consumed = [f.result() for f in futures]
    assert consumed.count(True) == 10  # 只有 10 个成功
    assert consumed.count(False) == 5
```

**验收**：脚本能运行且测试通过。

### 任务 3: 模型 API 调用的结构分析
找到这一行：
```python
response = client.chat.completions.create(
    model=self.model,
    messages=messages,
    tools=tool_schemas,
    ...
)
```

分析：
- `messages` 的结构：role/content/tool_call_id
- `tools` 的来源：`get_tool_definitions()`
- `response` 的三种主要返回情况（工具调用 / 文本 / 错误）

**输出**：用 Markdown 表格列出 3 种返回情况及对应处理。

### 任务 4: 改进一个错误处理
在 `run_agent.py` 中找到 API 调用的 try-except 块：
```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    # 现在的处理
    ...
```

**改进要求**：
1. 新增一个自定义异常类型 `LLMTimeoutError`
2. 在 except 中捕获 timeout，分类为 `LLMTimeoutError`
3. 对 timeout 做特殊处理（降低 timeout 配置或立即重试）
4. 写测试验证这个改进

## 风险点与注意事项

⚠️ **不要在一天内全理解** run_agent.py - 它有 12000+ 行！分块学习。
⚠️ **重点关注**：消息循环 + 工具分发 + 预算控制，这三个不要理解错。
⚠️ **Promise cache 约束**：不能在循环中改变 system_prompt 或 tool_schemas（破坏 cache）。
⚠️ **Context 压缩**：这是唯一允许中途改变上下文的方式，有特殊处理。

## 交付物

创建 `notes/day02-agent-loop.md`：
- Agent 循环的伪代码版本（50 行以内）
- IterationBudget 的线程安全分析（200 字）
- 模型 API 返回的三种情况 + 处理方式（Markdown 表格）
- 任务 2 的单元测试脚本（工作的代码）
- 任务 4 的改进方案文档 + 测试（或已提交的改动证明）

## 验收标准

你能够：
1. ✅ 描述 run_conversation 的 4 个阶段与关键检查点
2. ✅ 解释为什么 IterationBudget 需要线程锁
3. ✅ 说出循环的三种终止条件
4. ✅ 指出为什么不能中途改变 system_prompt（与 cache 相关）
5. ✅ 实现一个简单的改进（如错误分类）并通过测试

**这一天最核心：能否不看代码，复述整个循环流程。**

