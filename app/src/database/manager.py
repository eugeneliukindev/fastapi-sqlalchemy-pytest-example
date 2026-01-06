from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import settings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


class DatabaseManager:
    def __init__(self, url: str | URL, **engine_kw: Any):
        self.engine: AsyncEngine = create_async_engine(url=url, **engine_kw)
        self._session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        self.session_factory = asynccontextmanager(self.session_getter)

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_maker() as session:
            try:
                yield session
                await session.commit()
            except BaseException:
                await session.rollback()
                raise


db_manager = DatabaseManager(url=settings.db.url)
