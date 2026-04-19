# 第5天：记忆系统和技能系统

**学习日期**：Day 5  
**预计投入**：5小时  
**难度等级**：⭐⭐⭐ (中等)

---

## 📚 学习目标

理解持久化记忆提取和技能加载机制。

**关键成果**：
- ✅ 理解异步内存提取机制
- ✅ 理解内存数据库设计
- ✅ 理解技能发现和加载
- ✅ 理解SKILL.md格式
- ✅ 理解嵌套技能容器

---

## 📋 任务清单

### 任务5.1：内存提取系统（1.5小时）

**内存系统架构**：
```
会话完成
    ↓
MemoryMiddleware入队对话
    ↓
异步消费者线程
├─ extraction.py: 分析对话
├─ queue.py: 处理队列
└─ prompts.py: LLM提示词
    ↓
提取: {背景, 事实, 偏好, 置信度}
    ↓
持久化到memory.db
    ↓
后续对话检索相关记忆
    ↓
注入系统提示词
```

**extraction.py - 内存提取**

```
功能：
- 分析对话文本
- 识别用户信息
- 提取可重用事实
- 评分置信度
```

**LLM提示词例**：
```
你是记忆助手。分析这段对话，提取：

1. 用户背景 (work_context)
2. 个人偏好 (personal_context)
3. 关键事实 (facts: list[{text, confidence}])

对话:
[对话文本]

返回JSON:
{
    "work_context": "用户是数据分析师...",
    "personal_context": "用户喜欢Python...",
    "facts": [
        {"text": "用户使用Pandas", "confidence": 0.95},
        {"text": "用户偏好可视化", "confidence": 0.8}
    ]
}
```

**queue.py - 异步处理**

```python
class MemoryQueue:
    def __init__(self):
        self.queue: queue.Queue = queue.Queue()
        self.consumer_thread = Thread(
            target=self._consume,
            daemon=True
        )
        self.consumer_thread.start()
    
    def add(self, thread_id: str, messages: list):
        self.queue.put((thread_id, messages))
    
    def _consume(self):
        while True:
            thread_id, messages = self.queue.get()
            facts = extract_memory(messages)
            save_to_db(facts)
```

**为什么异步**：
```
原因1：提取耗时（LLM调用）
原因2：_________________________________
原因3：_________________________________
```

**数据库schema**：
```sql
CREATE TABLE facts (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    fact TEXT,
    confidence FLOAT,  -- [0.0, 1.0]
    source_thread_id TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    category TEXT -- 'background', 'preference', 'fact'
);

CREATE TABLE user_context (
    user_id TEXT PRIMARY KEY,
    work_context TEXT,
    personal_context TEXT,
    top_of_mind TEXT,
    updated_at DATETIME
);
```

**检索和注入**：
```python
def get_memory_context(user_id: str) -> str:
    # 获取相关事实
    facts = db.query("""
        SELECT fact, confidence FROM facts
        WHERE user_id = ? AND confidence > 0.7
        ORDER BY updated_at DESC
        LIMIT 10
    """, user_id)
    
    # 获取用户背景
    context = db.query("""
        SELECT work_context, personal_context
        FROM user_context
        WHERE user_id = ?
    """, user_id)
    
    # 构建提示词
    prompt = f"""
关于用户的信息：
工作背景: {context.work_context}
个人偏好: {context.personal_context}

关键事实:
{' '.join([f"• {f.fact} (置信度:{f.confidence})" for f in facts])}

请在回复中参考这些信息。
"""
    return prompt
```

**置信度和衰减**：
```python
# 同一事实重复出现→置信度上升
if existing_fact:
    existing_fact.confidence = min(
        existing_fact.confidence + 0.1,
        1.0
    )

# 时间衰减→旧事实权重下降
confidence = base_confidence * (0.95 ** days_ago)
```

**检验方式**：
- [ ] 为什么内存提取必须异步？
- [ ] 如何处理内存中的重复事实？
- [ ] 置信度如何随时间衰减？
- [ ] 如何避免内存提取的"幻觉"？

---

### 任务5.2：技能系统（1.5小时）

**技能发现机制**：
```python
def discover_skills(skills_dir: str) -> dict:
    skills = {}
    
    for root, dirs, files in os.walk(skills_dir):
        if 'SKILL.md' in files:
            skill_name = os.path.basename(root)
            skill_path = os.path.relpath(root, skills_dir)
            
            skills[skill_name] = {
                'name': skill_name,
                'path': f'/mnt/skills/{skill_path}',
                'description': parse_description(),
                'usage': parse_usage(),
            }
    
    return skills
```

**SKILL.md格式**：
```markdown
# 数据分析技能

## 功能概述
此技能提供...

## 使用示例
```python
from utils import analyze_csv
result = analyze_csv('/mnt/user-data/uploads/data.csv')
```

## 文件清单
- utils.py
- requirements.txt

## 限制
- 仅支持CSV格式
- 最大文件1GB
```

**三个部分**：
```
1. 功能概述：做什么
2. 使用示例：如何用
3. 文件清单：包含什么
```

**技能提示词注入**：
```
可用的技能：

1. 数据分析 (/mnt/skills/data_analysis)
   功能: CSV分析、统计、绘图
   使用: from utils import analyze_csv

2. Web研究 (/mnt/skills/web_research)
   功能: 网页爬取、信息提取
   使用: from utils import web_search

使用步骤：
1. cd /mnt/skills/技能名
2. 查看README和示例
3. 导入并调用函数
```

**技能加载到沙箱**：
```python
# /mnt/skills 是只读共享的
# Agent通过相对导入加载技能

# 例：在沙箱中执行
bash("""
cd /mnt/skills/data_analysis
python analyze.py /mnt/user-data/uploads/data.csv
""")
```

**嵌套技能容器**：
```
skills/public/
├── simple_skill/
│   └── SKILL.md
│
└── complex_analysis/
    ├── SKILL.md
    ├── python/
    │   ├── SKILL.md           # 嵌套
    │   └── main.py
    └── shell/
        ├── SKILL.md           # 嵌套
        └── run.sh
```

**虚拟路径**：
```
/mnt/skills/simple_skill
/mnt/skills/complex_analysis
/mnt/skills/complex_analysis/python
/mnt/skills/complex_analysis/shell
```

**为什么支持嵌套**：
```
原因1：组织复杂技能集合
原因2：_________________________________
原因3：_________________________________
```

**技能管理工具**：
```python
@tool(name="skill_manage")
def skill_manage(
    action: str,  # list, search, install, update
    name: str = None
) -> str:
    """管理技能"""
    if action == 'list':
        return json.dumps(discover_skills())
    elif action == 'search':
        return search_skills_in_market(name)
    elif action == 'install':
        return install_skill_from_market(name)
```

**代码练习**：创建一个自定义技能
```bash
# 1. 创建目录
mkdir -p skills/public/my_analyzer

# 2. 编写SKILL.md
cat > skills/public/my_analyzer/SKILL.md << 'EOF'
# 自定义分析器

## 功能
分析JSON数据并生成报告

## 使用
```python
from analyzer import run_analysis
result = run_analysis('/mnt/user-data/uploads/data.json')
```
EOF

# 3. 编写analyzer.py
cat > skills/public/my_analyzer/analyzer.py << 'EOF'
def run_analysis(path):
    import json
    with open(path) as f:
        data = json.load(f)
    return {"count": len(data)}
EOF

# 4. 测试发现
# 运行Agent，看是否发现到这个技能
```

**检验方式**：
- [ ] SKILL.md格式的三个关键部分是什么？
- [ ] 为什么技能路径用虚拟路径？
- [ ] 嵌套技能如何组织和访问？
- [ ] 如何从Agent中调用一个技能？

---

## ✅ 第5天检验清单

**理论题**：
- [ ] 内存提取为什么必须异步？
- [ ] 置信度如何在重复事实时更新？
- [ ] 技能发现算法是什么？
- [ ] SKILL.md的三个必要部分？
- [ ] 如何让Agent知道一个新增的技能？

**实践题**：
- [ ] 理解了内存数据库schema ✓ / ✗
- [ ] 能解释置信度衰减机制 ✓ / ✗
- [ ] 创建了自定义技能 ✓ / ✗
- [ ] 能设计嵌套技能结构 ✓ / ✗

---

## 🎓 Day 5总结

**核心收获**：
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

**异步处理的重要性**：
_____________________________________________

**技能系统的灵活性**：
_____________________________________________

---

**Day 5 完成时间**：_____________  
**理解程度评分** (1-10)：_____

---

**文档版本**：1.0  
**最后更新**：2025-04-19

