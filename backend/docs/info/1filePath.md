def _default_config_candidates() -> tuple[Path, ...]:
    backend_dir = Path(__file__).resolve().parents[3]
    repo_root = backend_dir.parent
    return (backend_dir / "config.yaml", repo_root / "config.yaml")


## 1. 核心逻辑拆解

* backend_dir = Path(__file__).resolve().parents[4]
* __file__：指的是当前这个 Python 文件的绝对路径。
   * .resolve()：将其转换为标准的绝对路径。
   * .parents[4]：表示向上跳 4 级目录。通常是因为该文件被埋得很深（比如在 src/project/api/v1/utils.py 这种结构里），跳 4 级正好能到达后端的根目录（backend_dir）。
* repo_root = backend_dir.parent
* 在 backend_dir 的基础上再往上一级，通常这就是整个 Git 仓库的根目录（repo_root）。
* return (backend_dir / "config.yaml", repo_root / "config.yaml")
* 使用 / 运算符拼接文件名。
   * 函数最后返回一个包含两个路径的元组：
   1. 后端目录下的 config.yaml。
      2. 仓库根目录下的 config.yaml。
   
## 2. 总结
这个函数定义了配置文件的搜索优先级。程序在启动时，会按照这个元组提供的路径顺序去检查文件是否存在，从而实现“在哪都能找到配置文件”的效果。
代码逻辑示意图：

/repo_root (仓库根目录)  <-- 候选路径 2
  ├── backend_dir (后端目录)  <-- 候选路径 1
  │     ├── ...
  │     └── 当前文件 (向上跳 4 级到 backend)
  └── config.yaml



