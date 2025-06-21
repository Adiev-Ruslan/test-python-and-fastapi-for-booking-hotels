from datetime import date

from sqlalchemy import select, func
from sqlalchemy.orm import aliased

from src.models.rooms import RoomsOrm
from src.models.hotels import HotelsOrm
from src.repos.base import BaseRepository
from src.repos.utils import rooms_ids_for_booking
from src.repos.mappers.mappers import HotelDataMapper


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelDataMapper

    async def get_all_with_optional_booking_filter(
        self,
        date_from: date,
        date_to: date,
        location: str | None = None,
        title: str | None = None,
        only_with_bookings: bool = False,
        limit: int = 5,
        offset: int = 0,
    ):
        hotel_alias = aliased(HotelsOrm)
        query = select(hotel_alias)
        
        if only_with_bookings:
            rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
            hotels_ids_to_get = (
                select(RoomsOrm.hotel_id)
                .filter(RoomsOrm.id.in_(rooms_ids_to_get))
            )
            query = query.filter(hotel_alias.id.in_(hotels_ids_to_get))
            count_query = (
                select(func.count())
               .filter(hotel_alias.id.in_(hotels_ids_to_get))
            )
        else:
            count_query = select(func.count()).select_from(hotel_alias)

        if location:
            query = query.filter(hotel_alias.location.ilike(f"%{location}%"))
            count_query = count_query.filter(hotel_alias.location.ilike(f"%{location}%"))
        if title:
            query = query.filter(hotel_alias.title.ilike(f"%{title}%"))
            count_query = count_query.filter(hotel_alias.title.ilike(f"%{title}%"))

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        total = await self.session.execute(count_query)
        
        hotels = [
            self.mapper.map_to_domain_entity(hotel)
            for hotel in result.scalars().all()
        ]

        return {"total": total.scalar_one(), "hotels": hotels}
