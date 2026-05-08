from pydantic import BaseModel, ConfigDict, Field

class ModelConfig(BaseModel):

    name: str = Field(..., description="unique name for the model")
    display_name: str | None = Field(..., description="display name for the model")
    description: str | None = Field(...,  description="description for the model")
    use: str = Field(..., description="class path of the model provider(e.g. langchain_openai.ChatOpenAi")
    model: str = Field(..., description="model name")
    model_config = ConfigDict(extra="allow")
    use_responses_api: bool | None = Field(
        default=None,
        description="Whether to route OpenAI ChatOpenAI calls through the /v1/responses API",
    )
    output_version: str | None = Field(
        default=None,
        description="Structured output version for OpenAI responses content, e.g. responses/v1",
    )
    supports_thinking: bool = Field(default_factory=lambda: False, description="Whether the model supports thinking")
