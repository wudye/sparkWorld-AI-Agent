from utils.log_config import get_logger
import os
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Self

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

from .token_usage_config import TokenUsageConfig


load_dotenv()
logger = get_logger(__name__)


class CircuitBreakerConfig(BaseModel):
    failure_threshold: int = Field(default=5, description="Number of consecutive failures before tripping the circuit")
    recovery_timeout_sec: int = Field(default=60, description="Time in seconds before attempting to recover the circuit")


def _default_config_candidates() -> tuple[Path, ...]:
    backend_dir = Path(__file__).resolve().parents[3]
    repo_root = backend_dir.parent
    return (backend_dir / "config.yaml", repo_root / "config.yaml")


class AppConfig(BaseModel):
    log_level: str = Field(default="info", description="Logging level for deerflow modules (debug/info/warning/error)")
    token_usage: TokenUsageConfig = Field(default_factory=TokenUsageConfig, description="Token usage tracking configuration")

    def __init__(self, **data):
        super().__init__(**data)
        logger.info("test in class")


def get_app_config():
    logger.info("this is from child test")
    _default_config_candidates()
    AppConfig()
    logger.info("end test")