from openai import OpenAI
from pydantic import  BaseModel,  Field, EmailStr

class UserInfo(BaseModel):
    name: str = Field(..., description="The user's full name")
    email: EmailStr = Field(..., description="The user's email address")
    age: int = Field(..., description="The user's age")


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[
        {"role": "user", "content": "My name is Alice, I am 23 years old, my email is exam@mail.com"}
    ],
    tools = [
        {
            "type": "function",
            "function": {
                "name": UserInfo.__name__,
                "description": UserInfo.__doc__,
                "parameters": UserInfo.model_json_schema()
            }
        }
    ],
    tool_choice={"type": "function", "function": UserInfo.__name__}
)

userInfo = UserInfo.model_validate_json(response.choices[0].message.tool_calls[0].function.arguments)

print(userInfo)