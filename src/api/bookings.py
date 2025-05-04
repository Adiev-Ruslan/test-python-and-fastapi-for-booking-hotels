from fastapi import APIRouter, HTTPException

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd

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
async def create_booking(
	user_id: UserIdDep,
	db: DBDep,
	booking_data: BookingAddRequest
):
	"""Бронируем номер отеля с проверкой доступности"""
	
	try:
		room = await db.rooms.get_one_or_none(id=booking_data.room_id)
		
		booking_add = BookingAdd(
			user_id=user_id,
			price=room.price,
			**booking_data.model_dump()
		)
		
		booking = await db.bookings.add_booking(booking_add)
		await db.commit()
		return {"status": "OK", "data": booking}
	
	except (ValueError, AttributeError) as e:
		await db.rollback()
		raise HTTPException(status_code=400, detail=str(e))
		
