用户想要一个完整的总结，关于如何在父项目中设置子包（child packages）。让我总结一下完整的步骤。

从之前的对话中，我了解到：
1. 使用 UV workspace 功能
2. 父项目需要配置 [tool.uv.workspace] 和 [tool.uv.sources]
3. 子项目需要有自己的 pyproject.toml 和 [build-system]
4. 有一个拼写错误需要修正：hatchlin -> hatchling，member -> members

让我提供一个完整的、结构化的步骤指南。
# UV Workspace 多包项目完整配置指南

以下是父项目包含多个子包的完整设置步骤：

---

## 📁 推荐目录结构

```
backend/                          # 父项目根目录
├── pyproject.toml               # 父项目配置
├── .python-version              # Python 版本
├── uv.lock                      # 依赖锁定文件
├── app/                         # 父项目应用代码
│   └── app.py
└── packages/                    # 子包目录（统一放这里）
    ├── harness/                 # 子包1: spark-harness
    │   └── spark/
    │       ├── __init__.py
    │       └── pyproject.toml
    ├── harness2/                # 子包2: spark2-harness2
    │   └── spark2/
    │       ├── __init__.py
    │       └── pyproject.toml
    └── spark1/                  # 子包3: spark1
        ├── __init__.py
        └── pyproject.toml
```

---

## 步骤 1：创建子包

### 每个子包都需要自己的 `pyproject.toml`

```toml
# packages/harness/spark/pyproject.toml

[project]
name = "spark-harness"           # ⚠️ 这个名字很重要！父项目要用它引用
version = "0.1.0"
description = "spark ai agent harness"
requires-python = ">=3.13"
dependencies = [
    # 子包自己的依赖
]

[build-system]
requires = ["hatchling"]         # 构建工具
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["spark"]             # 代码所在的目录名
```

```toml
# packages/spark1/pyproject.toml

[project]
name = "spark1"                  # 子包2的名字
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## 步骤 2：配置父项目

```toml
# backend/pyproject.toml（根项目）

[project]
name = "backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.136.1",
    "uvicorn[standard]>=0.47.0",
    
    # 引入子包（名称必须与子包 name 完全一致）
    "spark-harness",
    "spark1",
]

[dependency-groups]
dev = [
    "pytest>=9.0.3",
]

# ========== 关键配置 1: 定义 Workspace 成员 ==========
[tool.uv.workspace]
members = [
    "packages/*",      # 匹配 packages/spark1
    "packages/*/*",    # 匹配 packages/harness/spark
]

# ========== 关键配置 2: 映射本地包源 ==========
[tool.uv.sources]
spark-harness = { workspace = true }
spark1 = { workspace = true }
```

---

## 步骤 3：同步依赖

```bash
# 在父项目根目录运行
cd backend

# 安装所有依赖（父项目 + 所有子包）
uv sync

# 子包会被自动以"可编辑模式"安装
```

---

## 步骤 4：代码中导入使用

```python
# 在父项目的 app/app.py 中

# 导入子包1
from spark import some_module

# 导入子包2  
from spark1 import another_module

# 正常使用
```

---

## 🔑 关键要点总结

| 配置项 | 位置 | 作用 |
|--------|------|------|
| `[tool.uv.workspace]` | 父项目 | 定义哪些目录是 workspace 成员 |
| `members = ["packages/*"]` | 父项目 | 通配符匹配子包路径 |
| `[tool.uv.sources]` | 父项目 | 告诉 UV 从本地找这些包 |
| `name = "xxx"` | 子项目 | 包的唯一标识，父项目用此引用 |
| `[build-system]` | 子项目 | 让包可以被构建和安装 |

---

## ⚠️ 常见错误检查清单

```
✅ 子包 pyproject.toml 必须有 [build-system]
✅ 子包 name 必须与父项目 dependencies 中引用的名称一致
✅ 父项目 [tool.uv.workspace] 用 members（复数）
✅ 父项目 [tool.uv.sources] 中每个子包都要单独列出一行
✅ hatchling 拼写正确（不是 hatchlin）
✅ 子包代码目录与 packages = ["xxx"] 配置一致
```

---

## 📋 快速复制模板

### 父项目模板

```toml
[project]
name = "backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "spark-harness",    # 添加你的子包
]

[tool.uv.workspace]
members = ["packages/*", "packages/*/*"]

[tool.uv.sources]
spark-harness = { workspace = true }
```

### 子包模板

```toml
[project]
name = "spark-harness"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["spark"]
```

---

