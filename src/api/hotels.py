from datetime import date

from fastapi import Query, APIRouter, Body
from fastapi_cache.decorator import cache

from src.schemas.hotels import HotelPATCH, HotelAdd
from src.api.dependencies import PaginationDep, DBDep
from src.services.hotels import HotelService
from src.exceptions import (
    ObjectNotFoundException,
    HotelNotFoundHTTPException
)

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
@cache()
async def get_all_hotels(
    pagination: PaginationDep,
    db: DBDep,
    location: str | None = Query(None, description="Локация"),
    title: str | None = Query(None, description="Название отеля"),
    date_from: date = Query(example="2025-01-01"),
    date_to: date = Query(example="2025-01-30"),
):
    """Получит список всех гостиниц с датами бронирования"""
    
    return await HotelService(db).get_filtered_by_time(
        pagination,
        location,
        title,
        date_from,
        date_to
    )


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, db: DBDep):
    """Ручка для получения по id только одного конкретного отеля"""

    try:
        return await HotelService(db).get_hotel(hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException

    
@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {
                    "title": "Отель Сочи 5 звезд у моря",
                    "location": "ул. Моря 1",
                },
            }
        }
    ),
):
    """Добавить в БД новый отель"""

    hotel = await HotelService(db).create_hotel(hotel_data)
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}")
async def change_all_data_in_hotel(hotel_id: int, hotel_data: HotelAdd, db: DBDep):
    """Изменить все данные отеля"""

    await HotelService(db).change_all_data_in_hotel(hotel_id, hotel_data)
    return {"status": "OK"}


@router.patch("/{hotel_id}")
async def change_some_data_in_hotel(hotel_id: int, hotel_data: HotelPATCH, db: DBDep):
    """Изменить некоторые данные отеля"""
    
    await HotelService(db).change_some_data_in_hotel(
        hotel_id,
        hotel_data,
        exclude_unset=True
    )
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep):
    """Удалить отель из БД по его id"""

    await HotelService(db).delete_hotel(hotel_id)
    return {"status": "OK"}
