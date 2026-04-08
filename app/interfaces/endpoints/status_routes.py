import logging
from fastapi import APIRouter
from app.interfaces.schemas import Response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["status management"])

@router.get(
    path="",
    response_model=Response,
    summary="Check the status of the application",
    description="Check the status of the application"
)
async def get_status() -> Response:
    """Get the status of the application"""
    logger.info("Checking the status of the application")
    return Response.success(data={"status": "ok"})
