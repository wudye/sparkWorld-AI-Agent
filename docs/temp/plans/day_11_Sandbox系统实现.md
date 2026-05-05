# 第11天：Sandbox系统实现

**学习日期**：Day 11  
**预计投入**：8小时  
**难度等级**：⭐⭐⭐⭐ (较难)

---

## 🎯 今日目标

实现Sandbox的本地提供商和工具集。

---

## 📋 任务清单

### 任务11.1：Sandbox抽象接口（1小时）

```python
# deerflow/sandbox/sandbox.py

from abc import ABC, abstractmethod

class Sandbox(ABC):
    """沙箱抽象基类"""
    
    def __init__(self, id: str):
        self._id = id
    
    @property
    def id(self) -> str:
        return self._id
    
    @abstractmethod
    def execute_command(self, command: str) -> str:
        pass
    
    @abstractmethod
    def read_file(self, path: str) -> str:
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: str, append: bool = False) -> None:
        pass
    
    @abstractmethod
    def list_dir(self, path: str, max_depth: int = 2) -> list[str]:
        pass
```

### 任务11.2：LocalSandbox实现（3小时）

```python
# deerflow/sandbox/local/local_sandbox.py

import os
from pathlib import Path
from deerflow.sandbox.sandbox import Sandbox

class LocalSandbox(Sandbox):
    """本地文件系统沙箱"""
    
    def __init__(self, sandbox_id: str, base_path: str):
        super().__init__(sandbox_id)
        self.base_path = base_path
        self.thread_path = os.path.join(base_path, sandbox_id)
    
    def resolve_path(self, virtual_path: str) -> str:
        """虚拟路径→物理路径转换"""
        
        if virtual_path.startswith('/mnt/user-data'):
            relative = virtual_path[len('/mnt/user-data'):]
            physical = os.path.join(self.thread_path, relative)
        elif virtual_path.startswith('/mnt/skills'):
            relative = virtual_path[len('/mnt/skills'):]
            physical = os.path.join('/opt/deerflow/skills', relative)
        else:
            raise ValueError(f"Invalid path: {virtual_path}")
        
        # 安全检查：防止目录穿越
        physical = os.path.abspath(physical)
        if not physical.startswith(self.thread_path) and \
           not physical.startswith('/opt/deerflow/skills'):
            raise ValueError(f"Path traversal detected: {virtual_path}")
        
        return physical
    
    def read_file(self, path: str) -> str:
        """读取文件"""
        physical_path = self.resolve_path(path)
        with open(physical_path, 'r') as f:
            return f.read()
    
    def write_file(self, path: str, content: str, append: bool = False) -> None:
        """写入文件"""
        physical_path = self.resolve_path(path)
        
        # 创建父目录
        os.makedirs(os.path.dirname(physical_path), exist_ok=True)
        
        mode = 'a' if append else 'w'
        with open(physical_path, mode) as f:
            f.write(content)
    
    def list_dir(self, path: str, max_depth: int = 2) -> list[str]:
        """列表目录"""
        physical_path = self.resolve_path(path)
        result = []
        
        for root, dirs, files in os.walk(physical_path):
            depth = len(root) - len(physical_path)
            if depth >= max_depth:
                continue
            
            for f in files:
                result.append(os.path.join(root, f))
        
        return result
    
    def execute_command(self, command: str) -> str:
        """本地沙箱不支持直接bash"""
        raise NotImplementedError("Use AioSandbox for shell execution")
```

### 任务11.3：Sandbox工具（2小时）

```python
# deerflow/sandbox/tools.py

from langchain.tools import tool

def create_sandbox_tools(sandbox):
    """创建沙箱工具集"""
    
    @tool(name="read_file")
    def read_file(path: str) -> str:
        """读取文件内容"""
        return sandbox.read_file(path)
    
    @tool(name="write_file")
    def write_file(path: str, content: str) -> str:
        """写入文件"""
        sandbox.write_file(path, content)
        return f"Written to {path}"
    
    @tool(name="list_dir")
    def list_dir(path: str, max_depth: int = 2) -> str:
        """列表目录"""
        files = sandbox.list_dir(path, max_depth)
        return "\n".join(files)
    
    @tool(name="str_replace")
    def str_replace(path: str, old_str: str, new_str: str) -> str:
        """替换文件内容"""
        content = sandbox.read_file(path)
        if old_str not in content:
            return f"Error: old_str not found in {path}"
        
        new_content = content.replace(old_str, new_str)
        sandbox.write_file(path, new_content)
        
        return f"Replaced in {path}"
    
    return [read_file, write_file, list_dir, str_replace]
```

### 任务11.4：测试（1小时）

```python
# tests/test_sandbox.py

import pytest
import tempfile
from deerflow.sandbox.local.local_sandbox import LocalSandbox

@pytest.fixture
def sandbox():
    with tempfile.TemporaryDirectory() as tmpdir:
        return LocalSandbox('test_123', tmpdir)

def test_write_and_read(sandbox):
    sandbox.write_file('/mnt/user-data/test.txt', 'hello')
    content = sandbox.read_file('/mnt/user-data/test.txt')
    assert content == 'hello'

def test_str_replace(sandbox):
    sandbox.write_file(
        '/mnt/user-data/file.txt',
        'old content'
    )
    # 这里需要实现str_replace
    # sandbox.str_replace(...)

def test_path_security(sandbox):
    with pytest.raises(ValueError):
        sandbox.resolve_path('/etc/passwd')
```

---

## ✅ Day 11检验清单

**Sandbox实现**：
- [ ] 抽象接口定义 ✓ / ✗
- [ ] LocalSandbox实现 ✓ / ✗
- [ ] 虚拟路径映射 ✓ / ✗
- [ ] 安全检查 ✓ / ✗
- [ ] 工具集实现 ✓ / ✗

**测试**：
- [ ] 所有单元测试通过 ✓ / ✗
- [ ] 安全测试通过 ✓ / ✗
- [ ] 路径映射正确 ✓ / ✗

---

## 🎓 Day 11总结

**完成内容**：
- ✅ Sandbox抽象设计
- ✅ LocalSandbox完整实现
- ✅ 虚拟路径隔离
- ✅ 基础工具集

**下一步** (Day 12)：
- 工具和子Agent系统

---

**Day 11 完成时间**：_____________  
**测试覆盖率**：___ %

---

**文档版本**：1.0  
**最后更新**：2025-04-19

