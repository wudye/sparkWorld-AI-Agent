import logging
import os
from datetime import datetime


# ANSI 颜色码
class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    # 颜色定义
    GREY = "\033[90m"  # 灰色
    BLUE = "\033[94m"  # 蓝色
    GREEN = "\033[92m"  # 绿色
    YELLOW = "\033[93m"  # 黄色
    RED = "\033[91m"  # 红色
    BOLD_RED = "\033[1;91m"  # 粗体红色
    RESET = "\033[0m"  # 重置

    # 日志级别 → 颜色映射
    COLORS = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }

    def format(self, record):
        # 获取当前日志级别对应的颜色
        color = self.COLORS.get(record.levelno, self.GREY)

        # 给整个日志行上色
        message = super().format(record)
        return f"{color}{message}{self.RESET}"



# 创建一个统一的日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "%Y-%m-%d %H:%M:%S"
)


def setup_logger():
    """配置根日志器（仅控制台输出）"""
    if logging.getLogger().handlers:
        return
    # 控制台用彩色格式化器
    colored_formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(colored_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # 统一日志格式，去掉 uvicorn 默认的日志样式。
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        u_logger = logging.getLogger(name)
        u_logger.handlers.clear()  # 清空 uvicorn 自带 handler
        u_logger.propagate = True  # 向上传递给 root_logger


def get_logger(name):
    """获取带独立文件处理器的日志器"""
    logger = logging.getLogger(name)

    # 防止重复添加 handler
    if any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        return logger

    # 每个模块独立的日志文件
    log_file = os.path.join(LOG_DIR, f"{name}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 关闭向父日志器传递（避免日志重复打印）
    # logger.propagate = False

    return logger
