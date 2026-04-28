# `pyproject.toml` 高级配置解释

这些配置**不会自动创建**，需要你**手动添加**到 `pyproject.toml` 中，用于高级功能。

---

## 1️⃣ `[project.optional-dependencies]`

### 意思：**可选功能依赖**

这些是**非必需**的依赖，只有当你需要特定功能时才安装。

```toml
[project.optional-dependencies]
# 如果你想用 Ollama 模型，才需要装这个
ollama = ["langchain-ollama>=0.3.0"]

# 如果你想处理 PDF 文件，才需要装这个
pymupdf = ["pymupdf4llm>=0.0.17"]
```

### 为什么需要？

- **保持核心包轻量**：不是每个人都需要 Ollama 或 PDF 功能。
- **避免不必要的安装**：如果用户没有 Ollama，就不需要装 `langchain-ollama`。

### 如何安装？

**默认不安装**:
```powershell
uv sync
# ✗ 不会安装 ollama 和 pymupdf
```

**手动安装可选依赖**:
```powershell
# 安装 ollama 功能
uv add --optional ollama langchain-ollama>=0.3.0

# 或在同步时包含
uv sync --with ollama

# 安装所有可选依赖
uv sync --all-extras
```

---

## 2️⃣ `[build-system]`

### 意思：**项目打包工具**

这部分告诉 Python 如何**构建**你的项目（例如，打包成一个 `.whl` 文件发布到 PyPI）。

```toml
[build-system]
# 打包需要 hatchling 工具
requires = ["hatchling"]

# 使用 hatchling 的 build 后端
build-backend = "hatchling.build"
```

### 为什么需要？

- **标准化构建流程**：所有 Python 项目都用这个标准方式定义构建工具。
- **指定构建工具**：这里指定了用 `hatchling`（一个现代的构建工具），也可以是 `setuptools` 或 `flit`。

### 如何使用？

```powershell
# 构建项目（生成 .whl 和 .tar.gz 文件）
uv build

# 这会:
# 1. 读取 [build-system]
# 2. 安装 hatchling
# 3. 使用 hatchling 打包项目
```

---

## 3️⃣ `[tool.hatch.build.targets.wheel]`

### 意思：**Hatch 构建配置**

这是 `hatchling` 工具的**具体配置**。

```toml
[tool.hatch.build.targets.wheel]
# 打包时，只包含 deerflow/ 文件夹
packages = ["deerflow"]
```

### 为什么需要？

- **精确控制打包内容**：告诉 `hatchling` 你的 Python 包源代码在哪个文件夹。

### 结构图

```
packages/harness/
├── deerflow/                 ← ✅ 这是要打包的源代码
│   ├── __init__.py
│   ├── agents/
│   └── ...
├── pyproject.toml
└── tests/                    ← ❌ 这个文件夹不会被打包
```

当运行 `uv build` 时，`hatchling` 会：
1. 找到 `[tool.hatch.build.targets.wheel]`
2. 看到 `packages = ["deerflow"]`
3. 只把 `deerflow/` 文件夹打包进 `.whl` 文件

---

## 总结

| 配置 | 作用 | 自动创建？ |
|------|------|----------|
| `[project.optional-dependencies]` | 定义可选功能依赖 | ❌ 手动添加 |
| `[build-system]` | 定义项目打包工具 | ❌ 手动添加 |
| `[tool.hatch.build.targets.wheel]` | 配置打包工具的具体行为 | ❌ 手动添加 |

---

## 从零创建时

### 简单项目（不需要这些）

```toml
[project]
name = "my-project"
dependencies = ["fastapi"]
```

✅ **足够了**

### 复杂项目（需要这些）

```toml
[project]
name = "my-project"
dependencies = ["fastapi"]

[project.optional-dependencies]
extra = ["some-package"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["my_project_source_folder"]
```

✅ **用于发布和可选功能**

---

**简单说**：
- `optional-dependencies` → **可选功能**
- `build-system` → **如何打包**
- `tool.hatch` → **打包什么**

这些都是手动配置，用于更高级的项目管理。🎯