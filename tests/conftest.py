import os
from typing import AsyncGenerator
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlmodel import create_engine, SQLModel

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

global_settings = config.Settings()


@pytest.fixture(
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ]
)
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session", autouse=True)
def init_db():
    # create sync engine for alembic
    engine_sync = create_engine(global_settings.POSTGRES_TEST_URL)
    if not database_exists(engine_sync.url):
        create_database(engine_sync.url)

    # run migrations on test db
    alembic_config_file = os.path.join(global_settings.ROOT_DIR, "..", "alembic.ini")
    alembic_cfg = Config(alembic_config_file)
    alembic_cfg.set_main_option("sqlalchemy.url", global_settings.POSTGRES_TEST_URL)
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

    session = Session(engine_sync)

    # Add owner user
    user = UserFactory(id=OWNER_ID, email=OWNER_EMAIL)
    session.add(user)
    session.commit()
    at = AccessToken(token=OWNER_TOKEN, user_id=OWNER_ID)
    session.add(at)
    session.commit()


@pytest.fixture
def async_session_maker() -> sessionmaker:
    engine_async = create_async_engine(global_settings.POSTGRES_TEST_ASYNC_URL)
    return sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def async_session(async_session_maker) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def async_client(async_session) -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
    ) as async_client:
        app.dependency_overrides[get_async_session] = lambda: async_session

        yield async_client

@pytest.fixture
def db_session():
    engine_sync = create_engine(global_settings.POSTGRES_TEST_URL)
    yield Session(engine_sync)
