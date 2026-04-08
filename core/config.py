from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    env: str = "development"
    log_level: str = "INFO"
    app_config_path: str = "config.yaml"
    AUTO_MIGRATE: bool = True        # 配置项控制是否自动迁移


    sqlalchemy_database_uri: str = "postgresql+asyncpg://spark:spark@localhost:5432/spark_db"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    minio_endpoint: str = "localhost:9000"   # ← 新增：S3 API 地址
    minio_secure: bool = False              # ← 新增：是否使用 HTTPS
    minio_bucket : str =""
    minio_root_user: str = ""
    minio_root_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

"""
if __name__ == "__main__":
    settings = Settings()
    print(settings)

"""

@lru_cache()
def get_settings() ->Settings:
    """get settings with cache, so that it will not be loaded multiple times"""
    settings =  Settings()
    return settings