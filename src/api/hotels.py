from fastapi import Query, APIRouter, Body

from src.repos.hotels import HotelsRepository
from src.database import async_session_maker
from src.schemas.hotels import Hotel, HotelPATCH
from src.api.dependencies import PaginationDep

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("", description="Получить в json-формате список всех отелей")
async def get_hotels(
	pagination: PaginationDep,
	title: str | None = Query(None, description="Часть названия отеля"),
	location: str | None = Query(None, description="Часть названия местоположения отеля")
):
	per_page = pagination.per_page or 5
	async with async_session_maker() as session:
		return await HotelsRepository(session).get_all(
			location=location,
			title=title,
			limit=per_page,
			offset=per_page * (pagination.page - 1)
		)
	
	
@router.post("", description="Добавить в БД новый отель")
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
	"1": {"summary": "Сочи", "value": {
		"title": "Отель Сочи 5 звезд у моря",
		"location": "ул. Моря 1"
	}}})
):
	async with async_session_maker() as session:
		hotel = await HotelsRepository(session).add(hotel_data)
		await session.commit()
	
	return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}", description="Изменить все данные отеля")
async def change_all_data_in_hotels(hotel_id: int, hotel_data: Hotel):
	async with async_session_maker() as session:
		await HotelsRepository(session).edit(hotel_data, id=hotel_id)
		await session.commit()
	return {"status": "OK"}


@router.patch("/{hotel_id}", description="Изменить некоторые данные отеля")
async def change_some_data_in_hotels(hotel_id: int, hotel_data: HotelPATCH):
	async with async_session_maker() as session:
		await HotelsRepository(session).edit(
			hotel_data,
			exclude_unset=True,
			id=hotel_id
		)
		await session.commit()
	return {"status": "OK"}
	
	
@router.delete("/{hotel_id}", description="Удалить отель из БД по его id")
async def delete_hotel(hotel_id: int):
	async with async_session_maker() as session:
		await HotelsRepository(session).delete(id=hotel_id)
		await session.commit()
	return {"status": "OK"}
	

