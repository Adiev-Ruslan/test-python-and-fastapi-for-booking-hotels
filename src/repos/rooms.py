from pydantic import BaseModel
from fastapi import HTTPException

from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.schemas.rooms import Room

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
	
	async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
		# Получаем ID номера и ID отеля из фильтров или данных
		room_id = filter_by.get("id")
		if room_id is None:
			raise ValueError("Не указан ID для редактирования номера")
		
		# Извлекаем hotel_id из данных
		hotel_id = data.hotel_id if hasattr(data, "hotel_id") else None
		
		# Если hotel_id отсутствует в данных, получаем его из текущего номера
		if not hotel_id:
			current_room = await self.get_one_or_none(id=room_id)
			if not current_room:
				raise HTTPException(status_code=404, detail="Номер не найден")
			hotel_id = current_room.hotel_id
		
		# Проверяем уникальность room_num в рамках hotel_id
		if hasattr(data, "room_num") and data.room_num is not None:
			existing_room_query = select(self.model).where(
				self.model.room_num == data.room_num,
				self.model.hotel_id == hotel_id,
				self.model.id != room_id  # Исключаем текущий номер
			)
			existing_room = (await self.session.execute(existing_room_query)).scalars().first()
			
			if existing_room:
				raise HTTPException(
					status_code=400,
					detail="Такой номер уже существует в рамках этого отеля"
				)
		
		# Обновляем данные номера
		await super().edit(data, exclude_unset=exclude_unset, **filter_by)
	
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
	
