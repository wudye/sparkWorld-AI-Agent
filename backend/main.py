from fastapi import FastAPI
import uvicorn
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from utils.log_config import setup_logger
from utils.log_config import get_logger
from fastapi.security import APIKeyHeader, HTTPBearer

from utils.global_exception_handler import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware
from app.routers import agents

from packages.harness.config.app_config import get_app_config
import sys, os
from pathlib import  Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

setup_logger()
logger = get_logger(__name__)


logger.info(".---------------------------------------------------------------------------")

# 创建认证方案实例（写在 FastAPI() 外面）
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)
jwt_scheme = HTTPBearer(auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.info("hello in lifespan")
        app.state.config = get_app_config()
    except Exception:
        logger.exception("error in lifespan")

    yield

    logger.info("closed the agent")


def create_app() -> FastAPI:
    app = FastAPI(
        title="SparkWorld AI Agent",
        description="common ai agent harness includes everything",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {
                "name": "models",
                "description": "Operations for querying available AI models and their configurations",
            },
            {
                "name": "mcp",
                "description": "Manage Model Context Protocol (MCP) server configurations",
            },
            {
                "name": "memory",
                "description": "Access and manage global memory data for personalized conversations",
            },
            {
                "name": "skills",
                "description": "Manage skills and their configurations",
            },
            {
                "name": "artifacts",
                "description": "Access and download thread artifacts and generated files",
            },
            {
                "name": "uploads",
                "description": "Upload and manage user files for threads",
            },
            {
                "name": "threads",
                "description": "Manage DeerFlow thread-local filesystem data",
            },
            {
                "name": "agents",
                "description": "Create and manage custom agents with per-agent config and prompts",
            },
            {
                "name": "suggestions",
                "description": "Generate follow-up question suggestions for conversations",
            },
            {
                "name": "channels",
                "description": "Manage IM channel integrations (Feishu, Slack, Telegram)",
            },
            {
                "name": "assistants-compat",
                "description": "LangGraph Platform-compatible assistants API (stub)",
            },
            {
                "name": "runs",
                "description": "LangGraph Platform-compatible runs lifecycle (create, stream, cancel)",
            },
            {
                "name": "health",
                "description": "Health check and system status endpoints",
            },
        ],
        swagger_ui_parameters={
            "persistAuthorization": True,
        },
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ====== ③ 静态文件挂载（可选） ======
    # from fastapi.staticfiles import StaticFiles
    # app.mount("/static", StaticFiles(directory="static"), name="static")

    register_exception_handlers(app)


    app.include_router(agents.router)
    @app.get("/health",tags=["health"])
    async def health_check() -> dict:
        return {"status": "health", "service": "spark world ai main"}

    return app

app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
