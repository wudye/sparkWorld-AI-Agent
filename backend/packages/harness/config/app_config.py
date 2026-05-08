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
    models: list[ModelConfig] = Field(default_factory=list, description="Available models")
    sandbox: SandboxConfig = Field(description="Sandbox configuration")
    tools: list[ToolConfig] = Field(default_factory=list, description="Available tools")
    tool_groups: list[ToolGroupConfig] = Field(default_factory=list, description="Available tool groups")
    skills: SkillsConfig = Field(default_factory=SkillsConfig, description="Skills configuration")
    skill_evolution: SkillEvolutionConfig = Field(default_factory=SkillEvolutionConfig, description="Agent-managed skill evolution configuration")
    extensions: ExtensionsConfig = Field(default_factory=ExtensionsConfig, description="Extensions configuration (MCP servers and skills state)")
    tool_search: ToolSearchConfig = Field(default_factory=ToolSearchConfig, description="Tool search / deferred loading configuration")
    title: TitleConfig = Field(default_factory=TitleConfig, description="Automatic title generation configuration")
    summarization: SummarizationConfig = Field(default_factory=SummarizationConfig, description="Conversation summarization configuration")
    memory: MemoryConfig = Field(default_factory=MemoryConfig, description="Memory subsystem configuration")
    agents_api: AgentsApiConfig = Field(default_factory=AgentsApiConfig, description="Custom-agent management API configuration")
    subagents: SubagentsAppConfig = Field(default_factory=SubagentsAppConfig, description="Subagent runtime configuration")
    guardrails: GuardrailsConfig = Field(default_factory=GuardrailsConfig, description="Guardrail middleware configuration")
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig, description="LLM circuit breaker configuration")
    model_config = ConfigDict(extra="allow", frozen=False)
    checkpointer: CheckpointerConfig | None = Field(default=None, description="Checkpointer configuration")
    stream_bridge: StreamBridgeConfig | None = Field(default=None, description="Stream bridge configuration")


    def __init__(self, **data):
        super().__init__(**data)
        logger.info("test in class")


def get_app_config():
    logger.info("this is from child test")
    _default_config_candidates()
    AppConfig()
    logger.info("end test")