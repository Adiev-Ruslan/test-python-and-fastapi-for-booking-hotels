import pytest
from sqlalchemy import delete


@pytest.fixture
async def clear_bookings(db):
	await db.session.execute(delete(db.bookings.model))
	await db.session.commit()
	yield


@pytest.mark.parametrize("room_id, date_from, date_to, expected_count", [
	(1, "2024-08-01", "2024-08-10", 1),
    (1, "2024-08-11", "2024-08-15", 1),
    (1, "2024-08-16", "2024-08-20", 1),
])
@pytest.mark.asyncio
async def test_add_and_get_bookings(
	room_id, date_from, date_to, expected_count,
	db, authenticated_ac, clear_bookings
):
	initial_response = await authenticated_ac.get("/bookings/me")
	assert len(initial_response.json()) == 0
	
	booking_response = await authenticated_ac.post(
		"/bookings",
		json={
			"room_id": room_id,
			"date_from": date_from,
			"date_to": date_to,
		}
	)
	assert booking_response.status_code == 200
	
	final_response = await authenticated_ac.get("/bookings/me")
	bookings = final_response.json()
	assert len(bookings) == expected_count
	
	last_booking = bookings[-1]
	assert last_booking["room_id"] == room_id
	assert last_booking["date_from"] == date_from
	assert last_booking["date_to"] == date_to


@pytest.mark.parametrize("room_id, date_from, date_to, status_code", [
	(1, "2024-08-01", "2024-08-10", 200),
	(1, "2024-08-02", "2024-08-11", 200),
	(1, "2024-08-03", "2024-08-12", 200),
	(1, "2024-08-04", "2024-08-13", 200),
	(1, "2024-08-05", "2024-08-14", 200),
	(1, "2024-08-06", "2024-08-15", 500),
	(1, "2024-08-17", "2024-08-25", 200),
])
async def test_add_booking(
	room_id, date_from,
	date_to, status_code,
	db, authenticated_ac
):
	# room_id = (await db.rooms.get_all())[0].id
	response = await authenticated_ac.post(
		"/bookings",
		json={
			"room_id": room_id,
			"date_from": date_from,
			"date_to": date_to
		}
	)
	
	assert response.status_code == status_code
	if status_code == 200:
		res = response.json()
		assert isinstance(res, dict)
		assert res["status"] == "OK"
		assert "data" in res
	