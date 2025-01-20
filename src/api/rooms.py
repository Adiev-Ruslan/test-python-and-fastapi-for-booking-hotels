from fastapi import APIRouter, Body, Query, HTTPException

from src.repos.hotels import HotelsRepository
from src.repos.rooms import RoomsRepository
from src.database import async_session_maker
from src.schemas.rooms import RoomAdd, RoomAddWithHotel, RoomPATCH

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(
	hotel_id: int,
	status: str | None = Query(None, description="available or occupied")
):
	"""Получить список всех номеров отеля с их статусом (свободные/занятые)"""
	
	async with async_session_maker() as session:
		hotels_repo = HotelsRepository(session)
		rooms_repo = RoomsRepository(session)
		
		# Проверка существования отеля
		if not await hotels_repo.exists(hotel_id):
			raise HTTPException(status_code=404, detail=f"Отель с id {hotel_id} не найден")
		
		rooms = await rooms_repo.get_by_hotel(hotel_id=hotel_id, status=status)
		return {"hotel_id": hotel_id, "rooms": rooms}


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(hotel_id: int, room_id: int):
	"""Ручка для получения информации о конкретном номере по его id"""
	
	async with async_session_maker() as session:
		rooms_repo = RoomsRepository(session)
		hotel_repo = HotelsRepository(session)
		
		# Проверяю, что отель существует
		hotel = await hotel_repo.get_one_or_none(id=hotel_id)
		if hotel is None:
			raise HTTPException(
				status_code=404,
				detail="Отель не найден"
			)
		
		# Проверяю существовать ли номер
		room = await rooms_repo.get_one_or_none(id=room_id, hotel_id=hotel_id)
		if room is None:
			raise HTTPException(
				status_code=404,
				detail="Номер не найден или не принадлежит указанному отелю"
			)
		
		return {"status": "OK", "hotel_title": hotel.title, "room_data": room}


@router.post("/{hotel_id}/rooms")
async def create_room(
	hotel_id: int,
	room_data: RoomAdd = Body(
		example={
			"room_num": 4,
			"room_type": "одноместный",
			"price": 500,
			"is_occupied": False
		}
	)
):
	"""Добавить в БД новый номер отеля"""
	
	room_data_with_hotel = RoomAddWithHotel(**room_data.model_dump(), hotel_id=hotel_id)
	
	async with async_session_maker() as session:
		rooms_repo = RoomsRepository(session)
		hotels_repo = HotelsRepository(session)
		
		# Проверка существования отеля
		if not await hotels_repo.exists(hotel_id):
			raise HTTPException(status_code=404, detail=f"Отель с id {hotel_id} не найден")
		
		try:
			room = await rooms_repo.add(room_data_with_hotel)
			await session.commit()
		except HTTPException as e:
			await session.rollback()
			raise e
		return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def change_all_data_in_room(hotel_id: int, room_id: int, room_data: RoomAdd):
	"""Изменить все данные номера отеля"""
	
	async with async_session_maker() as session:
		await RoomsRepository(session).edit(room_data, id=room_id, hotel_id=hotel_id)
		await session.commit()
	return {"status": "OK"}
	
	
@router.patch("/{hotel_id}/rooms/{room_id}")
async def change_some_data_in_room(hotel_id: int, room_id: int, room_data: RoomPATCH):
	"""Изменить некоторые данные номера"""
	
	async with async_session_maker() as session:
		await RoomsRepository(session).edit(
			room_data,
			exclude_unset=True,
			id=room_id,
			hotel_id=hotel_id
		)
		await session.commit()
	return {"status": "OK"}
	
	
@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int):
	"""Удалить номер отеля из БД по его id"""
	
	async with async_session_maker() as session:
		await RoomsRepository(session).delete(id=room_id, hotel_id=hotel_id)
		await session.commit()
		
	return {"status": "OK"}
	
	

