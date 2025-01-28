from fastapi import APIRouter, Depends

from src.models.users import UsersOrm
from src.api.dependencies import get_current_user_id
from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("")
async def get_all_bookings(db: DBDep):
	"""Получить все бронирования"""
	bookings = await db.bookings.get_all()
	return {"status": "OK", "bookings": bookings}


@router.get("/me")
async def get_authorized_bookings(
	db: DBDep,
	current_user: UsersOrm = Depends(get_current_user_id)
):
	"""Получить бронирования авторизованного пользователя"""
	bookings = await db.bookings.get_by_user_id(user_id=current_user.id)
	return bookings


@router.post("")
async def create_booking(
	user_id: UserIdDep,
	db: DBDep,
	booking_data: BookingAddRequest
):
	"""Бронируем номер отеля"""
	
	room = await db.rooms.get_one_or_none(id=booking_data.room_id)
	room_price: int = room.price
	_booking_data = BookingAdd(
		user_id=user_id,
		price=room_price,
		**booking_data.model_dump()
	)
	booking = await db.bookings.add(_booking_data)
	await db.commit()
	return {"status": "OK", "data": booking}
