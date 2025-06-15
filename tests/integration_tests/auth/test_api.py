import pytest


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("k0t@pes.com", "1234", 200),
        ("k0t@pes.com", "1234", 409),
        ("k0t1@pes.com", "1235", 200),
        ("abcde", "1235", 422),
        ("abcde@abc", "1235", 422),
    ],
)
@pytest.mark.asyncio
async def test_full_auth_flow(email: str, password: str, status_code: int, ac):
    # 1. Тестирую регистрацию
    register_response = await ac.post("/auth/register", json={"email": email, "password": password})
    assert register_response.status_code == status_code
    if status_code != 200:
        return

    # 2. Тестирую логин
    login_response = await ac.post("/auth/login", json={"email": email, "password": password})
    assert login_response.status_code == 200
    assert ac.cookies["access_token"]
    assert "access_token" in login_response.json()

    # 3. Проверяю ручку /me
    me_response = await ac.get("/auth/me")
    assert me_response.status_code == 200
    user_data = me_response.json()
    assert user_data["email"] == email
    assert "id" in user_data
    assert "password" not in user_data
    assert "hashed_password" not in user_data

    # 4. Тестирую логаут
    logout_response = await ac.delete("/auth/logout")
    assert logout_response.status_code == 200
    assert "access_token" not in ac.cookies
    assert logout_response.json() == {"status": "OK"}
