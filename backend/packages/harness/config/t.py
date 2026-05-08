from pydantic import BaseModel, ConfigDict

class ModelConfig(BaseModel):
    name: str
    model_config = ConfigDict(extra="allow")

m = ModelConfig.model_validate({"name": "gpt", "temperature": 0.7, "maxxx": "abc"})

print(m.name)                    # -> "gpt"
print(ModelConfig.model_config)  # -> ConfigDict(extra='allow', ...)
print(m.model_dump())            # -> {'name': 'gpt', 'temperature': 0.7}
print(m.__pydantic_extra__)      # -> {'temperature': 0.7}