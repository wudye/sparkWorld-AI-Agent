
import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
import uuid


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器到 FastAPI 实例"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """处理 HTTP 异常（404、401、手动 raise 等）"""
        logger.warning(
            f"HTTP {exc.status_code}: {exc.detail} | "
            f"path={request.url.path} | method={request.method}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.detail,
                "path": request.url.path,
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """处理请求参数校验失败"""
        logger.warning(
            f"参数校验失败 | path={request.url.path} | {exc.errors()}"
        )
        return JSONResponse(
            status_code=422,
            content={
                "message": "请求参数错误",
                "detail": exc.errors(),
            }
        )
    """
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"未捕获异常 | path={request.url.path} | method={request.method}\n"
            f"{traceback.format_exc()}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal Server Error",
            }
        )
    """

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # 生成一个唯一错误 ID，方便排查
        error_id = str(uuid.uuid4())[:8]

        # 打印完整堆栈
        logger.error(
            f"异常捕获 [ID={error_id}]\n"
            f"路径: {request.method} {request.url.path}\n"
            f"参数: {dict(request.query_params)}\n"
            f"错误: {exc}\n"
            f"堆栈: {traceback.format_exc()}"
        )

        # 生产环境不要暴露具体错误信息给用户
        return JSONResponse(
            status_code=500,
            content={
                "message": "服务器内部错误",
                "error_id": error_id,  # 给用户这个 ID，运维可以查日志
            }
        )
