from typing import Callable

from dotenv import load_dotenv
from fastapi import FastAPI
import asyncio
import logging
from collections.abc import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware
from spark.config import app_config as spark_app_config
from spark.config.app_config import apply_logging_level
from contextlib import asynccontextmanager




get_app_config: Callable[[], None] = spark_app_config.get_app_config






logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S"
)

logger= logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    get_app_config()

    try:
        print("test and delete later in lifespan")
        yield
    finally:
        print("test and delete later in lifespan")



def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan
    )
    

    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    return app

app: Callable[[], FastAPI] = create_app()

