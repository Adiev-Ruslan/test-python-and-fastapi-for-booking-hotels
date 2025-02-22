from datetime import date

from pydantic import BaseModel
from fastapi import HTTPException

from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.repos.utils import rooms_ids_for_booking
from src.repos.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload


class RoomsRepository(BaseRepository):
	model = RoomsOrm
	mapper = RoomDataMapper
	
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
	
	async def get_filtered_by_time(self, hotel_id: int, date_from: date, date_to: date):
		rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)
		query = (
			select(self.model)
			.options(selectinload(self.model.facilities))
			.filter(RoomsOrm.id.in_(rooms_ids_to_get))
		)
		result = await self.session.execute(query)
		return [
			RoomDataWithRelsMapper.map_to_domain_entity(model)
			for model in result.unique().scalars().all()
		]

	async def get_room_by_id_with_facilities(self, room_id: int, hotel_id: int):
		query = (
			select(self.model)
			.options(selectinload(self.model.facilities))
			.filter_by(id=room_id, hotel_id=hotel_id)
		)
		result = await self.session.execute(query)
		room = result.scalars().first()
		
		if not room:
			return None
		
		return RoomDataWithRelsMapper.map_to_domain_entity(room)
		