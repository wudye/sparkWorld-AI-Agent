# 第3天：Sandbox隔离执行系统

**学习日期**：Day 3  
**预计投入**：5.5小时  
**难度等级**：⭐⭐⭐⭐ (较难)

---

## 📚 学习目标

完全理解Sandbox的设计、实现和安全机制。

**关键成果**：
- ✅ 理解Sandbox抽象设计
- ✅ 完全掌握LocalSandbox实现
- ✅ 理解5个沙箱工具的用途
- ✅ 理解虚拟路径隔离机制
- ✅ 理解安全策略
- ✅ 能创建Mock Sandbox进行测试

---

## 📋 任务清单

### 任务3.1：理解Sandbox抽象接口（1小时）

**阅读材料**：
```
✓ backend/packages/harness/deerflow/sandbox/sandbox.py
✓ backendclaude.md 第2.2节
✓ sandbox_detailed_analysis.md
```

**7个核心方法**：

```python
class Sandbox(ABC):
    # 1. 执行命令
    def execute_command(command: str) -> str
    
    # 2. 读文件
    def read_file(path: str) -> str
    
    # 3. 写文件
    def write_file(path: str, content: str, append: bool) -> None
    
    # 4. 列目录
    def list_dir(path: str, max_depth: int) -> list[str]
    
    # 5. 全局搜索
    def glob(path: str, pattern: str) -> tuple[list[str], bool]
    
    # 6. 搜索内容
    def grep(path: str, pattern: str) -> tuple[list[GrepMatch], bool]
    
    # 7. 更新二进制文件
    def update_file(path: str, content: bytes) -> None
```

**为什么设计成抽象基类**：
```
原因1：_________________________________________
原因2：_________________________________________
原因3：_________________________________________

未来支持的实现方式：
- LocalSandbox      → 本地文件系统
- AioSandbox        → Docker容器
- SSHSandbox (?)    → 远程SSH执行
- K8sSandbox (?)    → Kubernetes Pod
```

**代码练习**：
```python
# 理解接口
from deerflow.sandbox import Sandbox

class DummySandbox(Sandbox):
    def execute_command(self, command: str) -> str:
        return "dummy output"
    # ... 实现其他抽象方法

# 这样的设计在未来如何支持SSH沙箱？
答：_____________________________________________
```

**检验方式**：
- [ ] 为什么需要glob和grep方法？（而不是shell来做）
- [ ] Sandbox为什么不提供delete_file方法？（安全考虑）

---

### 任务3.2：理解LocalSandbox实现（1.5小时）

**阅读材料**：
```
✓ backend/packages/harness/deerflow/sandbox/local/local_sandbox.py
✓ backend/packages/harness/deerflow/sandbox/tools.py
✓ backendclaude.md 第2.2.6节
```

**核心概念**：

**1. LocalSandbox vs LocalSandboxProvider**

```python
# Provider: 工厂模式
class LocalSandboxProvider:
    def create_sandbox(self, sandbox_id: str) -> LocalSandbox:
        return LocalSandbox(sandbox_id, self.base_path)

# Sandbox: 具体实例
class LocalSandbox(Sandbox):
    def __init__(self, sandbox_id: str, base_path: str):
        self.sandbox_id = sandbox_id
        self.base_path = base_path
    
    def execute_command(self, command: str) -> str:
        # 实际实现
```

**为什么使用工厂模式**：
```
好处1：_________________________________________
好处2：_________________________________________
好处3：_________________________________________
```

**2. LocalSandbox的限制**

| 特性 | 支持 | 原因 |
|------|------|------|
| bash工具 | ❌ | 直接执行命令太危险 |
| read/write | ✅ | 文件操作相对安全 |
| 虚拟路径 | ✅ | 提供隔离保证 |
| 并发操作 | ⚠️ | 需要FileOperationLock |

**3. 虚拟路径映射**

```
虚拟路径 (Agent看到的)        物理路径 (真实存储)
/mnt/user-data/workspace/  →  /threads/thread_123/workspace/
/mnt/user-data/uploads/    →  /threads/thread_123/uploads/
/mnt/user-data/outputs/    →  /threads/thread_123/outputs/
/mnt/skills/               →  /opt/deerflow/skills/
```

**映射实现**：
```python
def resolve_path(self, virtual_path: str) -> str:
    if virtual_path.startswith('/mnt/user-data'):
        # 1. 提取相对路径
        relative = virtual_path[len('/mnt/user-data'):]
        # 2. 拼接真实路径
        physical = os.path.join(self.base_path, self.sandbox_id, relative)
        # 3. 安全检查
        # ... 防止目录穿越
        return physical
    elif virtual_path.startswith('/mnt/skills'):
        # ...
```

**为什么需要虚拟路径**：
```
安全原因：_________________________________________
隔离原因：_________________________________________
灵活性原因：_______________________________________
```

**4. 文件操作的原子性**

```python
class FileOperationLock:
    _locks: dict[tuple[str, str], RLock]  # (sandbox_id, path)
    
    # 保证str_replace的read-modify-write原子
    with self.acquire_lock(sandbox_id, path):
        content = read()
        content = content.replace(old, new)
        write(content)
```

**为什么需要锁**：
```
问题场景：
- 多个工具同时操作同一文件
- Thread A: read → 获得内容
- Thread B: read → 获得内容
- Thread A: write → 修改1
- Thread B: write → 修改2覆盖修改1 ❌

解决方案：
_____________________________________________
```

**代码练习**：
```python
# 创建一个LocalSandbox并测试
from deerflow.sandbox.local import LocalSandboxProvider

provider = LocalSandboxProvider(base_path='/tmp/sandboxes')
sandbox = provider.create_sandbox('test_123')

# 测试操作
sandbox.write_file('/mnt/user-data/workspace/test.txt', 'hello')
content = sandbox.read_file('/mnt/user-data/workspace/test.txt')

# 观察真实文件位置
import os
files = os.listdir('/tmp/sandboxes/test_123/workspace/')
```

**检验方式**：
- [ ] 解释虚拟路径和真实路径的映射
- [ ] str_replace为什么需要FileOperationLock？
- [ ] LocalSandbox为何禁用bash？如何在需要时启用？

---

### 任务3.3：Sandbox工具实现（1小时）

**5个Sandbox工具**：

**1️⃣ bash 工具**
```python
@tool(name="bash")
def bash(command: str) -> str:
    """执行bash命令"""
    # LocalSandbox: ❌ 禁用
    # AioSandbox: ✅ 在Docker容器中执行

# 配置：DEFAULT_BASH_ENABLED = False
```

**为什么LocalSandbox禁用bash**：
```
安全风险：
- rm -rf /         → 删除系统
- fork(); fork(); → Fork炸弹
- dd if=/dev/zero → 填充磁盘
_____________________________________________
```

**2️⃣ ls 工具**
```python
@tool(name="ls")
def ls(path: str, max_depth: int = 2) -> str:
    """列表目录内容，最多2层深度"""
    return sandbox.list_dir(path, max_depth)
```

**为什么有max_depth**：
```
原因1：_________________________________________
原因2：_________________________________________
```

**3️⃣ read_file 工具**
```python
@tool(name="read_file")
def read_file(path: str) -> str:
    """读取文件内容"""
    return sandbox.read_file(path)
```

**考虑**：
```
大文件处理？_____________________________________
截断策略？_____________________________________
```

**4️⃣ write_file 工具**
```python
@tool(name="write_file")
def write_file(path: str, content: str) -> str:
    """覆盖写文件"""
    sandbox.write_file(path, content, append=False)
```

**什么场景用这个**：
```
场景1：_________________________________________
场景2：_________________________________________
```

**5️⃣ str_replace 工具 ⭐ 最重要**
```python
@tool(name="str_replace")
def str_replace(
    path: str,
    old_str: str,
    new_str: str
) -> str:
    """替换文件中的文本
    
    1. 读取文件
    2. 查找old_str（必须精确匹配，包括缩进空格）
    3. 替换为new_str
    4. 写回
    5. 返回修改前后各20行上下文
    """
```

**为什么str_replace最好用**：
```
原因1（LLM需要上下文）：
_____________________________________________

原因2（精确匹配）：
_____________________________________________

原因3（原子操作）：
_____________________________________________
```

**使用示例**：
```python
# 修改Python文件中的一个函数
str_replace(
    path="/mnt/user-data/workspace/main.py",
    old_str="""def hello(name):
    print(f"Hi {name}")""",
    new_str="""def hello(name):
    print(f"Hello {name}!")"""
)
```

**代码练习**：
```python
# 观察str_replace如何显示上下文
# 打开test_sandbox.py，找到str_replace的测试用例

# 修改一个源代码文件
sandbox.write_file(
    '/mnt/user-data/workspace/app.py',
    '''def main():
    x = 1
    y = 2
    return x + y
'''
)

# 使用str_replace替换其中一部分
result = sandbox.str_replace(
    '/mnt/user-data/workspace/app.py',
    'y = 2',
    'y = 3'
)
# 观察返回的上下文
```

**检验方式**：
- [ ] str_replace vs write_file的区别是什么？
- [ ] 为什么str_replace的old_str必须精确匹配？
- [ ] 如何用str_replace修改一个代码文件中某个类的一个方法？

---

### 任务3.4：安全策略和权限控制（0.5小时）

**阅读材料**：
```
✓ backend/packages/harness/deerflow/sandbox/security.py
```

**1. 命令黑名单**
```python
DANGEROUS_PATTERNS = [
    r"(?i)rm\s+-rf",              # 不允许递归删除
    r"(?i):(){ *:|:|",            # Fork炸弹
    r"(?i)shutdown|reboot",       # 系统命令
]
```

**这些检查在LocalSandbox有用吗**：
```
LocalSandbox中：
_____________________________________________

AioSandbox中：
_____________________________________________
```

**2. 权限模型**
```
Sandbox操作都在隔离的虚拟路径内
├→ 无法访问/etc（系统目录）
├→ 无法访问/root（用户目录）
└→ 虚拟路径映射强制隔离
```

**检验方式**：
- [ ] 设计一个恶意Agent：如何突破隔离？
- [ ] 虚拟路径映射能否真正保证隔离？

---

### 任务3.5：实现一个简单的Mock Sandbox（1小时）

**实践目标**：创建一个内存中的Sandbox（不操作真实文件系统）

**代码框架**：
```python
from deerflow.sandbox import Sandbox

class MemorySandbox(Sandbox):
    def __init__(self, sandbox_id: str):
        self._id = sandbox_id
        self._files = {}  # {path: content}
    
    def execute_command(self, command: str) -> str:
        raise NotImplementedError("Not supported")
    
    def read_file(self, path: str) -> str:
        return self._files.get(path, "File not found")
    
    def write_file(self, path: str, content: str, append: bool = False) -> None:
        if append:
            self._files[path] = self._files.get(path, "") + content
        else:
            self._files[path] = content
    
    def list_dir(self, path: str, max_depth=2) -> list[str]:
        # 实现目录列表逻辑
        ...
    
    def glob(self, path: str, pattern: str, **kwargs):
        # 实现glob逻辑
        ...
    
    def grep(self, path: str, pattern: str, **kwargs):
        # 实现grep逻辑
        ...
    
    def update_file(self, path: str, content: bytes) -> None:
        self._files[path] = content.decode()
```

**测试**：
```python
sandbox = MemorySandbox('test')
sandbox.write_file('/test/file.txt', 'hello')
content = sandbox.read_file('/test/file.txt')
assert content == 'hello'
```

**这个Mock有什么用**：
```
用途1：_________________________________________
用途2：_________________________________________
用途3：_________________________________________
```

---

## ✅ 第3天检验清单

**理论题**：
- [ ] Sandbox的7个方法分别用来做什么？
- [ ] 虚拟路径/mnt/user-data/workspace映射到哪里？
- [ ] str_replace与write_file的差异？
- [ ] LocalSandbox为什么禁用bash？
- [ ] 如何实现一个SSH-based Sandbox？

**实践题**：
- [ ] 能创建LocalSandbox实例 ✓ / ✗
- [ ] 虚拟路径正确映射 ✓ / ✗
- [ ] str_replace正确工作 ✓ / ✗
- [ ] 并发操作安全 ✓ / ✗
- [ ] 创建了MemorySandbox ✓ / ✗

---

## 🎓 Day 3总结

**最重要的3个概念**：
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

**虚拟路径隔离的意义**：
_____________________________________________

**Sandbox设计的亮点**：
_____________________________________________

---

**Day 3 完成时间**：_____________  
**代码实践完成**：✓ / ✗  
**理解程度评分** (1-10)：_____  

---

**文档版本**：1.0  
**最后更新**：2025-04-19

