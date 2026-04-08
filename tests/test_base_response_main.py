from fastapi import  FastAPI
from pydantic import  BaseModel
from app.interfaces.schemas.base import Response  # ✅ 添加 app. 前缀
from typing import  List

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

db_users = {
    1: User(id=1, name="Alice"),
    2:User(id=2, name="Bob"),
    3:User(id=3, name="Charlie")
}

@app.get("/users/{user_id}", response_model=Response[User])
async def get_user(user_id: int):
    user = db_users.get(user_id)
    if not user:
        return Response.fail(code=404, msg="User not found")
    return Response.success(data=user)

@app.get("/users", response_model=Response[list[User]])
async def get_all_users():
    users = list(db_users.values())
    return Response.success(data=users)