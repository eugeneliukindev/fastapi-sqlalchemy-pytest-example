import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from src.config import settings
from src.core.models import Base
from src.main import app
from tests.model_factories import ALL_FACTORIES
from _pytest.monkeypatch import MonkeyPatch
import pytest
from src.database.manager import DatabaseManager

test_db_manager = DatabaseManager(url=settings.db.url, poolclass=NullPool)


async def _create_all_tables():
    async with test_db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _drop_all_tables():
    async with test_db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _truncate_all_tables():
    tables = Base.metadata.sorted_tables
    async with test_db_manager.engine.begin() as conn:
        for table in reversed(tables):
            await conn.execute(
                text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE")
            )


@pytest.fixture(autouse=True)
def _monkeypatch_session(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("src.database.manager", test_db_manager)
    yield


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _setup_database():
    await _drop_all_tables()
    await _create_all_tables()
    yield


@pytest.fixture(autouse=True)
def _inject_session_to_factories(session):
    for factory in ALL_FACTORIES:
        factory._meta.sqlalchemy_session = session
    yield


@pytest_asyncio.fixture(autouse=True)
async def _cleanup_database():
    yield
    await _truncate_all_tables()


@pytest_asyncio.fixture
async def session():
    async with test_db_manager.session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
