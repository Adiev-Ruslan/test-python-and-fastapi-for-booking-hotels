import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete

from src.api.dependencies import DBDep


@pytest.fixture(autouse=True)
async def cleanup_users(db):
	yield
	await db.session.execute(delete(db.users.model))
	await db.session.commit()
	
	
@pytest.mark.parametrize("email, password", [
	("test1@example.com", "password1"),
	("test2@example.com", "password2")
])
@pytest.mark.asyncio
async def test_full_auth_flow(
	ac: AsyncClient,
	db: DBDep,
	email: str,
	password: str
):
	
	# 1. Тестирую регистрацию
	register_response = await ac.post(
		"/auth/register",
		json={"email": email, "password": password}
	)
	assert register_response.status_code == status.HTTP_200_OK
	assert register_response.json() == {"status": "OK"}

	# 1.1. Проверяю повторную регистрацию
	duplicate_response = await ac.post(
			"/auth/register",
			json={"email": email, "password": password}
		)
	assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST

	# 2. Тестирую логин
	login_response = await ac.post(
		"/auth/login",
		json={"email": email, "password": password}
	)
	assert login_response.status_code == status.HTTP_200_OK
	assert "access_token" in login_response.json()

	# 2.1. Проверяю логин с неверным паролем
	wrong_login_response = await ac.post(
		"/auth/login",
		json={"email": email, "password": "wrong_password"}
	)
	assert wrong_login_response.status_code == status.HTTP_401_UNAUTHORIZED
	assert wrong_login_response.json()["detail"] == "Пароль неверный"

	# 3. Проверяю ручку /me
	me_response = await ac.get("/auth/me")
	assert me_response.status_code == status.HTTP_200_OK
	user_data = me_response.json()
	assert user_data["email"] == email
	assert "id" in user_data
	
	# 4. Тестирую логаут
	logout_response = await ac.delete("/auth/logout")
	assert logout_response.status_code == status.HTTP_200_OK
	assert logout_response.json() == {"status": "OK"}

	# 5. Проверяю доступ после логаута
	me_response_after_logout = await ac.get("/auth/me")
	assert me_response_after_logout.status_code == status.HTTP_401_UNAUTHORIZED

	# 6. Проверяю логаут без токена
	logout_no_token_response = await ac.delete("/auth/logout")
	assert logout_no_token_response.status_code == status.HTTP_400_BAD_REQUEST
	assert logout_no_token_response.json()["detail"] == "Пользователь не был залогинен или сессия истекла"


