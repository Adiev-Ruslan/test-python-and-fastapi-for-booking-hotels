import json
import os
import pytest
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

# Загружаем тестовый .env перед импортом config
os.environ["MODE"] = "TEST"
load_dotenv(".env-test")

from httpx import AsyncClient, ASGITransport
from src.config import settings
from src.database import Base, engine_null_pool, async_session_maker
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

	async with async_session_maker() as session:
		await insert_mock_data(session)


async def insert_mock_data(session: AsyncSession):
	"""Заполняет тестовую БД мок-данными"""
	
	with open("tests/mock_hotels.json", encoding="utf-8") as f:
		hotels_data = json.load(f)
		
	with open("tests/mock_rooms.json", encoding="utf-8") as f:
		rooms_data = json.load(f)
		
	hotels = [HotelsOrm(**hotel) for hotel in hotels_data]
	session.add_all(hotels)
	await session.flush()
	
	rooms = [RoomsOrm(**room) for room in rooms_data]
	session.add_all(rooms)
	
	await session.commit()


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
