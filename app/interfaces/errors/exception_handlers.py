import logging

from fastapi import FastAPI, Request

from fastapi.responses import  JSONResponse

from app.application.errors.exceptions import AppException
from app.interfaces.schemas import Response
from starlette.exceptions import HTTPException

logger =logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppException)
    async def app_exception_handler(req: Request, e: AppException) -> JSONResponse:
        logger.error(f"AppException: {e.code} - {e.msg}")
        return JSONResponse(
            status_code=e.status_code,
            content=Response(
                code=e.status_code,
                msg=e.msg,
                data={}
            ).model_dump()
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(req: Request, e: HTTPException) -> JSONResponse:
        logger.error(f"HTTPException: {e.status_code} - {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content=Response(
                code=e.status_code,
                msg=e.detail,
                data={}
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def exception_handler(req: Request, e: Exception) -> JSONResponse:

        logger.error(f"Exception: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=Response(
                code=500,
                msg="internal server error",
                data={},
            ).model_dump()
        )
