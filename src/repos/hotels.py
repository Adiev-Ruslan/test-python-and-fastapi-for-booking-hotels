from datetime import date

from sqlalchemy import func, select

from src.models.rooms import RoomsOrm
from src.models.hotels import HotelsOrm
from src.repos.base import BaseRepository
from src.repos.utils import rooms_ids_for_booking
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
	model = HotelsOrm
	schema = Hotel
	
	async def get_all(self, location, title, limit, offset):
		query = select(HotelsOrm)
		if title:
			query = query.filter(HotelsOrm.title.ilike(f"%{title}%"))
		if location:
			query = query.filter(HotelsOrm.location.ilike(f"%{location}%"))
		
		# Запрос для подсчета общего количества записей
		count_query = select(func.count()).select_from(query.subquery())
		total_count_result = await self.session.execute(count_query)
		total_count = total_count_result.scalar()
		
		# Запрос с пагинацией
		paginated_query = (
			query
			.limit(limit)
			.offset(offset)
		)
		
		print(query.compile(compile_kwargs={"literal_binds": True}))
		result = await self.session.execute(paginated_query)
		hotels = [
			Hotel.model_validate(hotel, from_attributes=True)
			for hotel in result.scalars().all()
		]

		return {"hotels": hotels, "total_count": total_count}
	
	async def get_filtered_by_time(
		self,
		date_from: date,
		date_to: date,
	):
		rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
		hotels_ids_to_get = (
			select(RoomsOrm.hotel_id)
			.select_from(RoomsOrm)
			.filter(RoomsOrm.id.in_(rooms_ids_to_get))
		)
		return await self.get_filtered(HotelsOrm.id.in_(hotels_ids_to_get))
	