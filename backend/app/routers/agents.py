# from ...utils.log_config import get_logger
from utils.log_config import get_logger
from fastapi import APIRouter


logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["agents"])

@router.get(
    "/agents1",
    summary="List Custom Agents",
    description="All agents available in the agents directory including their soul content"
)
async def agents1():
    logger.info("test in agents")
    return "hello from agents"

@router.get(
    "/agents2",
    summary="List Custom Agents",
    description="All agents available in the agents directory including their soul content"
)
async def agents2():
    logger.info("test in agents")
    return "hello from agents2222222222"