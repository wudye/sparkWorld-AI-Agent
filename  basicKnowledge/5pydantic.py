from pydantic import  BaseModel,  Field, EmailStr

class UserInfo(BaseModel):
    name: str = Field(..., description="The user's full name")
    email: EmailStr = Field(..., description="The user's email address")
    age: int = Field(..., description="The user's age")


json_string = '{"name": "Alice", "email": "test@email.com", "age": 23}'
try:
    user = UserInfo.model_validate_json(json_string)
    print(user)
    print(user.name)
    print(user.email)
    print(user.age)
except Exception as e:
    print(e)


print(UserInfo.model_json_schema())