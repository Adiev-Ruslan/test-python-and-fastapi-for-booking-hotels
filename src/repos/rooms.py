from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.schemas.rooms import Room

from sqlalchemy import select


class RoomsRepository(BaseRepository):
	model = RoomsOrm
	schema = Room
	
	async def get_by_hotel(
		self,
		hotel_id: int,
		status: str | None
	):
		"""Получить список номеров для указанного отеля с возможностью фильтрации по статусу"""
		
		query = select(self.model).where(self.model.hotel_id == hotel_id)
		
		if status == "available":
			query = query.where(self.model.is_occupied == False)
		elif status == "occupied":
			query = query.where(self.model.is_occupied == True)
		
		result = await self.session.execute(query)
		rooms = result.scalars().all()
		
		return [
			{
				"id": room.id,
				"title": room.title,
				"status": "occupied" if room.is_occupied else "available",
			}
			for room in rooms
		]
	
