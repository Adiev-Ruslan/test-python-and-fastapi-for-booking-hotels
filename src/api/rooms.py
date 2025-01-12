from fastapi import APIRouter, Body, Query

from src.repos.rooms import RoomsRepository
from src.database import async_session_maker
from src.schemas.rooms import RoomAdd, RoomPATCH

router = APIRouter(prefix="/rooms", tags=["Номера"])


@router.get("/{hotel_id}")
async def get_rooms(
	hotel_id: int,
	status: str | None = Query(None, description="Свободен/занят")
):
	"""Получить список всех номеров отеля с их статусом (свободные/занятые)"""
	
	async with async_session_maker() as session:
		rooms_repo = RoomsRepository(session)
		rooms = await rooms_repo.get_by_hotel(hotel_id=hotel_id, status=status)
		
	return {"hotel_id": hotel_id, "rooms": rooms}
	

@router.get("/hotels/{hotel_id}/{room_id}")
async def get_room(room_id: int):
	"""Ручка для получения по id только одного конкретного номера отеля"""


@router.post("/hotels")
async def create_room(room_data: RoomAdd = Body(openapi_examples={
	"1": {"summary": "Удобства номера", "value": {
		"кровати": "одна двухспальная",
		"meals": "завтрак, обед и ужин",
		"кондиционер": "да"
	}}})
):
	"""Добавить в БД новый номер отеля"""


@router.put("/hotels/{room_id}")
async def change_all_data_in_room(room_id: int, room_data: RoomAdd):
	"""Изменить все данные номера отеля"""
	
	
@router.patch("/hotels/{room_id}")
async def change_some_data_in_room(room_id: int, room_data: RoomPATCH):
	"""Изменить некоторые данные номера"""
	
	
@router.delete("/hotels/{room_id}")
async def delete_room(room_id: int):
	"""Удалить номер отеля из БД по его id"""

