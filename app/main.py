import logging
from alembic import command
from alembic.config import Config
from core.config import get_settings
from fastapi import FastAPI
from app.infrastructure.logging import  setup_logging
from contextlib import asynccontextmanager
from app.interfaces.endpoints.routes import router
from fastapi.middleware.cors import CORSMiddleware
from app.interfaces.errors.exception_handlers import register_exception_handlers
from app.infrastructure.storage.redis import get_redis
from app.infrastructure.storage.postgres import get_postgres
from app.infrastructure.storage.cos import get_minio


# 1. load settings
settings = get_settings()

# 2. init logging, module level import before app creation to ensure logging is available throughout the application
setup_logging()
logger = logging.getLogger()

# 3.define OpenAPI tags for better documentation organization
openapi_tags = [
    {
        "name": "state management",
        "description": "State management API"
    }
]

@asynccontextmanager
async def lifespan(app: FastAPI):

    # uvicorn has its own logging configuration, we need to call it again to ensure that the logging is configured correctly
    setup_logging()
    logger.info("Starting up the application with environment")

    # on startup, we can run database migrations if AUTO_MIGRATE is enabled and we are in development environment. In production environment, we should not run migrations automatically to avoid potential issues.
    if settings.AUTO_MIGRATE and settings.env == "development":
        try:
            logger.info("Running database migrations...")
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations completed successfully")
        except Exception as e:
            # If migration fails, we log the error. In production environment, we also raise the exception to prevent the application from starting with an inconsistent database state.
            logger.error(f"Migration failed: {e}")
            if settings.env == "production":
                raise

    # Initialize storage clients
    await get_redis().init()
    await get_postgres().init()
    await get_minio().init()

    try:
        yield
    finally:
        try:
            logger.info("Shutting down the application")
        except Exception as e:
            logger.error(f"Error shutting down the application: {e}")

        # Shutdown storage clients
        await get_redis().shutdown()
        await get_postgres().shutdown()
        # MinIO 客户端不需要显式关闭，但如果有其他资源需要清理，可以在这里处理
        await get_minio().shutdown()
        logger.info("Application shutdown complete")

# 4. create FastAPI app with lifespan and OpenAPI tags
app = FastAPI(

    title="SpartWorld Agent",
    description="SpartWorld Agent, the first version uses the A2A MCP and sandbox",
    lifespan=lifespan,
    version="0.0.1",
    openapi_tags=openapi_tags
)

# 5. add CORS middleware to allow cross-origin requests (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# 6. register exception handlers
register_exception_handlers(app)

# 7. include API routes with prefix
app.include_router(router, prefix="/api")