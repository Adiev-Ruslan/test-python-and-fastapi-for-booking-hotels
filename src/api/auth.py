from fastapi import APIRouter, HTTPException, Response, Request

from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import UserAlreadyExistsException
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register", description="Ручка для аутентификации пользователя")
async def register_user(data: UserRequestAdd, db: DBDep):
    existing_user = await db.users.get_one_or_none(email=data.email)
    if existing_user:
        raise UserAlreadyExistsException()
    
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(
        email=data.email,
        hashed_password=hashed_password
    )
    
    try:
        await db.users.add(new_user_data)
        await db.commit()
    except Exception as e:  # noqa: E722
        raise HTTPException(
            status_code=400,
            detail="Ошибка при создании пользователя"
        )

    return {"status": "OK"}


@router.post("/login", description="Ручка для входа пользователя")
async def login_user(data: UserRequestAdd, response: Response, db: DBDep):
    user = await db.users.get_user_with_hashed_password(email=data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Пароль неверный")
    access_token = AuthService().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.delete("/logout")
async def logout_user(request: Request, response: Response):
    """
    Ручка для выхода из аккаунта
    """

    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=400, detail="Пользователь не был залогинен или сессия истекла"
        )

    response.delete_cookie("access_token")
    return {"status": "OK"}


@router.get("/me")
async def get_me(user_id: UserIdDep, db: DBDep):
    """
    Получает access_token из cookies пользователя.
    Если токен отсутствует, возвращает сообщение об ошибке.
    """

    user = await db.users.get_one_or_none(id=user_id)
    return user
