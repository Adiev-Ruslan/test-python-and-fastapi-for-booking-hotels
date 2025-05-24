from fastapi import APIRouter, HTTPException

from src.exceptions import ObjectNotFoundException
from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("")
async def get_all_bookings(db: DBDep):
    """Получить все бронирования"""
    bookings = await db.bookings.get_all()
    return {"status": "OK", "bookings": bookings}


@router.get("/me")
async def get_authorized_bookings(user_id: UserIdDep, db: DBDep):
    """Получить бронирования авторизованного пользователя"""
    return await db.bookings.get_filtered(user_id=user_id)


@router.post("")
async def create_booking(user_id: UserIdDep, db: DBDep, booking_data: BookingAddRequest):
    """Бронируем номер отеля с проверкой доступности"""

    try:
        room: Room = await db.rooms.get_one(id=booking_data.room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=400, detail="Номер не найден")
    
    hotel: Hotel = await db.hotels.get_one(id=room.hotel_id)
    room_price: int = room.price
    _booking_data = BookingAdd(
        user_id=user_id,
        price=room_price,
        **booking_data.dict()
    )

    booking = await db.bookings.add_booking(_booking_data, hotel_id=hotel.id)
    await db.commit()
    return {"status": "OK", "data": booking}
