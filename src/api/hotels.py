from datetime import date

from fastapi import Query, APIRouter, Body, HTTPException
from fastapi_cache.decorator import cache

from src.schemas.hotels import HotelPATCH, HotelAdd
from src.api.dependencies import PaginationDep, DBDep
from src.exceptions import (
    dates_are_fine,
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
    dates_are_fine(date_from, date_to)
    per_page = pagination.per_page or 5

    result = await db.hotels.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
    )

    return result


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, db: DBDep):
    """Ручка для получения по id только одного конкретного отеля"""

    try:
        return await db.hotels.get_one(id=hotel_id)
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

    hotel = await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}")
async def change_all_data_in_hotel(hotel_id: int, hotel_data: HotelAdd, db: DBDep):
    """Изменить все данные отеля"""

    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.patch("/{hotel_id}")
async def change_some_data_in_hotel(hotel_id: int, hotel_data: HotelPATCH, db: DBDep):
    """Изменить некоторые данные отеля"""

    await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep):
    """Удалить отель из БД по его id"""

    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK"}
