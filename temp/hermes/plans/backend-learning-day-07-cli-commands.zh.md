# Day 07 - CLI 命令分发与配置管理

## 目标
理解斜杠命令的中央注册表机制、配置的优先级与加载顺序、以及 Profile 隔离的实现。

## 关键文件
- `hermes_cli/commands.py`
- `hermes_cli/config.py`
- `cli.py`（集成点）
- `hermes_constants.py`（Profile 工具）

## 学习内容

### 1) CommandDef 与中央注册表
```python
# hermes_cli/commands.py

@dataclass
class CommandDef:
    name: str                    # 规范名（如 "resume"）
    description: str
    category: str               # Session / Configuration / Tools & Skills / Info / Exit
    aliases: tuple = ()         # 别名（如 ("r",)）
    args_hint: str = ""         # "[session_id]"
    cli_only: bool = False      # 仅 CLI 可用
    gateway_only: bool = False  # 仅网关可用
    gateway_config_gate: str = ""  # config.yaml 中的判断路径

COMMAND_REGISTRY = [
    CommandDef("resume", "Resume a previous session", "Session", aliases=("r",)),
    CommandDef("clear", "Clear session", "Session"),
    CommandDef("config", "Manage configuration", "Configuration"),
    # ...
]

# 由此自动生成：
# 1. COMMANDS_BY_CATEGORY - 用于 /help 显示
# 2. GATEWAY_KNOWN_COMMANDS - gateway 的分发
# 3. TELEGRAM_COMMANDS - Telegram 菜单
# 4. Slack mapping - /hermes 子命令
```

**关键特性**：
- 单一来源：COMMAND_REGISTRY
- 自动传播到所有消费方
- 别名、网关开关、全类别统一管理

### 2) 命令分发的流程
```python
# cli.py - HermesCLI.process_command()

def process_command(self, cmd_original: str):
    """分发命令"""
    # 1. 规范化命令名
    canonical = resolve_command(cmd_original)
    # "r" → "resume", "config show" → "config"
    
    # 2. 根据规范名分发
    if canonical == "resume":
        self._handle_resume(cmd_original)
    elif canonical == "clear":
        self._handle_clear(cmd_original)
    elif canonical == "config":
        # 可能是 "config show" / "config set" / "config edit"
        self._handle_config(cmd_original)
    # ...
```

**关键**：
- `resolve_command()` 处理别名与子命令
- 分发在一个大 if-elif 块中
- 每个处理函数是一个独立的方法

### 3) 配置加载的优先级
```python
# hermes_cli/config.py

def load_cli_config() -> dict:
    """按优先级加载配置"""
    
    # 1. 硬编码的默认值（最低）
    config = copy.deepcopy(DEFAULT_CONFIG)
    
    # 2. ~/.hermes/config.yaml（用户配置，高优）
    config_path = get_hermes_home() / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            user_config = yaml.safe_load(f) or {}
        # 深度合并
        config = deep_merge(config, user_config)
    
    # 3. ~/.hermes/.env（API key 与密钥，最高）
    env_path = get_hermes_home() / ".env"
    if env_path.exists():
        load_dotenv(env_path)  # 加载到 os.environ
    
    # 4. 系统环境变量（覆盖所有）
    # HERMES_MAX_ITERATIONS=200 可以覆盖 config.yaml
    
    return config
```

**优先级**（从低到高）：
1. 代码硬编码 DEFAULT_CONFIG
2. config.yaml（配置文件）
3. .env（密钥文件）
4. 环境变量（最优先）

### 4) Profile 隔离的关键函数
```python
# hermes_constants.py

def get_hermes_home() -> Path:
    """返回当前 profile 的 HERMES_HOME"""
    # 读取环境变量（早期被 _apply_profile_override() 设置）
    hermes_home = os.environ.get("HERMES_HOME")
    if hermes_home:
        return Path(hermes_home)
    
    # 回退到默认
    return Path.home() / ".hermes"

def display_hermes_home() -> str:
    """返回用户可见的路径"""
    home = get_hermes_home()
    if home.name == ".hermes":
        return "~/.hermes"
    else:
        # profiles/work/
        return str(home.relative_to(Path.home()))

# 使用方式：
# 代码中：from hermes_constants import get_hermes_home
#        db_path = get_hermes_home() / "state.db"
# 用户显示：from hermes_constants import display_hermes_home
#          print(f"Config: {display_hermes_home()}/config.yaml")
```

## 实践任务

### 任务 1: 新增一个斜杠命令
添加 `/echo <text>` 命令，简单返回用户输入。

1. 在 `hermes_cli/commands.py` 中的 `COMMAND_REGISTRY` 添加：
```python
CommandDef("echo", "Echo back the input", "Info", aliases=("e",)),
```

2. 在 `cli.py` 的 `process_command()` 中添加分发：
```python
elif canonical == "echo":
    args = cmd_original.split(maxsplit=1)
    text = args[1] if len(args) > 1 else ""
    print(f"Echo: {text}")
```

3. 测试：
```bash
hermes> /echo hello world
Echo: hello world

hermes> /e test
Echo: test
```

**验收**：两种调用方式都工作。

### 任务 2: 配置优先级演示
创建一个脚本演示配置优先级：
```python
import os
from hermes_cli.config import load_cli_config

# 1. 默认配置
config1 = load_cli_config()
print(f"Default model: {config1.get('model')}")

# 2. 创建 config.yaml
config_content = "model: gpt-4"
(get_hermes_home() / "config.yaml").write_text(config_content)

# 3. 重新加载
config2 = load_cli_config()
print(f"With config.yaml: {config2.get('model')}")

# 4. 设置环境变量
os.environ["HERMES_MODEL"] = "claude-3-5-sonnet"

# 5. 再次重新加载（环境变量应该优先）
config3 = load_cli_config()
print(f"With env var: {config3.get('model')}")  # 应该是 claude-3-5-sonnet
```

**验收**：输出显示正确的优先级覆盖。

### 任务 3: Profile 模式下的隔离测试
```python
from pathlib import Path
from hermes_constants import get_hermes_home, display_hermes_home

def test_profile_isolation():
    """模拟 Profile 切换"""
    
    # 默认 profile
    default_home = get_hermes_home()
    assert "profiles" not in str(default_home)
    
    # 模拟切换到 work profile
    os.environ["HERMES_HOME"] = str(Path.home() / ".hermes" / "profiles" / "work")
    work_home = get_hermes_home()
    assert "profiles/work" in str(work_home)
    
    # 验证状态文件独立
    db1 = work_home / "state.db"
    assert "work" in str(db1)
    
    # 验证可见路径
    display = display_hermes_home()
    assert "work" in display
```

**验收**：多个 profile 的状态文件路径完全独立。

### 任务 4: 改进配置加载的错误处理
现有的 `load_cli_config()` 可能在以下情况崩溃：
- config.yaml 格式错误（YAML 语法错）
- .env 文件权限不足
- 环境变量包含无效值

为 `load_cli_config()` 添加异常处理与日志：
```python
def load_cli_config() -> dict:
    config = copy.deepcopy(DEFAULT_CONFIG)
    
    try:
        config_path = get_hermes_home() / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                user_config = yaml.safe_load(f) or {}
            config = deep_merge(config, user_config)
            logger.info(f"✅ Loaded config from {config_path}")
    except yaml.YAMLError as e:
        logger.error(f"❌ Config YAML error: {e}")
        logger.warning("Using default config")
    except Exception as e:
        logger.error(f"❌ Failed to load config: {e}")
    
    # ... 其他加载逻辑
    
    return config
```

**验收**：能优雅地处理 3 种错误场景，用户看到有用的错误消息。

## 风险点与注意事项

⚠️ **不要硬编码 ~/.hermes** - 用 `get_hermes_home()`。
⚠️ **别名冲突** - 不能有两个命令的别名相同。
⚠️ **子命令的分发** - `/config show` 需要额外解析，不是自动的。
⚠️ **网关特定命令** - 某些命令（如 `/tui`）只在 CLI 中有意义。

## 交付物

创建 `notes/day07-cli-commands.md`：
- CommandDef 的完整设计说明
- 命令分发流程的伪代码
- 配置优先级的优先级表
- Profile 隔离的关键函数
- 任务 1-4 的代码与验证

## 验收标准

你能够：
1. ✅ 新增一个斜杠命令并通过别名调用
2. ✅ 解释配置的 4 级优先级
3. ✅ 区分 `get_hermes_home()` 与 `display_hermes_home()`
4. ✅ 理解 Profile 隔离的实现机制
5. ✅ 为配置加载添加错误处理

**最后检查**：能否在多 Profile 下同时运行两个 Hermes 实例而互不干扰？

