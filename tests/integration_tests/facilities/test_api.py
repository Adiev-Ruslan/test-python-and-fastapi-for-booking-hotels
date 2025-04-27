async def test_get_facilities(ac):
	response = await ac.get("/facilities")
	assert response.status_code == 200
	
	facilities = response.json()
	assert isinstance(facilities, list)
	
	if facilities:
		assert "id" in facilities[0]
		assert "name" in facilities[0]
	

async def test_create_facility(ac):
	new_facility = "Кондиционер"
	
	response = await ac.post("/facilities", json={"title": new_facility})
	assert response.status_code == 200
	
	data = response.json()
	assert isinstance(data, dict)
	assert data["data"]["title"] == new_facility
	assert "data" in data
	
	