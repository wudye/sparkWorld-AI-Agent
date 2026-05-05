import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ]
)

logger = logging.getLogger(__name__)



import logging
import os
import inspect

def setup_logger(log_level=logging.INFO):
    """配置并返回日志记录器，日志文件名自动匹配调用模块名"""
    # 获取调用此函数的模块名
    caller_frame = inspect.stack()[1]
    caller_module = inspect.getmodule(caller_frame[0])
    module_name = os.path.splitext(os.path.basename(caller_module.__file__))[0]
    
    log_file = f"{module_name}.log"
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    

    # 每日轮转，保留30天
    from logging.handlers import TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        f"{module_name}.log",
        when="midnight",
        interval=1,
        backupCount=30  # 保留30天
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # 配置日志记录器
    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger



import logging
import os
from datetime import datetime


def setup_logger():

    """统一配置日志：控制台 + 自动按模块分文件到 logs/ 目录"""
    # 检查是否已配置
    if logging.getLogger().handlers:
        return

    # 创建 logs 目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 带时间戳的文件处理器
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"app_{timestamp}.log"),
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)






```python
"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

| 占位符 | 含义 | 实际输出示例 |
|--------|------|-------------|
| `%(asctime)s` | **时间** (as-time) | `2026-05-04 14:30:01` |
| `%(name)s` | **日志器名称** | `main`、`router`、`uvicorn.error` |
| `%(levelname)s` | **日志级别** (level-name) | `INFO`、`WARNING`、`ERROR` |
| `%(message)s` | **日志内容** | `服务启动成功` |

## 可以用哪些占位符

| 占位符 | 含义 | 示例值 |
|--------|------|--------|
| `%(asctime)s` | 时间（配合 `datefmt` 自定义格式） | `2026-05-04 14:30:01` |
| `%(name)s` | 日志器名称（`__name__` 的值） | `main` |
| `%(levelname)s` | 级别名称 | `INFO` |
| `%(levelno)s` | 级别数字 | `20` |
| `%(message)s` | 日志消息 | `服务启动成功` |
| `%(filename)s` | 文件名 | `main.py` |
| `%(module)s` | 模块名（不带.py） | `main` |
| `%(funcName)s` | 函数名 | `root` |
| `%(lineno)d` | 行号 | `42` |
| `%(pathname)s` | 完整文件路径 | `F:\...\backend\main.py` |
| `%(process)d` | 进程ID | `1420` |
| `%(threadName)s` | 线程名 | `MainThread` |

## 组合示例

```python
# 更详细的格式
format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
# 输出：2026-05-04 14:30:01 - main - INFO - main.py:42 - 服务启动成功

# 带进程和线程（用于调试并发问题）
format="%(asctime)s [%(process)d:%(threadName)s] %(levelname)s - %(message)s"
# 输出：2026-05-04 14:30:01 [1420:MainThread] INFO - 服务启动成功
```

## `datefmt` 配合使用

```python
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
datefmt="%Y-%m-%d %H:%M:%S"   # 控制 asctime 的格式
```

`datefmt` 的格式化符号：

| 符号 | 含义 | 示例 |
|------|------|------|
| `%Y` | 4位年份 | `2026` |
| `%m` | 月份 | `05` |
| `%d` | 日期 | `04` |
| `%H` | 小时(24h) | `14` |
| `%M` | 分钟 | `30` |
| `%S` | 秒 | `01` |

其中 `s` 后缀（如 `%(asctime)s`）是 Python 的**字符串格式化语法**，表示这个占位符接受的是字符串类型，不是日志格式本身的含义。