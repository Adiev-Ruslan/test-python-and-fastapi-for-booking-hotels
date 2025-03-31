import os
import pytest
import asyncio
from dotenv import load_dotenv

# Загружаем тестовый .env перед импортом config
os.environ["MODE"] = "TEST"
load_dotenv(".env-test")

from httpx import AsyncClient, ASGITransport
from src.config import settings
from src.database import Base, engine_null_pool
from src.models import *
from src.main import app

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
	assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
	async with engine_null_pool.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
		await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database):
	async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
		await ac.post(
			"/auth/register",
			json={
				"email": "kot@pes.com",
				"password": "1234"
			}
		)
