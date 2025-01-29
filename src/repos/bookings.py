from sqlalchemy import select

from src.models.bookings import BookingsOrm
from src.repos.base import BaseRepository
from src.schemas.bookings import Booking


class BookingsRepository(BaseRepository):
	model = BookingsOrm
	schema = Booking
	
	async def get_all(self):
		query = select(self.model)
		result = await self.session.execute(query)
		return result.scalars().all()
	
