from fastapi import HTTPException
from sqlalchemy import select, func
from datetime import date

from src.models.bookings import BookingsOrm
from src.repos.base import BaseRepository
from src.schemas.bookings import Booking, BookingAdd
from src.repos.mappers.mappers import BookingDataMapper
from src.repos.utils import rooms_ids_for_booking


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self):
        query = select(BookingsOrm).filter(BookingsOrm.date_from == date.today())
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def get_all(self):
        query = select(self.model)

        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar()

        result = await self.session.execute(query)
        bookings = [
            Booking.model_validate(booking, from_attributes=True)
            for booking in result.scalars().all()
        ]

        return {"bookings": bookings, "total_count": total_count}

    async def add_booking(self, data: BookingAdd, hotel_id: int):
        rooms_ids_to_get = rooms_ids_for_booking(
            date_from=data.date_from, date_to=data.date_to, hotel_id=hotel_id
        )

        rooms_ids_to_book_res = await self.session.execute(rooms_ids_to_get)
        rooms_ids_to_book: list[int] = rooms_ids_to_book_res.scalars().all()

        if data.room_id in rooms_ids_to_book:
            new_booking = await self.add(data)
            return new_booking
        else:
            raise HTTPException(500)
