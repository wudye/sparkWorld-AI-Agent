# Day 13 - 模型路由与元数据管理

## 目标
理解不同模型的能力差异、Context 约束、以及如何安全地降级或切换模型。这涉及成本优化与可靠性。

## 关键文件
- `agent/model_metadata.py`
- `agent/smart_model_routing.py`
- `agent/models_dev.py`
- `run_agent.py`（模型选择与 fallback）

## 学习内容

### 1) 模型的元数据
```python
# agent/model_metadata.py

MODEL_METADATA = {
    "claude-3-5-sonnet": {
        "provider": "anthropic",
        "context_length": 200000,
        "max_output_tokens": 4096,
        "cost_input_1m_tokens": 3.0,    # 美元
        "cost_output_1m_tokens": 15.0,
        "supports_vision": True,
        "supports_tools": True,
        "latency_percentile_p95": 3.5,  # 秒
    },
    "gpt-4-turbo": {
        "provider": "openai",
        "context_length": 128000,
        "max_output_tokens": 4096,
        "cost_input_1m_tokens": 10.0,
        "cost_output_1m_tokens": 30.0,
        "supports_vision": True,
        "supports_tools": True,
        "latency_percentile_p95": 5.0,
    },
    # ... 20+ 个模型
}

def get_context_length(model: str) -> int:
    """获取模型的 context 长度"""
    if model in MODEL_METADATA:
        return MODEL_METADATA[model]["context_length"]
    
    # 动态查询（models.dev registry）
    try:
        return fetch_model_metadata_from_registry(model)
    except:
        return 4096  # 保守的默认值

def estimate_tokens(text: str) -> int:
    """粗略估算文本的 token 数"""
    # 简单启发式：英文 ~4 chars per token
    return len(text) // 4

def estimate_request_tokens(messages: list, tools: list) -> int:
    """估算完整 request 的 token 数"""
    total = 0
    
    # 消息内容
    for msg in messages:
        total += estimate_tokens(msg.get("content", ""))
    
    # 工具 schema（粗略）
    tool_schema_str = json.dumps(tools)
    total += estimate_tokens(tool_schema_str)
    
    # 缓冲（系统开销）
    total += 500
    
    return total
```

### 2) Context 溢出的处理
```python
# run_agent.py - 当接近 context 限制时的决策

def should_compress_context(self, messages: list, estimated_tokens: int):
    """判断是否需要压缩"""
    context_limit = self.context_limit
    
    # 规则 1：使用了 prompt cache 就不压缩（破坏 cache）
    if self.use_anthropic_cache and estimated_tokens < 0.9 * context_limit:
        return False
    
    # 规则 2：接近 90% 就开始考虑
    if estimated_tokens > 0.9 * context_limit:
        # 规则 3：如果能通过降级模型解决，不压缩
        if self.can_downgrade_model():
            return False
        
        # 规则 4：最后才压缩
        return True
    
    return False

def can_downgrade_model(self) -> bool:
    """是否有更便宜的替代模型"""
    if self.model == "gpt-4-turbo":
        # 降级到 gpt-3.5-turbo
        return True
    elif self.model == "claude-3-5-sonnet":
        # 降级到 claude-3-haiku
        return True
    return False

def downgrade_and_retry(self):
    """降级模型并重试"""
    downgrade_map = {
        "gpt-4-turbo": "gpt-3.5-turbo",
        "claude-3-5-sonnet": "claude-3-haiku",
    }
    
    new_model = downgrade_map.get(self.model)
    if not new_model:
        raise ContextLengthExceeded()
    
    logger.info(f"Downgrading {self.model} → {new_model}")
    self.model = new_model
    
    # 重新尝试
    return self.run_conversation(...)
```

### 3) 模型路由的智能决策
```python
# agent/smart_model_routing.py

class ModelRouter:
    """智能模型选择"""
    
    def select_best_model(self, 
        task_type: str,
        context_size: int,
        budget: float = None
    ) -> str:
        """根据任务类型和约束选择最佳模型"""
        
        # 第 1 步：过滤满足 context 要求的模型
        candidates = [
            m for m in MODEL_METADATA.keys()
            if MODEL_METADATA[m]["context_length"] >= context_size
        ]
        
        # 第 2 步：按任务类型排序
        if task_type == "vision":
            # 视觉任务需要强大的视觉能力
            candidates = [m for m in candidates if MODEL_METADATA[m]["supports_vision"]]
        elif task_type == "coding":
            # 编码任务偏向开源模型的某些优势
            pass
        
        # 第 3 步：按成本排序（如果有预算限制）
        if budget:
            candidates = self._filter_by_cost(candidates, budget)
        
        # 第 4 步：返回排名第一的
        if candidates:
            return candidates[0]
        
        # 回退
        return "claude-3-5-sonnet"  # 最保险的选择
```

### 4) 错误分类与自动降级
```python
# agent/error_classifier.py

def classify_api_error(error_response: dict) -> FailoverReason:
    """分类 API 错误，决定重试策略"""
    
    error_code = error_response.get("error", {}).get("code")
    error_message = error_response.get("error", {}).get("message", "")
    
    # 速率限制 → 指数退避重试
    if error_code == "rate_limit_exceeded":
        return FailoverReason.RATE_LIMIT
    
    # Context 溢出 → 考虑压缩或降级
    if "context_length_exceeded" in error_message.lower():
        return FailoverReason.CONTEXT_LENGTH
    
    # Token 不足 → 立即降级
    if error_code == "invalid_request_error" and "max_tokens" in error_message:
        return FailoverReason.TOKEN_LIMIT
    
    # 模型不可用 → 切换供应商
    if error_code == "model_not_found":
        return FailoverReason.MODEL_UNAVAILABLE
    
    # 其他错误 → 不重试
    return FailoverReason.OTHER

def should_retry_with_lower_tokens(reason: FailoverReason) -> bool:
    """根据错误原因决定是否降低输出 token 限制并重试"""
    return reason in (
        FailoverReason.CONTEXT_LENGTH,
        FailoverReason.TOKEN_LIMIT
    )

def should_switch_model(reason: FailoverReason) -> bool:
    """根据错误原因决定是否切换模型"""
    return reason in (
        FailoverReason.MODEL_UNAVAILABLE,
        FailoverReason.CONTEXT_LENGTH  # 持续超出则考虑换模型
    )
```

## 实践任务

### 任务 1: 构建模型元数据表
1. 收集 20+ 个常见模型（Claude、GPT、Gemini、Llama 等）的信息
2. 创建一个对比表：

```
| 模型 | Provider | Context | Cost/1M (in) | Vision? | Tools? |
|------|----------|---------|------------|---------|--------|
| claude-3-5-sonnet | Anthropic | 200k | $3 | ✓ | ✓ |
| gpt-4-turbo | OpenAI | 128k | $10 | ✓ | ✓ |
| ...
```

**输出**：CSV 或 Markdown 表格，至少 15 个模型。

### 任务 2: 实现一个模型成本估算器
```python
def estimate_request_cost(
    model: str,
    input_messages: list,
    output_tokens_estimate: int = 500
) -> float:
    """估算一个 request 的成本"""
    
    # 估算输入 token
    input_tokens = 0
    for msg in input_messages:
        input_tokens += estimate_tokens(msg.get("content", ""))
    
    # 查询模型元数据
    metadata = MODEL_METADATA[model]
    cost_per_1m_input = metadata["cost_input_1m_tokens"]
    cost_per_1m_output = metadata["cost_output_1m_tokens"]
    
    # 计算成本
    input_cost = (input_tokens / 1_000_000) * cost_per_1m_input
    output_cost = (output_tokens_estimate / 1_000_000) * cost_per_1m_output
    
    return input_cost + output_cost

# 测试
messages = [{"role": "user", "content": "Hello, how are you?"}]
cost = estimate_request_cost("gpt-4-turbo", messages)
print(f"Estimated cost: ${cost:.6f}")
```

**验收**：成本估算在合理范围内（通常 $0.001-$0.01）。

### 任务 3: 模型降级与重试的模拟
```python
class ModelDowngradeSimulator:
    """模拟模型降级场景"""
    
    def __init__(self):
        self.downgrade_chain = {
            "gpt-4-turbo": "gpt-3.5-turbo",
            "claude-3-5-sonnet": "claude-3-haiku",
        }
    
    def test_context_overflow_handling(self):
        """测试 context 溢出时的处理"""
        
        # 场景：消息太多，超出模型 context 限制
        model = "gpt-4-turbo"
        context_limit = MODEL_METADATA[model]["context_length"]
        
        # 构造一个巨大的消息（模拟）
        huge_message = {"role": "user", "content": "x" * (context_limit + 10000)}
        messages = [huge_message]
        
        estimated_tokens = estimate_request_tokens(messages, [])
        
        # 判断是否超出
        if estimated_tokens > context_limit:
            # 选项 1：压缩
            print("Option 1: Compress context")
            
            # 选项 2：降级
            new_model = self.downgrade_chain[model]
            print(f"Option 2: Downgrade to {new_model}")
```

### 任务 4: 构建模型选择的决策树
基于以下因素，为每种场景推荐最适合的模型：

```python
def recommend_model(
    task_type: str,                # "text" / "vision" / "code"
    expected_context_size: int,    # token 数
    budget_constraint: str = "low"  # "low" / "medium" / "high"
) -> str:
    """推荐模型"""
    
    recommendations = {
        ("text", "low"): "claude-3-haiku",
        ("text", "medium"): "claude-3-5-sonnet",
        ("text", "high"): "gpt-4-turbo",
        
        ("vision", "low"): "claude-3-haiku",
        ("vision", "medium"): "claude-3-5-sonnet",
        ("vision", "high"): "gpt-4-turbo",
        
        ("code", "low"): "gpt-3.5-turbo",
        ("code", "medium"): "gpt-4",
        ("code", "high"): "gpt-4-turbo",
    }
    
    key = (task_type, budget_constraint)
    return recommendations.get(key, "claude-3-5-sonnet")
```

**要求**：
- 为 9 种组合提供推荐
- 能解释每个推荐的原因（成本 vs 质量权衡）

## 风险点与注意事项

⚠️ **成本估算的准确性** - 实际成本可能因为缓存、流量等差异。
⚠️ **模型可用性变化** - 供应商停用模型，需要更新元数据。
⚠️ **Context 限制的边界** - 不同模型的 token 计算方式略有不同。
⚠️ **降级链的设计** - 降级太急进会损伤质量，太保守会浪费成本。

## 交付物

创建 `notes/day13-model-routing.md`：
- 20+ 个模型的对比表
- Context 溢出的处理决策树
- 成本估算的算法与示例
- 任务 1-4 的代码与验证
- 模型选择的最佳实践指南

## 验收标准

你能够：
1. ✅ 列出 20+ 个模型的关键元数据
2. ✅ 估算一个 request 的成本
3. ✅ 设计模型降级链
4. ✅ 在不同场景下推荐合适的模型
5. ✅ 实现自动错误分类与重试

**最后检查**：能否根据成本与质量权衡自动选择模型？

