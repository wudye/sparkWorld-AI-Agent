from typing import Union
from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/apps/{app_id}")
async def get_app(app_id:int, q: Union[str, None] = None):
    return {"app_id": app_id, "q": q}


# uv run uvicorn 2fastApi:app --reload