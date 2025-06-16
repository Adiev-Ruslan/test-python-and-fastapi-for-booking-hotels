from datetime import date

from pydantic import BaseModel
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from src.exceptions import RoomNotFoundException
from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.repos.utils import rooms_ids_for_booking
from src.repos.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper
from src.schemas.rooms import RoomAdd

from sqlalchemy import select
from sqlalchemy.orm import selectinload


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper
    schema = RoomAdd

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

    async def get_one_with_rels(self, **filter_by):
        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise RoomNotFoundException
        
        return RoomDataWithRelsMapper.map_to_domain_entity(model)
        