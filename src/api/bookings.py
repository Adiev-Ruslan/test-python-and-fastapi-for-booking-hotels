from fastapi import APIRouter

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("")
async def get_all_bookings(db: DBDep):
    """Получить все бронирования"""
    bookings = await BookingService(db).get_all()
    return {"status": "OK", "bookings": bookings}


@router.get("/me")
async def get_authorized_bookings(user_id: UserIdDep, db: DBDep):
    """Получить бронирования авторизованного пользователя"""
    bookings = await BookingService(db).get_for_user(user_id)
    return {"status": "OK", "bookings": bookings}


@router.post("")
async def create_booking(
    user_id: UserIdDep,
    db: DBDep,
    booking_data: BookingAddRequest
):
    """Бронируем номер отеля с проверкой доступности"""
    booking = await BookingService(db).create_booking(user_id, booking_data)
    return {"status": "OK", "data": booking}
