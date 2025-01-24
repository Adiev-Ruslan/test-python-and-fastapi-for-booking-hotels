from src.models.bookings import BookingsOrm
from src.repos.base import BaseRepository
from src.schemas.bookings import Booking


class BookingsRepository(BaseRepository):
	model = BookingsOrm
	schema = Booking
	