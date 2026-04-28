在 uv 的工作流中，实现“子项目共享虚拟环境”的标准做法是使用 Workspace（工作区） 模式。这种模式下，根目录统一管理虚拟环境（.venv），所有子项目（Sub-projects）共享该环境及其依赖。
以下是具体操作步骤：
## 1. 初始化根项目（Workspace Root）
首先创建一个根目录，作为所有子项目的“家长”。

mkdir my-monorepo && cd my-monorepo
uv init --lib  # 初始化为库模式或应用模式均可

## 2. 配置 pyproject.toml 声明工作区
打开根目录下的 pyproject.toml，手动添加 [tool.uv.workspace] 配置。这告诉 uv 哪些文件夹是子项目。

[project]
name = "my-monorepo"
version = "0.1.0"
dependencies = [] # 这里可以放所有子项目通用的基础依赖

[tool.uv.workspace]
members = ["projects/*"]  # 指定子项目存放的路径

## 3. 创建子项目
在 projects 目录下创建具体的子项目。

mkdir -p projects/sub-app-1
cd projects/sub-app-1
uv init --app  # 初始化子项目

## 4. 建立共享连接
在子项目的 pyproject.toml 中，声明它属于哪个工作区。

[project]
name = "sub-app-1"
version = "0.1.0"
dependencies = [
    "requests", # 子项目特有的依赖
]

[tool.uv]
workspace = { member = true } # 明确声明自己是工作区成员

## 5. 同步与安装
回到根目录执行同步命令。uv 会在根目录创建一个 .venv，并把所有子项目的依赖都安装进去。

cd ../.. # 回到根目录
uv sync

## 6. 在 VS Code 中使用

* 解析器选择：在 VS Code 中按 Ctrl+Shift+P -> Python: Select Interpreter，选择根目录下的 .venv。
* 运行代码：
* 在根目录运行特定子项目：uv run --package sub-app-1 main.py
   * 在子项目目录下运行：uv run main.py（它会自动向上查找并使用根目录的虚拟环境）。

------------------------------
## 核心优势总结

   1. 磁盘空间省：只有一个 .venv 文件夹，避免每个子项目重复下载安装包。
   2. 版本统一：根目录的 uv.lock 会锁定整个工作区的依赖版本，确保子项目之间不会产生版本冲突。
   3. 相互调用：子项目 A 可以非常容易地通过 uv add --path ../sub-lib-b 将子项目 B 作为本地依赖引入。


