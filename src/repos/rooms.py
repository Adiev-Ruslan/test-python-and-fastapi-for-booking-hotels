from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository


class RoomsRepository(BaseRepository):
	model = RoomsOrm
