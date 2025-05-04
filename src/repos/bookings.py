from sqlalchemy import select, func
from datetime import date

from src.models import RoomsOrm
from src.models.bookings import BookingsOrm
from src.repos.base import BaseRepository
from src.schemas.bookings import Booking, BookingAdd
from src.repos.mappers.mappers import BookingDataMapper


class BookingsRepository(BaseRepository):
	model = BookingsOrm
	mapper = BookingDataMapper
	
	async def get_bookings_with_today_checkin(self):
		query = (
			select(BookingsOrm)
			.filter(BookingsOrm.date_from == date.today())
		)
		res = await self.session.execute(query)
		return [
			self.mapper.map_to_domain_entity(booking)
			for booking in res.scalars().all()
		]
	
	async def get_all(self):
		query = select(self.model)

		count_query = select(func.count()).select_from(query.subquery())
		total_count_result = await self.session.execute(count_query)
		total_count = total_count_result.scalar()

		result = await self.session.execute(query)
		bookings = [
			Booking.model_validate(booking, from_attributes=True)
			for booking in result.scalars().all()
		]

		return {"bookings": bookings, "total_count": total_count}

	async def add_booking(self, booking_data: BookingAdd):
		room = await self.session.get(RoomsOrm, booking_data.room_id)
		if not room:
			raise ValueError("Номер не найден")

		query = (
			select(func.count())
			.select_from(BookingsOrm)
			.where(
				BookingsOrm.room_id == booking_data.room_id,
				BookingsOrm.date_from <= booking_data.date_to,
				BookingsOrm.date_to >= booking_data.date_from,
			)
		)
		if await self.session.scalar(query) >= 1:
			raise ValueError("Номер уже забронирован на указанные даты")

		new_booking = BookingsOrm(**booking_data.model_dump())
		self.session.add(new_booking)
		await self.session.flush()
		return Booking.model_validate(new_booking)
	