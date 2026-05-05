# Day 10 - 记忆、技能与轨迹系统

## 目标
理解长期学习机制（记忆、技能、轨迹数据），以及它们如何集成到 Agent 循环中，为后续的数据分析与训练提供基础。

## 关键文件
- `agent/memory_manager.py`
- `agent/memory_provider.py`
- `agent/skill_commands.py`
- `agent/trajectory.py`
- `trajectory_compressor.py`

## 学习内容

### 1) 记忆系统的架构
```python
# agent/memory_manager.py

class MemoryManager:
    """管理用户长期记忆"""
    
    def __init__(self, user_id: str, hermes_home: Path):
        self.user_id = user_id
        self.memory_path = hermes_home / "memory" / f"{user_id}.json"
    
    def build_context_block(self) -> str:
        """构建记忆上下文，注入 system prompt"""
        if not self.memory_path.exists():
            return ""
        
        memory_data = json.loads(self.memory_path.read_text())
        
        # 记忆条目：key-value 格式
        # {
        #   "preferences": "User prefers Python over JavaScript",
        #   "projects": "Currently working on ML models",
        #   "communication_style": "Direct, technical discussions"
        # }
        
        entries = []
        for key, value in memory_data.items():
            entries.append(f"- {key}: {value}")
        
        return f"User Memory:\n" + "\n".join(entries)
    
    def update_memory(self, key: str, value: str):
        """更新或新增一条记忆"""
        if not self.memory_path.exists():
            data = {}
        else:
            data = json.loads(self.memory_path.read_text())
        
        data[key] = value
        self.memory_path.write_text(json.dumps(data, indent=2))
```

**关键特性**：
- 按用户隔离
- 注入到 system prompt 中
- 由模型主动学习和更新

### 2) 技能系统的自定义能力
```python
# agent/skill_commands.py

def discover_skills(hermes_home: Path) -> list:
    """发现用户的自定义技能"""
    skills_dir = hermes_home / "skills"
    if not skills_dir.exists():
        return []
    
    skills = []
    for skill_file in skills_dir.glob("*.py"):
        # 每个文件是一个技能
        # 例如 ~/.hermes/skills/write_blog.py
        skill_name = skill_file.stem
        skill_content = skill_file.read_text()
        
        skills.append({
            "name": skill_name,
            "description": extract_docstring(skill_content),
            "code": skill_content
        })
    
    return skills

def build_skills_system_prompt(skills: list) -> str:
    """将技能注入 system prompt"""
    if not skills:
        return ""
    
    prompt_parts = [
        "You have access to the following user-defined skills:\n"
    ]
    
    for skill in skills:
        prompt_parts.append(f"### Skill: {skill['name']}")
        prompt_parts.append(skill['description'])
        prompt_parts.append(f"Code:\n{skill['code']}\n")
    
    return "\n".join(prompt_parts)
```

**示例技能文件**（~/.hermes/skills/write_blog.py）：
```python
"""
Write a blog post about a topic.

This skill helps generate structured blog posts with intro, main points, and conclusion.
"""

def write_blog(topic: str, wordcount: int = 1000) -> str:
    outline = f"""
    Blog Post: {topic}
    
    1. Introduction
    2. Main Points
    3. Examples
    4. Conclusion
    """
    return outline
```

### 3) 轨迹数据的采集与压缩
```python
# agent/trajectory.py

class Trajectory:
    """单次会话的完整轨迹"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages = []          # 完整消息历史
        self.tool_calls = []        # 工具调用记录
        self.decisions = []         # 关键决策点
        self.reasoning = []         # 思维过程
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "messages": self.messages,
            "tool_calls": self.tool_calls,
            "decisions": self.decisions,
            "reasoning": self.reasoning
        }

def save_trajectory(session_id: str, trajectory: Trajectory, hermes_home: Path):
    """保存轨迹数据"""
    trajectory_dir = hermes_home / "trajectories"
    trajectory_dir.mkdir(exist_ok=True)
    
    trajectory_file = trajectory_dir / f"{session_id}.jsonl"
    
    with open(trajectory_file, "w") as f:
        f.write(json.dumps(trajectory.to_dict()))
    
    logger.info(f"Trajectory saved: {trajectory_file}")

# trajectory_compressor.py - 用于离线分析
def compress_trajectories(source_dir: Path) -> dict:
    """压缩多个轨迹为统计数据"""
    stats = {
        "total_sessions": 0,
        "avg_turns": 0,
        "tools_distribution": {},
        "reasoning_length": []
    }
    
    trajectories = list(source_dir.glob("*.jsonl"))
    for traj_file in trajectories:
        traj = json.loads(traj_file.read_text())
        stats["total_sessions"] += 1
        stats["avg_turns"] += len(traj["messages"])
        
        for tool_call in traj["tool_calls"]:
            tool_name = tool_call.get("name")
            stats["tools_distribution"][tool_name] = \
                stats["tools_distribution"].get(tool_name, 0) + 1
    
    return stats
```

### 4) 三者的集成
```python
# run_agent.py 中的集成点

def run_conversation(self, user_message, ...):
    # 第 1 步：构建 system prompt（包含记忆与技能）
    memory_block = build_memory_context_block(self.user_id)
    skills_prompt = build_skills_system_prompt()
    system_prompt = build_system_prompt() + "\n" + memory_block + "\n" + skills_prompt
    
    # 第 2 步：正常的 Agent 循环
    messages = [{"role": "system", "content": system_prompt}]
    ...
    
    # 第 3 步：循环中记录工具调用
    trajectory = Trajectory(self.session_id)
    for tool_call in response.tool_calls:
        trajectory.tool_calls.append({
            "name": tool_call.name,
            "args": tool_call.arguments,
            "timestamp": time.time()
        })
    
    # 第 4 步：会话结束后保存轨迹
    trajectory.messages = messages
    save_trajectory(self.session_id, trajectory, self.hermes_home)
```

## 实践任务

### 任务 1: 理解记忆的 3 种形式
1. **会话记忆**：单个 session 内的消息（由 SessionDB 管理）
2. **长期记忆**：跨会话的用户偏好（由 MemoryManager 管理）
3. **轨迹数据**：每个会话的完整操作记录（用于分析与训练）

为每种形式写出：
- 存储位置
- 生命周期
- 访问方式
- 隐私考虑

**输出**：比对表

### 任务 2: 创建一个自定义技能
创建 `~/.hermes/skills/summarize_text.py`：
```python
"""
Summarize long text into key points.

This skill extracts the main ideas and condenses content.
"""

def summarize_text(text: str, num_points: int = 5) -> str:
    """
    Extract key points from text.
    
    Args:
        text: The text to summarize
        num_points: Number of key points to extract
    
    Returns:
        Bullet list of key points
    """
    # 这是一个占位符实现
    # 实际会被 Agent 调用来执行
    return f"Summarizing {len(text)} chars into {num_points} points..."
```

验证：
```bash
hermes skill list
# 应该看到 summarize_text 在列表中
```

**验收**：技能被正确发现并可用。

### 任务 3: 轨迹数据的采集与分析
1. 运行一个简单的 Agent 对话（3-5 轮）
2. 查看 `~/.hermes/trajectories/` 是否有新文件生成
3. 用 `trajectory_compressor.py` 分析轨迹数据

```python
from trajectory_compressor import compress_trajectories
from pathlib import Path

trajectories_dir = Path.home() / ".hermes" / "trajectories"
stats = compress_trajectories(trajectories_dir)

print(f"Total sessions: {stats['total_sessions']}")
print(f"Tools used: {stats['tools_distribution']}")
```

**验收**：能成功读取和分析轨迹数据。

### 任务 4: 改进记忆的自动更新
现有的记忆管理是手动的（由模型决定是否更新）。
设计一个自动记忆更新的规则，例如：
- 如果用户多次提到相同的偏好，自动学习
- 如果用户纠正模型的理解，自动更新记忆
- 如果涉及新的项目或工作，自动记录

**要求**：
- 提出 3 条自动学习规则
- 每条规则的伪代码实现
- 考虑误学习的风险

## 风险点与注意事项

⚠️ **记忆的隐私性** - 用户的偏好和历史应该本地加密存储。
⚠️ **技能的安全性** - 用户自定义技能代码应该沙盒执行，不能直接访问系统。
⚠️ **轨迹数据的大小** - 长期运行会积累大量轨迹，需要定期清理或压缩。
⚠️ **记忆冲突** - 如果新旧记忆矛盾（如模型被纠正），需要解决冲突。

## 交付物

创建 `notes/day10-learning-systems.md`：
- 记忆、技能、轨迹的架构对比
- 三者如何集成到 Agent 循环
- 任务 1-4 的实现与验证
- 自动学习规则的伪代码

## 验收标准

你能够：
1. ✅ 区分会话记忆、长期记忆、轨迹数据
2. ✅ 创建并使用一个自定义技能
3. ✅ 采集和分析轨迹数据
4. ✅ 提议改进记忆自动更新的方案
5. ✅ 理解隐私与安全考虑

**最后检查**：能否基于轨迹数据生成有用的统计报告？

