from datetime import date

from fastapi import APIRouter, HTTPException, Query

from src.api.dependencies import DBDep
from src.schemas.rooms import RoomAdd, RoomAddWithHotel, RoomPATCH

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_all_rooms(
	db: DBDep,
	hotel_id: int,
	date_from: date = Query(example="2025-02-01"),
	date_to: date = Query(example="2025-02-10")
):
	"""Получить список всех номеров отеля"""
	
	return await db.rooms.get_filtered_by_time(
		hotel_id=hotel_id,
		date_from=date_from,
		date_to=date_to
	)
	

@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(hotel_id: int, room_id: int, db: DBDep):
	"""Ручка для получения информации о конкретном номере по его id"""
	
	# Проверяю, что отель существует
	hotel = await db.hotels.get_one_or_none(id=hotel_id)
	if hotel is None:
		raise HTTPException(
			status_code=404,
			detail="Отель не найден"
		)
	
	# Проверяю существовать ли номер
	room = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
	if room is None:
		raise HTTPException(
			status_code=404,
			detail="Номер не найден или не принадлежит указанному отелю"
		)
	
	return {"status": "OK", "hotel_title": hotel.title, "room_data": room}


@router.post("/{hotel_id}/rooms")
async def create_room(db: DBDep, hotel_id: int, room_data: RoomAdd):
	"""Добавить в БД новый номер отеля"""
	
	hotel = await db.hotels.get_one_or_none(id=hotel_id)
	if hotel is None:
		raise HTTPException(status_code=404, detail=f"Отель с id {hotel_id} не найден")
	
	room_data_with_hotel = RoomAddWithHotel(**room_data.model_dump(), hotel_id=hotel_id)
	room = await db.rooms.add(room_data_with_hotel)
	await db.commit()
	
	return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def change_all_data_in_room(
	db: DBDep, hotel_id: int,
	room_id: int, room_data: RoomAdd
):
	"""Изменить все данные номера отеля"""
	
	await db.rooms.edit(room_data, id=room_id, hotel_id=hotel_id)
	await db.commit()
	return {"status": "OK"}
	
	
@router.patch("/{hotel_id}/rooms/{room_id}")
async def change_some_data_in_room(
	db: DBDep, hotel_id: int,
	room_id: int, room_data: RoomPATCH
):
	"""Изменить некоторые данные номера"""
	
	await db.rooms.edit(
		room_data, exclude_unset=True,
		id=room_id, hotel_id=hotel_id
	)
	await db.commit()
	return {"status": "OK"}
	
	
@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(db: DBDep, hotel_id: int, room_id: int):
	"""Удалить номер отеля из БД по его id"""
	
	await db.rooms.delete(id=room_id, hotel_id=hotel_id)
	await db.commit()
	return {"status": "OK"}
	
