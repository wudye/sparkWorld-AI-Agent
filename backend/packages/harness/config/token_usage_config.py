from pydantic import BaseModel, Field

class TokenUsageConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable token usage tracking middleware")