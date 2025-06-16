from datetime import date

from fastapi import APIRouter, HTTPException, Query, Body

from src.api.dependencies import DBDep
from src.schemas.rooms import RoomAddRequest, RoomPatchRequest
from src.exceptions import HotelNotFoundHTTPException, HotelNotFoundException

from src.services.rooms import RoomService

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_all_rooms(
    db: DBDep,
    hotel_id: int,
    date_from: date = Query(example="2025-02-01"),
    date_to: date = Query(example="2025-02-10"),
):
    """Получить список всех номеров отеля"""

    return await RoomService(db).get_all_rooms(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(hotel_id: int, room_id: int, db: DBDep):
    """Ручка для получения информации о конкретном номере по его id"""

    # Проверяю, что отель существует
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Отель не найден")

    # Проверяю существовать ли номер
    room = await db.rooms.get_room_by_id_with_facilities(room_id=room_id, hotel_id=hotel_id)
    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Номер не найден или не принадлежит указанному отелю",
        )

    return {"status": "OK", "hotel_title": hotel.title, "room_data": room}


@router.post("/{hotel_id}/rooms")
async def create_room(hotel_id: int, db: DBDep, room_data: RoomAddRequest = Body()):
    """Добавить в БД новый номер отеля"""

    try:
        room = await RoomService(db).create_room(hotel_id, room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException

    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def change_all_data_in_room(
    db: DBDep, hotel_id: int, room_id: int, room_data: RoomAddRequest
):
    """Изменить все данные номера отеля"""
    
    await RoomService(db).change_all_data_in_room(hotel_id, room_id, room_data)
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def change_some_data_in_room(
    db: DBDep, hotel_id: int, room_id: int, room_data: RoomPatchRequest
):
    """Изменить некоторые данные номера"""
    
    await RoomService(db).change_some_data_in_room(hotel_id, room_id, room_data)
    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(db: DBDep, hotel_id: int, room_id: int):
    """Удалить номер отеля из БД по его id"""
    
    await RoomService(db).delete_room(hotel_id, room_id)
    return {"status": "OK"}
