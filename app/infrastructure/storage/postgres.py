import logging
from functools import lru_cache
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

#from app.domain.repositories.uow import IUnitOfWork
# from app.infrastructure.repositories.db_uow import DBUnitOfWork
from core.config import get_settings

logger = logging.getLogger(__name__)

"""
The engine is the low-level database connection pool and DB interface.
It knows:
how to connect (URL, driver, host, port, DB name),
how to create DB connections,
how to manage connection pooling,
how to execute raw SQL (async_conn.execute(text("..."))).
A Session is the ORM’s unit of work:
it tracks ORM objects (mapped classes),
handles transactions,
lets you use ORM queries instead of raw sql,

Engine = one global per app (per DB URL)
Session factory = one global per engine
Session (from session_factory) = many short-lived, per-request objects
"""

class Postgres:
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._settings = get_settings()

    async def init(self) ->None:
        if self._engine is not None:
            logger.warning("Postgres engine is already initialized")
            return
        try:
            self._engine = create_async_engine(
                self._settings.sqlalchemy_database_uri,
                echo=True if self._settings.env == "development" else False,
                pool_pre_ping=True, # check connection before each request
            )
            self._session_factory = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            )
            logger.info("postgres engine created, testing connection...")
            async with self._engine.begin() as async_conn:
                await async_conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
                logger.info("uuid-ossp extension is ready")
        except Exception as e:
            logger.error(f"Postgres engine initialization failed: {e}")
            raise e

    async def shutdown(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Postgres engine shutdown complete")
        get_postgres.cache_clear()

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("Postgres engine is not initialized")
        return self._session_factory

@lru_cache()
def get_postgres() -> Postgres:
    """Get the Postgres instance (singleton)"""
    return Postgres()

async def get_db_session() -> AsyncSession:
    """Get a new database session"""
    postgres = get_postgres()
    session_factory = postgres.session_factory

    async with session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise e


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    postgres = get_postgres()
    return postgres.session_factory


