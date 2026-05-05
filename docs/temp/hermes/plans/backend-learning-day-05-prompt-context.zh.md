# Day 05 - Prompt 构建与 Context 压缩

## 目标
理解 prompt 组件的组装顺序、Context 压缩的时机与约束（特别是与 prompt cache 的交互）。这涉及模型效率与成本优化。

## 关键文件
- `agent/prompt_builder.py`
- `agent/context_compressor.py`
- `agent/prompt_caching.py`
- `run_agent.py`（集成点）

## 学习内容

### 1) System Prompt 的组成部分
```python
def build_system_prompt(self, platform: str, tools_list: list):
    """组装系统 prompt，不同平台有差异"""
    
    components = []
    
    # 1. Agent 身份（固定）
    components.append(DEFAULT_AGENT_IDENTITY)
    # "You are Hermes, a capable AI agent..."
    
    # 2. 平台特定提示（固定）
    if platform == "cli":
        components.append(PLATFORM_HINTS["cli"])
    elif platform == "telegram":
        components.append(PLATFORM_HINTS["telegram"])
    # ...
    
    # 3. 工具使用指导（固定）
    components.append(TOOL_USE_ENFORCEMENT_GUIDANCE)
    # "You have access to the following tools..."
    
    # 4. 内存指导（可选）
    if self.memory_enabled:
        components.append(MEMORY_GUIDANCE)
    
    # 5. 会话搜索指导（可选）
    if self.session_search_enabled:
        components.append(SESSION_SEARCH_GUIDANCE)
    
    # 6. 技能指导（可选）
    if self.skills_enabled:
        components.append(build_skills_system_prompt())
    
    # 7. 上下文文件指导（如果提供了）
    if context_files:
        components.append(build_context_files_prompt(context_files))
    
    return "\n\n".join(components)
```

**关键特性**：
- 大部分组件是固定的（一旦设定不变）
- 少数组件动态但在会话开始时就确定
- 整个 system_prompt 在 `run_conversation()` 开始时构建，之后不改

### 2) Prompt Cache 的约束
```python
# Anthropic 的 prompt caching 要求：
# - 前两个消息块必须相同
# - 工具列表必须相同
# - 如果改变 system_prompt 或 tools，cache 失效

# 在 run_agent.py 中的体现：
if self.use_anthropic_cache:
    # 第 1-2 次迭代：建立 cache
    # apply_anthropic_cache_control() 标记前两块为可缓存
    # 第 3+ 次迭代：复用 cache（只要 system/tools 不变）
    
    # 如果需要压缩，执行特殊路径：
    if needs_compression:
        # 这会改变 messages，导致 cache 失效
        # 但这是唯一允许的异常
        messages = compress_context(messages)
        # 从此时起，cache 重新开始
```

**重点**：一旦启动 cache，就被锁定。Context compression 是"有意的 cache 破坏"。

### 3) Context 压缩的流程
```python
class ContextCompressor:
    def compress(self, messages: list, target_tokens: int):
        """
        压缩消息历史，保留最新 N 条完整消息，
        压缩早期的消息为一个摘要
        """
        # 1. 分离不能删的消息（最新的 N 条）
        recent = messages[-10:]  # 保留最后 10 条
        
        # 2. 要压缩的部分
        to_compress = messages[:-10]
        
        # 3. 调用辅助 LLM 生成摘要
        summary_llm = AuxiliaryClient()  # 用便宜的模型
        summary = summary_llm.summarize(to_compress)
        
        # 4. 构建新的消息栈
        compressed = [
            {"role": "user", "content": f"[Earlier context summary]\n{summary}"},
            *recent
        ]
        
        return compressed
```

**成本权衡**：
- 不压缩：token 成本高（完整历史）
- 压缩：额外花钱调用摘要 LLM，但整体成本可能更低

### 4) 记忆与技能的集成
```python
# 在 system prompt 中插入：

# 1. 用户的长期记忆
memory_block = build_memory_context_block()
# "Based on previous conversations, the user prefers..."

# 2. 检索相关旧会话
if session_search_enabled:
    similar_sessions = search_similar_sessions(query)
    session_context = SESSION_SEARCH_GUIDANCE.format(
        similar_sessions=similar_sessions
    )

# 3. 用户的自定义技能
skills_context = build_skills_system_prompt()
# 会扫描 ~/.hermes/skills/ 并注入为 user 消息
```

## 实践任务

### 任务 1: System Prompt 的组件拆解
1. 打开 `agent/prompt_builder.py`
2. 找到各个常量（`DEFAULT_AGENT_IDENTITY`, `TOOL_USE_ENFORCEMENT_GUIDANCE` 等）
3. 列出所有可能的组件及其大小（token 数）
4. 分析：如果修改身份，是否影响 cache？如果修改工具指导呢？

**输出**：表格
```
| 组件 | 大小(token) | 固定? | Cache 影响? |
|-----|---------|-------|----------|
| Agent identity | 150 | Yes | Yes |
| Platform hints | 50-100 | Yes | Yes |
| Tool guidance | 200 | Yes | Yes (除非工具列表改) |
| Memory block | 可变 | No | Yes |
| ...
```

### 任务 2: 实现一个简单的压缩器
```python
class SimpleContextCompressor:
    """简化版压缩器，用于演示"""
    
    def compress(self, messages: list, keep_last_n: int = 5):
        """保留最后 N 条消息，早期消息合并为一条"""
        if len(messages) <= keep_last_n:
            return messages  # 不需要压缩
        
        # 早期消息的摘要
        early_msgs = messages[:-keep_last_n]
        summary = self._make_summary(early_msgs)
        
        # 新的消息列表
        compressed = [
            {
                "role": "system",
                "content": f"[Compressed context from {len(early_msgs)} earlier messages]\n{summary}"
            },
            *messages[-keep_last_n:]
        ]
        return compressed
    
    def _make_summary(self, messages: list) -> str:
        """生成摘要（这里只是示例）"""
        topics = []
        for msg in messages:
            if "topic" in msg.get("content", "").lower():
                topics.append(msg["content"][:100])
        return f"Discussed topics: {'; '.join(topics[:3])}"
```

**测试**：
```python
compressor = SimpleContextCompressor()
messages = [
    {"role": "user", "content": f"Msg {i}"} for i in range(20)
]
compressed = compressor.compress(messages, keep_last_n=5)
assert len(compressed) == 6  # 1 摘要 + 5 保留
```

### 任务 3: Cache 与 Compression 的交互分析
在 `run_agent.py` 中找到这个逻辑：
```python
if use_anthropic_cache and needs_compression:
    # 这是关键决策点
    ...
```

分析：
1. 何时触发压缩？（token 阈值？迭代次数？）
2. 压缩后的 cache 如何重新计算？
3. 能否在一个会话中压缩多次？

**输出**：伪代码流程图
```
while iteration < max_iterations:
    if use_cache and iteration >= 3:
        cache_active = True
    
    if tokens_used > 0.8 * context_limit:
        需要压缩吗？
        → 如果 cache 活跃，压缩会破坏它 ✗
        → 需要特殊处理 ✓
    
    调用模型
```

### 任务 4: 改进 System Prompt 的一个方面
选择以下之一：
1. **新增平台** - 为一个新平台添加 PLATFORM_HINTS
2. **新增指导** - 为特定场景添加新的 GUIDANCE（如"严格遵守输出格式"）
3. **优化记忆** - 改进 build_memory_context_block() 的内容质量

**要求**：
- 代码改动 < 50 行
- 配套测试验证改动有效
- 文档说明为什么这样改进

## 风险点与注意事项

⚠️ **修改 system_prompt 就是修改 cache** - 即使只改一个词，也会造成大量重新计算。
⚠️ **记忆与技能的大小** - 如果把整个用户历史记忆塞进去，会快速消耗 context。
⚠️ **Compression 的质量** - 差的摘要会导致模型表现下降（换钱不换好）。
⚠️ **平台特定指导** - Telegram 与桌面 CLI 的约束不同，system prompt 要区分。

## 交付物

创建 `notes/day05-prompt-context.md`：
- System prompt 的完整组件列表（含大小）
- Cache 与 compression 的关系图
- 任务 2 的工作代码
- 任务 3 的流程分析（伪代码）
- 任务 4 的改进方案（含测试）

## 验收标准

你能够：
1. ✅ 列出 system prompt 的所有 6+ 个组件
2. ✅ 解释为什么改变工具列表会破坏 cache
3. ✅ 实现一个工作的压缩器
4. ✅ 说出压缩的触发条件与成本
5. ✅ 为一个场景改进 system prompt 并验证

**最后检查**：能否在不破坏 cache 的前提下，改进 prompt 质量？

