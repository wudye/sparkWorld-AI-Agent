# Day 09 - Profile 隔离与多实例架构

## 目标
掌握 Profile 的完整设计、实现细节、以及如何在多实例模式下安全运行。这对部署和用户体验至关重要。

## 关键文件
- `hermes_cli/main.py`（Profile 入口）
- `hermes_constants.py`（Profile 工具集）
- `hermes_cli/config.py`（Profile 检测）

## 学习内容

### 1) Profile 的目的与设计
```
需求：支持在同一台机器上运行多个独立的 Hermes 实例
- 不同的 API keys（不同供应商账户）
- 不同的配置（不同模型、工具集）
- 不同的会话历史
- 不同的工作目录

解决方案：Profile 机制
~/.hermes/              # 默认 profile（default）
~/.hermes/profiles/work/        # work profile
~/.hermes/profiles/research/    # research profile

每个 profile 完全独立：
- HERMES_HOME 指向不同目录
- config.yaml 在各自的目录
- .env 在各自的目录
- state.db 在各自的目录
```

### 2) Profile 的早期初始化
```python
# hermes_cli/main.py

def main():
    """Entry point"""
    
    # 第 1 步：解析 -p 参数
    parser = ArgumentParser()
    parser.add_argument("-p", "--profile", default="default")
    args, remaining_args = parser.parse_known_args()
    
    # 第 2 步：应用 profile 覆盖（在其他模块导入前）
    _apply_profile_override(args.profile)
    # 这会设置 HERMES_HOME 环境变量
    
    # 第 3 步：现在导入其他模块是安全的
    from hermes_cli.config import load_cli_config
    from run_agent import AIAgent
    
    # 所有下游代码都会正确读取 get_hermes_home()
    config = load_cli_config()
    
    # ... 启动 CLI
```

**关键**：Profile override 必须在任何其他导入之前执行。

### 3) get_hermes_home() 的正确实现
```python
# hermes_constants.py

_HERMES_HOME_OVERRIDE: Optional[Path] = None

def _apply_profile_override(profile_name: str) -> None:
    """设置 HERMES_HOME 环境变量"""
    global _HERMES_HOME_OVERRIDE
    
    if profile_name == "default":
        # 默认 profile
        hermes_home = Path.home() / ".hermes"
    else:
        # 自定义 profile
        hermes_home = Path.home() / ".hermes" / "profiles" / profile_name
    
    # 创建目录
    hermes_home.mkdir(parents=True, exist_ok=True)
    
    # 设置环境变量
    os.environ["HERMES_HOME"] = str(hermes_home)
    _HERMES_HOME_OVERRIDE = hermes_home

def get_hermes_home() -> Path:
    """获取当前 HERMES_HOME（profile-aware）"""
    # 检查环境变量（由 _apply_profile_override 设置）
    hermes_home = os.environ.get("HERMES_HOME")
    if hermes_home:
        return Path(hermes_home)
    
    # 回退到默认
    return Path.home() / ".hermes"

def display_hermes_home() -> str:
    """用户可见的路径"""
    home = get_hermes_home()
    if "profiles" in str(home):
        # ~/.hermes/profiles/work → "~/.hermes/profiles/work"
        return "~/.hermes/profiles/" + home.name
    else:
        # ~/.hermes → "~/.hermes"
        return "~/.hermes"
```

### 4) 常见的 Profile 相关命令
```bash
# 列出所有 profile
hermes profile list
# work (ACTIVE)
# research
# default

# 切换 profile
hermes -p work config show

# 为 profile 初始化配置
hermes -p research config wizard

# 查看 profile 的会话
hermes -p work session list
```

## 实践任务

### 任务 1: 创建并切换多个 Profile
```bash
# 1. 创建 work profile
hermes -p work profile init

# 2. 在 work profile 中配置
hermes -p work config set model gpt-4-turbo
hermes -p work config set openai_api_key sk-xxx

# 3. 创建 personal profile
hermes -p personal profile init

# 4. 在 personal 中配置不同的 API key
hermes -p personal config set model claude-3-5-sonnet
hermes -p personal config set anthropic_api_key sk-ant-xxx

# 5. 验证隔离
hermes -p work config show      # 应该看到 gpt-4-turbo
hermes -p personal config show  # 应该看到 claude-3-5-sonnet

# 6. 验证会话隔离
hermes -p work chat "hello"
hermes -p personal chat "hello"
hermes -p work session list   # 应该看不到 personal 的会话
```

**验收**：两个 profile 的配置完全独立。

### 任务 2: Profile 路径隔离验证
写一个脚本验证各个模块是否都使用了 profile-safe 的路径：
```python
import os
from pathlib import Path
from hermes_constants import get_hermes_home, display_hermes_home
from hermes_state import SessionDB

def test_profile_path_isolation():
    """验证 profile 路径隔离"""
    
    # 保存默认环境
    orig_home = os.environ.get("HERMES_HOME")
    
    try:
        # 测试 profile: work
        os.environ["HERMES_HOME"] = str(Path.home() / ".hermes" / "profiles" / "work")
        
        # 验证各模块的路径都包含 "work"
        hermes_home = get_hermes_home()
        assert "work" in str(hermes_home), f"get_hermes_home() returned: {hermes_home}"
        
        # SessionDB 应该使用 profile-safe 路径
        db = SessionDB()
        db_path = str(db.db_path)
        assert "work" in db_path, f"DB path: {db_path}"
        
        # 配置路径也应该隔离
        from hermes_cli.config import get_config_path
        config_path = get_config_path()
        assert "work" in str(config_path), f"Config path: {config_path}"
        
        print("✅ All paths are profile-isolated")
        
    finally:
        # 恢复环境
        if orig_home:
            os.environ["HERMES_HOME"] = orig_home
```

**验收**：脚本通过，确认无硬编码路径。

### 任务 3: 多 Profile 并发运行
创建一个脚本，同时在两个 profile 中运行 Agent（模拟）：
```python
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
from hermes_constants import _apply_profile_override, get_hermes_home
from hermes_state import SessionDB

def run_in_profile(profile_name: str, iterations: int):
    """在特定 profile 中运行"""
    # 应用 profile override
    _apply_profile_override(profile_name)
    
    home = get_hermes_home()
    print(f"[{profile_name}] HERMES_HOME = {home}")
    
    # 创建 SessionDB（应该在 profile 目录）
    db = SessionDB()
    
    # 模拟会话
    session_key = f"{profile_name}_session"
    db.create_session(session_key, source="test", model="test")
    
    for i in range(iterations):
        db.save_message(
            session_id=session_key,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}"
        )
    
    messages = db.get_session_messages(session_key)
    print(f"[{profile_name}] Created {len(messages)} messages")
    
    return len(messages)

# 并发运行两个 profile
with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [
        executor.submit(run_in_profile, "work", 10),
        executor.submit(run_in_profile, "personal", 10)
    ]
    results = [f.result() for f in futures]

print(f"Results: {results}")  # [10, 10]
```

**验收**：两个 profile 的数据完全隔离，互不干扰。

### 任务 4: 发现并修复一个硬编码路径
在代码中搜索 `~/.hermes` 或 `Path.home() / ".hermes"`：
```bash
grep -r "~/.hermes" --include="*.py" .
grep -r 'Path.home().*".hermes"' --include="*.py" .
```

如果找到硬编码路径：
1. 用 `get_hermes_home()` 替换
2. 添加一个测试验证修复
3. 运行 `scripts/run_tests.sh` 确保无回归

**验收**：找到并修复至少 1 个硬编码路径。

## 风险点与注意事项

⚠️ **Profile override 的时机** - 必须在导入其他模块前，否则后续 get_hermes_home() 会读到错误的值。
⚠️ **线程安全** - 如果多线程中改变 HERMES_HOME，会导致竞态。应该在启动前设置一次。
⚠️ **环境变量污染** - 如果用户手动设置 HERMES_HOME，会覆盖 profile 机制。
⚠️ **回滚风险** - 删除 profile 目录前要备份，尤其是 state.db。

## 交付物

创建 `notes/day09-profiles.md`：
- Profile 的设计目标与实现
- `get_hermes_home()` 与 `display_hermes_home()` 的区别
- 常见 Profile 命令参考
- 任务 1-4 的验证截图
- 已知的硬编码路径列表与修复计划

## 验收标准

你能够：
1. ✅ 创建并切换多个 Profile
2. ✅ 验证两个 Profile 的配置完全独立
3. ✅ 实现一个 Profile-safe 的模块
4. ✅ 在两个 Profile 中并发运行 Agent
5. ✅ 找到并修复硬编码路径

**最后检查**：能否在同一台机器上运行 5 个不同 Profile，每个用不同 API key？

