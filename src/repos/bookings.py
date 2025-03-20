from sqlalchemy import select, func
from datetime import date

from src.models.bookings import BookingsOrm
from src.repos.base import BaseRepository
from src.schemas.bookings import Booking
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
