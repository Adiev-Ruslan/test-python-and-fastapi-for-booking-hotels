from fastapi import Query, APIRouter, Body
from sqlalchemy import insert, select, func

from src.repos.hotels import HotelsRepository
from src.database import async_session_maker, engine
from src.models.hotels import HotelsOrm
from src.schemas.hotels import Hotel, HotelPATCH
from src.api.dependencies import PaginationDep

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("", description="Получить в json-формате список всех отелей")
async def get_hotels(
	pagination: PaginationDep,
	title: str | None = Query(None, description="Часть названия отеля"),
	location: str | None = Query(None, description="Часть названия местоположения отеля")
):
	async with async_session_maker() as session:
		return await HotelsRepository(session).get_all()
	
	# per_page = pagination.per_page or 5
	# async with async_session_maker() as session:
	# 	query = select(HotelsOrm)
	# 	if title:
	# 		query = query.filter(HotelsOrm.title.ilike(f"%{title}%"))
	# 	if location:
	# 		query = query.filter(HotelsOrm.location.ilike(f"%{location}%"))
	#
	# 	# Запрос для подсчета общего количества записей
	# 	count_query = select(func.count()).select_from(query.subquery())
	# 	total_count_result = await session.execute(count_query)
	# 	total_count = total_count_result.scalar()
	#
	# 	# Запрос с пагинацией
	# 	paginated_query = (
	# 		query
	# 		.limit(per_page)
	# 		.offset(per_page * (pagination.page - 1))
	# 	)
	# 	print(query.compile(compile_kwargs={"literal_binds": True}))
	# 	result = await session.execute(paginated_query)
	# 	hotels = result.scalars().all()
	#
	# return {"hotels": hotels, "total_count": total_count}
	

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

