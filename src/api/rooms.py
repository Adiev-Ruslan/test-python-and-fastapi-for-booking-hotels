from fastapi import APIRouter, Body, Query, HTTPException

from src.repos.hotels import HotelsRepository
from src.repos.rooms import RoomsRepository
from src.database import async_session_maker
from src.schemas.rooms import RoomAdd, RoomAddWithHotel

router = APIRouter(prefix="/rooms", tags=["Номера"])


@router.get("/{hotel_id}")
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
	

@router.get("/hotels/{hotel_id}/{room_id}")
async def get_room(room_id: int):
	"""Ручка для получения по id только одного конкретного номера отеля"""


@router.post("/{hotel_id}")
async def create_room(
	hotel_id: int,
	room_data: RoomAdd = Body(
		example={
			"room_num": 4,
			"room_type": "одноместный",
			"price": 500,
			"quantity": 30,
			"is_occupied": False
		}
	)
):
	"""Добавить в БД новый номер отеля"""
	
	room_data_with_hotel = RoomAddWithHotel(**room_data.model_dump(), hotel_id=hotel_id)
	
	async with async_session_maker() as session:
		rooms_repo = RoomsRepository(session)
		try:
			room = await rooms_repo.add(room_data_with_hotel)
			await session.commit()
		except HTTPException as e:
			await session.rollback()
			raise e
		return {"status": "OK", "data": room}


@router.put("/hotels/{room_id}")
async def change_all_data_in_room(room_id: int, room_data: RoomAdd):
	"""Изменить все данные номера отеля"""
	
	
@router.patch("/hotels/{room_id}")
async def change_some_data_in_room(room_id: int, room_data: RoomAddWithHotel):
	"""Изменить некоторые данные номера"""
	
	
@router.delete("/hotels/{room_id}")
async def delete_room(room_id: int):
	"""Удалить номер отеля из БД по его id"""

