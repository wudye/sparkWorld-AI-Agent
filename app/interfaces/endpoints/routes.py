
from fastapi import APIRouter
from . import status_routes
from . import minio_test

def create_api_router() ->APIRouter:

    api_router = APIRouter()

    api_router.include_router(status_routes.router)
    api_router.include_router(minio_test.router)

    return api_router

router = create_api_router()