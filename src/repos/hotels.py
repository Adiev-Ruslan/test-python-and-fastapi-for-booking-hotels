from datetime import date

from sqlalchemy import select, func

from src.models.rooms import RoomsOrm
from src.models.hotels import HotelsOrm
from src.repos.base import BaseRepository
from src.repos.utils import rooms_ids_for_booking
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
	model = HotelsOrm
	schema = Hotel
	
	async def get_filtered_by_time(
		self,
		date_from: date,
		date_to: date,
		location: str | None = None,
		title: str | None = None,
		limit: int = 5,
		offset: int = 0
	):
		rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
		
		hotels_ids_to_get = (
			select(RoomsOrm.hotel_id)
			.select_from(RoomsOrm)
			.filter(RoomsOrm.id.in_(rooms_ids_to_get))
		)
		
		query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids_to_get))
		
		if location:
			query = query.filter(HotelsOrm.location.ilike(f"%{location}%"))
		if title:
			query = query.filter(HotelsOrm.title.ilike(f"%{title}%"))
		
		count_query = select(func.count()).filter(HotelsOrm.id.in_(hotels_ids_to_get))

		total_count = await self.session.execute(count_query)
		total_count = total_count.scalar_one()
		
		query = query.limit(limit).offset(offset)
		
		hotels = await self.session.execute(query)
		hotels = hotels.scalars().all()
	
		return {"total": total_count, "hotels": hotels}
		