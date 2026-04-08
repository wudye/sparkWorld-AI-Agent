from typing import List
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "items",
        "description": "Operations with items.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

api = FastAPI(
    title="FastAPI",
    description="This is a very fancy project that includes everything fastapi has to offer",
    version="0.0.1",
    openapi_tags=tags_metadata
)

class User(BaseModel):
    id: int
    name: str

class Order(BaseModel):
    id: int
    item: str
    price: float


user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/", response_model=List[User], summary="get user list", description="get user list")
async  def get_users():
    return [User(id=1,  name="user1"), User(id=2, name="user2")]

@user_router.post("/", response_model=User, summary="create user", description="create user")
async def create_user(user: User):
    return user

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/", response_model=List[Order], summary="get order list", description="get order list")
async def get_order():
    return [Order(id=1, item="item1", price=10.0), Order(id=2, item="item2", price=20.0)]

@order_router.post("/", response_model=Order, summary="create order", description="create order")
async def create_order(order: Order):
    return order

api.include_router(user_router)
api.include_router(order_router)