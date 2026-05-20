from typing import Callable

from fastapi import FastAPI
import asyncio
import logging
from collections.abc import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S"
)

logger= logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI()
    return app

app = create_app

