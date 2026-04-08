# uvicorn app.main:app --reload       
# 安装所有依赖
    uv sync

controller -> service -> repository -> database
DDD (Domain Driven Design):
- Domain: The core business logic and rules of the application.
- Application: The layer that coordinates the application activities and orchestrates the domain logic.
- Infrastructure: The layer that provides technical capabilities and services to support the application and domain layers.
  - User Interface: The layer that interacts with the users and presents the application functionality. 

user interface -> application -> domain -> infrastructure

# design api return data:
  {
    "code": 200,
    "message": "Success",
    "data": {} 
  }
  200: Success
  400: Bad Request
  404: Not Found
  422: Validation Error
  429: Too Many Requests
  500: Internal Server Error
  
  if it is page
  {
    "code": 200,
    "message": "Success",
    "data": {
      "paginator": {
        "page_size": 10, // every page has 10 records
        "current_pate": 1, 
        "total_page": 10,
        "total_record": 100
      }
    }
  }

# env 
 1. os, dotenv
 dotenv.load_dotenv() # load .env file
    os.getenv("DATABASE_URL") # get env variable
 2. pydantic-settings + BaseSettings + lru_cache
   will auto load .env file and cache the settings object don't need to load .env file every time

# log config
In Python logging there are two independent filters for every log messag
It must pass both checks:
record.level >= logger.level
record.level >= handler.level

# router setup
# FastAPI initialize the router and include it in the main app
# error handling 
# docker install database postgres, redis, 
# configure database connection in .env file
# initialize database connection in the main app
 - use config to get database connection parameters in env file
 - create a database connection pool and store it in the app state
 - in main initialize this redis client and close it when the app shutdown
 - use the connection pool in the repository layer to execute database queries

# minio to replace aws s3 for file storage
操作	方法名	说明
Create	upload_file()	从本地路径上传
Create	upload_bytes()	直接上传 bytes 数据
Read	download_file()	下载到本地
Read	get_file()	获取 bytes 数据
Read	get_presigned_url()	生成临时访问链接
Read	list_files()	列出文件列表
Read	stat_file()	获取文件元信息
Update	copy_object()	复制/重命名文件
Delete	delete_file()	删除单个文件
Delete	delete_files()	批量删除

# Alembic 
1.ORM:
    class -> table
    Instance/object -> row
    Attribute -> column
2. Migration:
    - alembic init alembic
    - alembic.ini change sqlalchemy.url = driver://user:pass@localhost/dbname to your database connection string
       SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://spark:spark@localhost:5432/spark_db  for runtime ORM (async).
       sqlalchemy.url = postgresql+psycopg2://spark:spark@localhost:5432/spark_db for migration tooling (usually sync).
    - in __init__.py export the Base and models
     from .models import Base, User, Post
      __all__ = ["Base", "User", "Post"]
    - in alembic/env.py change target_metadata = None to
     from app.infrastructure.models import Base
      target_metadata = Base.metadata to your ORM base metadata
3. Create migration:
    - alembic revision --autogenerate -m "create demo table"
    - alembic upgrade head to apply the migration to the database
    - alembic downgrade -1/version to rollback the last migration
    - in main config automatically run the migration when the app starts
          alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
  

# psycopg2-binary for postgres database connection

# pytest and httpx for testing in development environment
- test file should be named test_*.py or *_test.py
- test function should be named test_*
- test class should be named Test* and not have __init__ method
- use assert statement to check the expected result
pytest test_app.py 
pytest test_app.py::TestUserAPI::test_create_user
pytest test_app.py::TestUserAPI::test_create_user
-v for verbose detail output
- s to show print statements in the test output
## fixture for setup and teardown
in conftest.py
## pytest with @pytest.mark.asyncio for async test functions
with @pytest.mark.parametrize to run the same test with different parameters

1 项目环境变量配置和通用开发
- 使用 pydantic-settings + BaseSettings + lru_cache 定义配置类，自动加载.env环境变量并进行类型验证
- 配置日志记录，使用 Python 的 logging 模块设置日志格式和级别
- 定义统一的 API 响应格式，包含 code、message 和 data 字段
- error handling，使用 FastAPI 的异常处理机制捕获和处理常见错误，返回统一的错误响应格式
- 使用 FastAPI 的 APIRouter 组织路由，保持代码结构清晰
- 完成 main.py 编写， 使用lifespan 管理项目的生命周期
2. Docker 容器化和数据库配置
- 编写 Dockerfile 定义应用的容器镜像，安装依赖并设置工作目录
- 使用 docker-compose.yml 定义服务，包含应用容器和数据库容器（redis，postgresql， minio）
- 配置数据库连接，使用环境变量传递数据库连接字符串
- 在应用启动时初始化数据库连接池，确保高效的数据库访问
3. alembic 数据库迁移和 pytest 测试配置