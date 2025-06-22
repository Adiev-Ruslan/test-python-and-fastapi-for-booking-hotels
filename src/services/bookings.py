from fastapi import HTTPException

from src.exceptions import (
	ObjectNotFoundException,
	RoomNotFoundHTTPException,
	AllRoomsAreBookedException
)
from src.schemas.bookings import BookingAddRequest, BookingAdd
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room


class BookingService:
	def __init__(self, db):
		self.db = db
		
	async def get_all(self):
		return await self.db.bookings.get_all()
	
	async def get_for_user(self, user_id: int):
		return await self.db.bookings.get_filtered(user_id=user_id)
	
	async def create_booking(
		self,
		user_id: int,
		booking_data: BookingAddRequest
	):
		try:
			room: Room = await self.db.rooms.get_one(id=booking_data.room_id)
		except ObjectNotFoundException:
			raise RoomNotFoundHTTPException
		
		hotel: Hotel = await self.db.hotels.get_one(id=room.hotel_id)
		room_price: int = room.price
		_booking_data = BookingAdd(
			user_id=user_id,
			price=room_price,
			**booking_data.dict()
		)
		
		try:
			booking = await self.db.bookings.add_booking(_booking_data, hotel_id=hotel.id)
		except AllRoomsAreBookedException as ex:
			raise HTTPException(status_code=409, detail=ex.detail)
		
		await self.db.commit()
		return booking

	