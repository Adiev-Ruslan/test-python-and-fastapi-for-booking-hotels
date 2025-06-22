from datetime import date

from src.exceptions import (
	dates_are_fine, ObjectNotFoundException,
	HotelNotFoundException
)
from src.schemas.hotels import HotelAdd, HotelPATCH, Hotel
from src.services.base import BaseService


class HotelService(BaseService):
	async def get_hotels(
		self,
		pagination,
		location: str | None,
		title: str | None,
		date_from: date,
		date_to: date,
		only_with_bookings: bool = False
	):
		dates_are_fine(date_from, date_to)
		per_page = pagination.per_page or 5
		result = await self.db.hotels.get_all_with_optional_booking_filter(
			date_from=date_from,
			date_to=date_to,
			location=location,
			title=title,
			only_with_bookings=only_with_bookings,
			limit=per_page,
			offset=per_page * (pagination.page - 1),
		)
		
		return result
	
	async def get_hotel(self, hotel_id: int):
		return await self.db.hotels.get_one(id=hotel_id)
		
	async def create_hotel(self, data: HotelAdd):
		hotel = await self.db.hotels.add(data)
		await self.db.commit()
		return hotel
	
	async def change_all_data_in_hotel(self, hotel_id: int, data: HotelAdd):
		await self.db.hotels.edit(data, id=hotel_id)
		await self.db.commit()
		
	async def change_some_data_in_hotel(
		self,
		hotel_id: int,
		data: HotelPATCH,
		exclude_unset: bool = False
	):
		await self.db.hotels.edit(data, exclude_unset=exclude_unset, id=hotel_id)
		await self.db.commit()
		
	async def delete_hotel(self, hotel_id: int):
		await self.db.hotels.delete(id=hotel_id)
		await self.db.commit()
		
	async def get_hotel_with_check(self, hotel_id: int) -> Hotel:
		try:
			return await self.db.hotels.get_one(id=hotel_id)
		except ObjectNotFoundException:
			raise HotelNotFoundException

