from datetime import date
from src.schemas.bookings import BookingAdd


async def test_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id

    # Create
    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2025, month=6, day=10),
        date_to=date(year=2025, month=6, day=20),
        price=100,
    )
    created = await db.bookings.add(booking_data)

    # Read
    booking = await db.bookings.get_one_or_none(id=created.id)

    assert booking
    assert booking.id == created.id
    assert booking.room_id == created.room_id
    assert booking.user_id == created.user_id
    assert booking.price == 100
    assert booking.model_dump(exclude={"id"}) == booking_data.model_dump()

    # Update
    await db.bookings.update_by_id(created.id, {"price": 150})
    updated = await db.bookings.get_one_or_none(id=created.id)

    assert updated is not None
    assert updated.id == created.id
    assert updated.price == 150
    assert updated.date_from == created.date_from
    assert updated.date_to == created.date_to
    assert updated.user_id == created.user_id
    assert updated.room_id == created.room_id

    # Delete
    await db.bookings.delete(id=created.id)
    deleted = await db.bookings.get_one_or_none(id=created.id)
    assert deleted is None

    await db.commit()
