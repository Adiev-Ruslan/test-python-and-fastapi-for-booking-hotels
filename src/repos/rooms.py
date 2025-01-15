from pydantic import BaseModel

from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.schemas.rooms import Room

from fastapi import HTTPException

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, insert


class RoomsRepository(BaseRepository):
	model = RoomsOrm
	schema = Room
	
	async def add(self, data: BaseModel):
		try:
			add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
			result = await self.session.execute(add_data_stmt)
			model = result.scalars().one()
			return self.schema.model_validate(model, from_attributes=True)
		except IntegrityError:
			raise HTTPException(
				status_code=400,
				detail=f"Номер комнаты {data.room_num} уже существует в отеле {data.hotel_id}."
			)
	
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
				"room N": room.room_num,
				"status": "occupied" if room.is_occupied else "available",
			}
			for room in rooms
		]
	
