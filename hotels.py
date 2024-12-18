from fastapi import Query, APIRouter
from schemas.hotels import Hotel, HotelPATCH

router = APIRouter(prefix="/hotels", tags=["Отели"])

hotels = [
	{"id": 1, "title": "Sochi", "name": "sochi"},
	{"id": 2, "title": "Дубай", "name": "dubai"},
]


@router.get(
	"",
	description="Получить в json-формате список всех отелей"
)
def get_hotels(
	id: int | None = Query(None, description="Айдишник"),
	title: str | None = Query(None, description="Название отеля"),
):
	hotels_ = []
	for hotel in hotels:
		if id and hotel["id"] != id:
			continue
		if title and hotel["title"] != title:
			continue
		hotels_.append(hotel)
	return hotels_


@router.post("", description="Добавить в БД новый отель")
def create_hotel(hotel_data: Hotel):
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

