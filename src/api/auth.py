from fastapi import APIRouter, HTTPException, Response, Request

from src.repos.users import UsersRepository
from src.database import async_session_maker
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register", description="Ручка для аутентификации пользователя")
async def register_user(data: UserRequestAdd):
	hashed_password = AuthService().hash_password(data.password)
	new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
	async with async_session_maker() as session:
		await UsersRepository(session).add(new_user_data)
		await session.commit()
		
	return {"status": "OK"}


@router.post("/login", description="Ручка для входа пользователя")
async def login_user(data: UserRequestAdd, response: Response):
	async with async_session_maker() as session:
		user = await UsersRepository(session).get_user_with_hashed_password(email=data.email)
		if not user:
			raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")
		if not AuthService().verify_password(data.password, user.hashed_password):
			raise HTTPException(status_code=401, detail="Пароль неверный")
		access_token = AuthService().create_access_token({"user_id": user.id})
		response.set_cookie("access_token", access_token)
		return {"access_token": access_token}
	

@router.get("/only_auth")
async def only_auth(request: Request):
	"""
	Получает access_token из cookies пользователя.
	Если токен отсутствует, возвращает сообщение об ошибке.
	"""
	
	access_token = request.cookies.get("access_token")
	if not access_token:
		raise HTTPException(
			status_code=401,
			detail="access-token отсутствует, либо пользователь не вошел(не зарегистрирован)"
		)
	
	return {"access_token": access_token}
	
	