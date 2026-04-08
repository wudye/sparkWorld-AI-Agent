import logging
from fastapi import APIRouter
from fastapi import File, UploadFile, Form, Query, HTTPException
from app.interfaces.schemas import Response
from app.infrastructure.storage.cos import get_minio
from typing import Optional
"""
powershell:

# ========== 测试 MinIO API ==========

# 1. 上传文件
"Hello from PowerShell!" | Out-File "test.txt" -Encoding utf8
curl.exe -X POST "http://localhost:8000/api/minio/upload" -F "file=@test.txt" -F "object_name=test/hello.txt"

# 2. 列出文件
curl.exe "http://localhost:8000/api/minio/files"

# 3. 获取文件信息
curl.exe "http://localhost:8000/api/minio/hello.txt/info"

# 4. 获取临时链接
curl.exe "http://localhost:8000/api/minio/hello.txt/url?expires=3600"


# 5. 下载文件
curl.exe -O "http://localhost:8000/api/minio/test/hello.txt"

# 6. 删除文件
curl.exe -X DELETE "http://localhost:8000/api/minio/test/hello.txt"

# 7. 批量删除
curl.exe -X DELETE "http://localhost:8000/api/minio/batch/delete?object_names=test/hello.txt"

"""




logger = logging.getLogger(__name__)

router = APIRouter(prefix="/minio", tags=["minio management"])


@router.post(
    "/upload",
    response_model=Response,
    summary="上传文件到MinIO",
    description="通过表单上传文件到MinIO对象存储"
)
async def upload_file(
        file: UploadFile = File(..., description="要上传的文件"),
        object_name: Optional[str] = Form(None, description="存储的对象名(可选)"),
):
    """上传文件到 MinIO"""
    minio = get_minio()
    try:
        content = await file.read()
        target_name = object_name or file.filename

        # 根据文件扩展名设置 content_type
        content_type = file.content_type or "application/octet-stream"

        success = await minio.upload_bytes(
            data=content,
            object_name=target_name,
            content_type=content_type,
        )

        if success:
            return Response.success(
                msg="文件上传成功",
                data={"object_name": target_name}
            )
        return Response.fail(code=500, msg="文件上传失败")
    except Exception as e:
        logger.error(f"上传文件异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{object_name}",
    response_model=Response,
    summary="覆盖更新文件",
    description="覆盖更新已存在的文件(相当于UPDATE)"
)
async def update_file(
        object_name: str,
        file: UploadFile = File(..., description="新的文件内容"),
):
    """更新（覆盖）MinIO 中的文件"""
    minio = get_minio()
    try:
        content = await file.read()
        success = await minio.upload_bytes(
            data=content,
            object_name=object_name,
            content_type=file.content_type or "application/octet-stream",
        )

        if success:
            return Response.success(msg=f"文件 {object_name} 更新成功")
        return Response.fail(code=500, msg="文件更新失败")
    except Exception as e:
        logger.error(f"更新文件异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════
#  R - READ (下载/获取)
# ══════════════════════════════════════

@router.get(
    "/files",
    response_model=Response,
    summary="列出所有文件",
    description="列出Bucket中的文件列表"
)
async def list_files(
        prefix: str = Query("", description="文件名前缀过滤"),
        recursive: bool = Query(True, description="是否递归子目录"),
):
    """列出 MinIO 中的文件列表"""
    minio = get_minio()
    try:
        files = await minio.list_files(prefix=prefix, recursive=recursive)
        return Response.success(data={"files": files, "count": len(files)})
    except Exception as e:
        logger.error(f"列取文件异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{object_name}/info",
    response_model=Response,
    summary="获取文件元信息",
    description="获取文件的大小、类型、修改时间等元信息"
)
async def get_file_info(object_name: str):
    """获取文件的元信息"""
    minio = get_minio()
    try:
        info = await minio.stat_file(object_name)
        if info is None:
            raise HTTPException(status_code=404, detail="文件不存在")
        return Response.success(data=info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件信息异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{object_name}/url",
    response_model=Response,
    summary="生成临时访问链接",
    description="生成文件的临时预签名URL(用于直接下载或预览)"
)
async def get_file_url(
        object_name: str,
        expires: int = Query(3600, ge=60, le=86400, description="有效期(秒), 60~86400"),
):
    """生成文件的临时访问链接"""
    minio = get_minio()
    try:
        url = await minio.get_presigned_url(object_name, expires=expires)
        if url is None:
            raise HTTPException(status_code=404, detail="文件不存在")
        return Response.success(data={
            "url": url,
            "expires_in": expires,
            "object_name": object_name
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成访问链接异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{object_name}",
    summary="下载文件",
    description="直接下载文件(返回二进制数据)"
)
async def download_file(object_name: str):
    """下载文件内容（返回 bytes）"""
    from fastapi.responses import Response as FastAPIResponse

    minio = get_minio()
    try:
        data = await minio.get_file(object_name)
        if data is None:
            raise HTTPException(status_code=404, detail="文件不存在")

        # 获取文件信息以确定 media type
        info = await minio.stat_file(object_name)
        content_type = info.get("content_type", "application/octet-stream") if info else "application/octet-stream"

        return FastAPIResponse(
            content=data,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{object_name}"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════
#  D - DELETE (删除)
# ══════════════════════════════════════

@router.delete(
    "/{object_name}",
    response_model=Response,
    summary="删除单个文件",
    description="从MinIO中删除指定文件"
)
async def delete_single_file(object_name: str):
    """删除单个文件"""
    minio = get_minio()
    try:
        success = await minio.delete_file(object_name)
        if success:
            return Response.success(msg=f"文件 {object_name} 删除成功")
        return Response.fail(code=500, msg="文件删除失败")
    except Exception as e:
        logger.error(f"删除文件异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/batch/delete",
    response_model=Response,
    summary="批量删除文件",
    description="一次删除多个文件"
)
async def batch_delete_files(
        object_names: list[str] = Query(..., description="要删除的文件名列表"),
):
    """批量删除多个文件"""
    minio = get_minio()
    try:
        success = await minio.delete_files(object_names)
        if success:
            return Response.success(
                msg=f"成功删除 {len(object_names)} 个文件",
                data={"deleted_count": len(object_names)}
            )
        return Response.fail(code=500, msg="批量删除失败")
    except Exception as e:
        logger.error(f"批量删除异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))