import pytest


@pytest.mark.asyncio
async def test_get_facilities(ac):
	response = await ac.get("/facilities")
	assert response.status_code == 200
	
	facilities = response.json()
	assert isinstance(facilities, list)
	
	if facilities:
		assert "id" in facilities[0]
		assert "name" in facilities[0]
	

@pytest.mark.asyncio
async def test_create_facility(ac):
	new_facility = {"name": "Кондиционер"}
	
	response = await ac.post("/facilities", json=new_facility)
	assert response.status_code == 200
	
	data = response.json()
	assert data["status"] == "OK"
	assert "data" in data
	facility = data["data"]
	
	assert facility["name"] == new_facility["name"]
	assert "id" in facility
	
	