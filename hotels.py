from fastapi import Query, APIRouter, Body, Depends
from schemas.hotels import Hotel, HotelPATCH
from dependencies import PaginationDep

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


"""@router.get(
	"",
	description="Получить в json-формате список всех отелей"
)
def get_hotels(
	id: int | None = Query(None, description="Айдишник"),
	title: str | None = Query(None, description="Название отеля"),
	pagination: PaginationDep = Depends()  # Используем зависимость для пагинации
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
"""

@router.get(
	"",
	description="Получить в json-формате список всех отелей (либо некоторые из них)"
)
def get_hotels(
	pagination: PaginationDep,
	id: int | None = Query(None, description="Айдишник"),
	title: str | None = Query(None, description="Название отеля"),
):
	
	hotels_ = []
	for hotel in hotels_:
		if id and hotel["id"] != id:
			continue
		if title and hotel["title"] != title:
			continue
		hotels_.append(hotel)

	if pagination.page and pagination.per_page:
		return hotels_[pagination.per_page * (pagination.page-1):][:pagination.per_page]
	return hotels_


@router.post("", description="Добавить в БД новый отель")
def create_hotel(hotel_data: Hotel = Body(openapi_examples={
	"1": {"summary": "Сочи", "value": {
		"title": "Отель Сочи 5 звезд у моря",
		"name": "sochi-u-morya"
	}}})
):
	global hotels
	hotels.append({
		"id": hotels[-1]["id"] + 1,
		"title": hotel_data.title,
		"name": hotel_data.name,
	})
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

