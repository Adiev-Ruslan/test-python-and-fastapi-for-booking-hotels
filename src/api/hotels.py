from fastapi import Query, APIRouter, Body, HTTPException

from src.schemas.hotels import HotelPATCH, HotelAdd
from src.api.dependencies import PaginationDep, DBDep

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_hotels(
	pagination: PaginationDep,
	db: DBDep,
	title: str | None = Query(None, description="Часть названия отеля"),
	location: str | None = Query(None, description="Часть названия местоположения отеля")
):
	"""Получить в json-формате список всех отелей"""
	
	per_page = pagination.per_page or 5
	return await db.hotels.get_all(
		location=location,
		title=title,
		limit=per_page,
		offset=per_page * (pagination.page - 1)
	)


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, db: DBDep):
	"""Ручка для получения по id только одного конкретного отеля"""
	
	hotel = await db.hotels.get_one_or_none(id=hotel_id)
	if hotel is None:
		raise HTTPException(status_code=404, detail="Нет такого отеля")
	
	return {"status": "OK", "data": hotel}
		
	
@router.post("")
async def create_hotel(
	db: DBDep,
	hotel_data: HotelAdd = Body(openapi_examples={
		"1": {"summary": "Сочи", "value": {
			"title": "Отель Сочи 5 звезд у моря",
			"location": "ул. Моря 1"
	}}})
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
	
