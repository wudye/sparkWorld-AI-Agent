

import logging
from functools import lru_cache
from typing import Optional
from datetime import timedelta
import io
from minio.error import S3Error

from minio import Minio
from core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class MinIOStorage:
    """MinIO 对象存储"""

    def __init__(self):
        self._settings: Settings = get_settings()
        self._client: Optional[Minio] = None

    async def init(self) -> None:
        """完成 MinIO 对象存储客户端的创建"""
        # 1. 判断客户端是否存在，如果存在则记录日志并终止程序
        if self._client is not None:
            logger.warning("MinIO object storage client is already initialized")
            return

        try:
            # 2. 创建 MinIO 客户端
            self._client = Minio(
                endpoint=self._settings.minio_endpoint,      # "localhost:9000"
                access_key=self._settings.minio_root_user,
                secret_key=self._settings.minio_root_password,
                secure=self._settings.minio_secure,           # False (HTTP)
            )

            # 3. 自动创建 bucket（如果不存在）
            if not self._client.bucket_exists(self._settings.minio_bucket):
                self._client.make_bucket(self._settings.minio_bucket)
                logger.info(f"Bucket [{self._settings.minio_bucket}] created successfully")
            else:
                logger.info(f"Bucket [{self._settings.minio_bucket}] is already exists")

            logger.info("MinIO storage initialized successfully")
        except Exception as e:
            logger.error(f"MinIO initialization failed: {str(e)}")
            raise


    async def upload_file(
            self,
            file_path: str,  # 本地文件路径，如 "images/photo.jpg"
            object_name: str = None,  # 存储在 MinIO 的对象名，默认同 file_path
            content_type: str = "application/octet-stream",
    ) -> bool:
        """上传本地文件到 MinIO"""
        object_name = object_name or file_path
        try:
            self.client.fput_object(
                bucket_name=self._settings.minio_bucket,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type,
            )
            logger.info(f"文件上传成功: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"文件上传失败: {e}")
            return False

    async def upload_bytes(
            self,
            data: bytes | str,
            object_name: str,  # 存储对象名，如 "files/document.txt"
            length: int = None,
            content_type: str = "application/octet-stream",
    ) -> bool:
        """上传字节/字符串数据到 MinIO"""
        if isinstance(data, str):
            data = data.encode("utf-8")
            length = len(data)
        try:
            self.client.put_object(
                bucket_name=self._settings.minio_bucket,
                object_name=object_name,
                data=io.BytesIO(data),
                length=length or len(data),
                content_type=content_type,
            )
            logger.info(f"数据上传成功: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"数据上传失败: {e}")
            return False

    # ══════════════════════════════════════
    #  R - READ (下载/获取文件)
    # ══════════════════════════════════════

    async def download_file(
            self,
            object_name: str,  # MinIO 中的对象名
            file_path: str,  # 保存到的本地路径
    ) -> bool:
        """从 MinIO 下载文件到本地"""
        try:
            self.client.fget_object(
                bucket_name=self._settings.minio_bucket,
                object_name=object_name,
                file_path=file_path,
            )
            logger.info(f"文件下载成功: {object_name} -> {file_path}")
            return True
        except S3Error as e:
            logger.error(f"文件下载失败: {e}")
            return False

    async def get_file(self, object_name: str) -> bytes | None:
        """从 MinIO 获取文件的字节数据"""
        try:
            response = self.client.get_object(
                bucket_name=self._settings.minio_bucket,
                object_name=object_name,
            )
            data = response.read()
            response.close()
            response.release_conn()
            logger.info(f"获取文件数据成功: {object_name}")
            return data
        except S3Error as e:
            logger.error(f"获取文件数据失败: {e}")
            return None

    async def get_presigned_url(
            self,
            object_name: str,
            expires: int = 3600,  # 有效期（秒），默认1小时
    ) -> str | None:
        """生成临时访问链接（用于前端直接下载/预览）"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=self._settings.minio_bucket,
                object_name=object_name,
                expires=timedelta(seconds=expires),
            )
            return url
        except S3Error as e:
            logger.error(f"生成预签名URL失败: {e}")
            return None

    async def list_files(self, prefix: str = "", recursive: bool = True) -> list:
        """列出 Bucket 中的文件列表"""
        try:
            objects = self.client.list_objects(
                bucket_name=self._settings.minio_bucket,
                prefix=prefix,
                recursive=recursive,
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"列取文件失败: {e}")
            return []

    async def stat_file(self, object_name: str) -> dict | None:
        """获取文件元信息（大小、类型、最后修改时间等）"""
        try:
            info = self.client.stat_object(
                bucket_name=self._settings.minio_bucket,
                object_name=object_name,
            )
            return {
                "name": info.object_name,
                "size": info.size,
                "content_type": info.content_type,
                "last_modified": info.last_modified,
                "etag": info.etag,
            }
        except S3Error as e:
            logger.error(f"获取文件信息失败: {e}")
            return None

    # ══════════════════════════════════════
    #  U - UPDATE (覆盖上传 = 更新)
    # ══════════════════════════════════════

    async def copy_object(
            self,
            source_object: str,  # 源对象名
            dest_object: str,  # 目标对象名（可同名覆盖）
    ) -> bool:
        """复制/移动对象（可用于重命名或更新）"""
        try:
            self.client.copy_object(
                bucket_name=self._settings.minio_bucket,
                object_name=dest_object,
                source=f"{self._settings.minio_bucket}/{source_object}",
            )
            logger.info(f"对象复制成功: {source_object} -> {dest_object}")
            return True
        except S3Error as e:
            logger.error(f"对象复制失败: {e}")
            return False

    # ══════════════════════════════════════
    #  D - DELETE (删除文件)
    # ══════════════════════════════════════

    async def delete_file(self, object_name: str) -> bool:
        """删除单个文件"""
        try:
            self.client.remove_object(
                bucket_name=self._settings.minio_bucket,
                object_name=object_name,
            )
            logger.info(f"文件删除成功: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"文件删除失败: {e}")
            return False

    async def delete_files(self, object_names: list[str]) -> bool:
        """批量删除多个文件"""
        try:
            errors = self.client.remove_objects(
                bucket_name=self._settings.minio_bucket,
                objects_iter=object_names,
            )
            for error in errors:
                logger.error(f"批量删除出错: {error}")
            logger.info(f"批量删除完成")
            return True
        except S3Error as e:
            logger.error(f"批量删除失败: {e}")
            return False

    async def shutdown(self) -> None:
        """关闭 MinIO 对象存储"""
        if self._client is not None:
            self._client = None
            logger.info("closed MinIO ")

        get_minio.cache_clear()

    @property
    def client(self) -> Minio:
        """只读属性，返回 MinIO 对象存储客户端"""
        if self._client is None:
            raise RuntimeError("MinIO object storage client is not initialized")
        return self._client


@lru_cache()
def get_minio() -> MinIOStorage:
    """获取 MinIO 对象存储实例"""
    return MinIOStorage()
