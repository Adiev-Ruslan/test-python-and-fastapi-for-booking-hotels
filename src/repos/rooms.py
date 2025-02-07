from datetime import date

from pydantic import BaseModel
from fastapi import HTTPException

from src.database import engine
from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.schemas.rooms import Room

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, insert, func


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
		rooms_count = (
			select(BookingsOrm.room_id, func.count("*").label("rooms_booked"))
			.select_from(BookingsOrm)
			.filter(
				BookingsOrm.date_from <= date_to,
				BookingsOrm.date_to >= date_from
			)
			.group_by(BookingsOrm.room_id)
			.cte(name="rooms_count")
		)
		
		rooms_left_table = (
			select(
				RoomsOrm.id.label("room_id"),
				(RoomsOrm.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left"),
			)
			.select_from(RoomsOrm)
			.outerjoin(rooms_count, RoomsOrm.id == rooms_count.c.room_id)
			.cte(name="rooms_left_table")
		)
		
		rooms_ids_for_hotel = (
			select(RoomsOrm.id)
			.select_from(RoomsOrm)
			.filter_by(hotel_id=hotel_id)
			.subquery(name="rooms_ids_for_hotel")
		)
		
		rooms_ids_to_get = (
			select(rooms_left_table.c.room_id)
			.select_from(rooms_left_table)
			.filter(
				rooms_left_table.c.rooms_left > 0,
				rooms_left_table.c.room_id.in_(rooms_ids_for_hotel)
			)
		)
		
		# print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))

		return await self.get_filtered(RoomsOrm.id.in_(rooms_ids_to_get))
		