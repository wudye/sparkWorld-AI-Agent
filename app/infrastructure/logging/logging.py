import sys

from langchain_community.vectorstores.oraclevs import log_level

from core.config import get_settings
import logging

def setup_logging():
    setting = get_settings()

    # get root logger object
    root_logger = logging.getLogger()

    # Remove any existing handlers so you don’t get duplicate logs.
    root_logger.handlers.clear()
    log_level = getattr(logging, setting.log_level.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)
    root_logger.addHandler(stream_handler)

    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    root_logger.info("Logging initialized. Log level is set up with level: %s", setting.log_level)
