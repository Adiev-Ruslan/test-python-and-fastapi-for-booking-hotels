from fastapi import Query, APIRouter, Body
from sqlalchemy import insert

from src.database import async_session_maker, engine
from src.models.hotels import HotelsOrm
from src.schemas.hotels import Hotel, HotelPATCH
from src.api.dependencies import PaginationDep

router = APIRouter(prefix="/hotels", tags=["Отели"])

hotels = [
	{"id": 1, "title": "Sochi", "name": "sochi"},
	{"id": 2, "title": "Дубай", "name": "dubai"},
	{"id": 3, "title": "Мальдивы", "name": "maldivs"},
	{"id": 4, "title": "Геленджик", "name": "gelik"},
	{"id": 5, "title": "Москва", "name": "moscow"},
	{"id": 6, "title": "Казань", "name": "kazan"},
	{"id": 7, "title": "Гачи", "name": "gachi"},
]


@router.get(
	"",
	description="Получить в json-формате список всех отелей"
)
def get_hotels(
	pagination: PaginationDep,
	id: int | None = Query(None, description="Айдишник"),
	title: str | None = Query(None, description="Название отеля"),
):
	
	# Фильтруем отели по id и title
	hotels_ = [
		hotel for hotel in hotels
		if (not id or hotel["id"] == id) and (not title or hotel["title"] == title)
	]
	
	# Реализация пагинации через срезы
	page = pagination.page or 1  # Если page не передан, используем значение по умолчанию
	per_page = pagination.per_page or 3  # Если per_page не передан, используем значение по умолчанию
	start = (page - 1) * per_page
	end = start + per_page
	paginated_hotels = hotels_[start:end]
	
	# Возвращаем результат
	return {
		"total": len(hotels_),  # Общее количество отелей после фильтрации
		"page": page,  # Текущая страница
		"per_page": per_page,  # Количество отелей на странице
		"total_pages": (len(hotels_) + per_page - 1) // per_page,  # Всего страниц
		"data": paginated_hotels  # Список отелей на текущей странице
	}


@router.post("", description="Добавить в БД новый отель")
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
	"1": {"summary": "Сочи", "value": {
		"title": "Отель Сочи 5 звезд у моря",
		"location": "ул. Моря 1"
	}}})
):
	async with async_session_maker() as session:
		add_hotel_stmt = insert(HotelsOrm).values(**hotel_data.model_dump())
		print(add_hotel_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
		await session.execute(add_hotel_stmt)
		await session.commit()
	
	return {"status": "OK"}


@router.put(
	"/{hotel_id}",
	description="Изменить все данные отеля"
)
def change_all_data_in_hotels(hotel_id: int, hotel_data: Hotel):
	global hotels
	
	for hotel in hotels:
		if hotel["id"] == hotel_id:
			hotel.update(hotel_data)
			break
	else:
		return {"status": "Hotel not found"}
	
	return {"status": "OK"}


@router.patch(
	"/{hotel_id}",
	description="Изменить некоторые данные отеля"
)
def change_some_data_in_hotels(hotel_id: int, hotel_data: HotelPATCH):
	global hotels
	
	hotel = next((hotel for hotel in hotels if hotel["id"] == hotel_id), None)
	if not hotel:
		return {"status": "Hotel not found"}
		
	updated_data = hotel_data.dict(exclude_unset=True)
	hotel.update(updated_data)
	return {"status": "OK", "updated_data": hotel}
	
	# hotel = [hotel for hotel in hotels if hotel["id"] == hotel_id][0]
	# if hotel_data.title:
	# 	hotel["title"] = hotel_data.title
	# if hotel_data.name:
	# 	hotel["name"] = hotel_data.name
	# return {"status": "OK"}


@router.delete(
	"/{hotel_id}",
	description="Удалить отель из БД по его id"
)
def delete_hotel(hotel_id: int):
	global hotels
	for hotel in hotels:
		if hotel["id"] == hotel_id:
			hotels.remove(hotel)
			return {"status": "OK"}
	
	return {"status": "Hotel not found"}

