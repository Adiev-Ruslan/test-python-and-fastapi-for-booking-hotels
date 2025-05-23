# ruff: noqa: E402

from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

import json
import os
import pytest
import asyncio
from dotenv import load_dotenv
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient, ASGITransport

# Загружаем тестовый .env перед импортом config
os.environ["MODE"] = "TEST"
load_dotenv(".env-test")

from src.api.dependencies import get_db
from src.config import settings
from src.database import Base, engine_null_pool, async_session_maker_null_pool
from src.models import *  # noqa
from src.main import app
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager

settings.MODE = "TEST"  # Принудительно устанавливаем


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop на всю сессию, чтобы избежать ScopeMismatch."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    print(f"DEBUG: settings.MODE = {settings.MODE}")
    print(f"DEBUG: settings.DB_URL = {settings.DB_URL}")
    assert settings.MODE == "TEST"


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> DBManager:
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open("tests/mock_hotels.json", encoding="utf-8") as f:
        hotels_data = json.load(f)

    with open("tests/mock_rooms.json", encoding="utf-8") as f:
        rooms_data = json.load(f)

    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels_data]
    rooms = [RoomAdd.model_validate(room) for room in rooms_data]

    async with DBManager(session_factory=async_session_maker_null_pool) as _db:
        await _db.hotels.add_bulk(hotels)
        await _db.rooms.add_bulk(rooms)
        await _db.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncClient:
    FastAPICache.init(InMemoryBackend())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(ac, setup_database):
    await ac.post("/auth/register", json={"email": "kot@pes.com", "password": "1234"})


@pytest.fixture
async def authenticated_ac(ac) -> AsyncClient:
    login_response = await ac.post("/auth/login", json={"email": "kot@pes.com", "password": "1234"})

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    yield ac
