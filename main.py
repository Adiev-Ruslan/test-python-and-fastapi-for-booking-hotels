from fastapi import FastAPI, Query, Body
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn

app = FastAPI(docs_url=None)
hotels = [
	{"id": 1, "title": "Sochi", "name": "sochi"},
	{"id": 2, "title": "Дубай", "name": "dubai"},
]


@app.get(
	"/hotels",
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


@app.post(
	"/hotels",
	description="Добавить в БД новый отель"
)
def create_hotel(
	title: str = Body(embed=True),
):
	global hotels
	hotels.append({
		"id": hotels[-1]["id"] + 1,
		"title": title
	})
	return {"status": "OK"}


@app.put(
	"/hotels/{hotel_id}",
	description="Изменить все данные отеля"
)
def change_all_data_in_hotels(
	hotel_id: int,
	data: dict = Body({
		"title": "New Title",
		"name": "new-name"})
):
	global hotels
	
	for hotel in hotels:
		if hotel["id"] == hotel_id:
			hotel.update(data)
			break
	else:
		return {"status": "Hotel not found"}
	
	return {"status": "OK"}


@app.patch(
	"/hotels/{hotel_id}",
	description="Изменить некоторые данные отеля"
)
def change_some_data_in_hotels(
	hotel_id: int,
	title: str = Body(None),
	name: str = Body(None)
):
	global hotels
	
	for hotel in hotels:
		if hotel["id"] == hotel_id:
			if title:
				hotel["title"] = title
			if name:
				hotel["name"] = name
			break
	else:
		return {"status": "Hotel not found"}
	
	return {"status": "OK"}


@app.delete(
	"/hotels/{hotel_id}",
	description="Удалить отель из БД по его id"
)
def delete_hotel(hotel_id: int):
	global hotels
	hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
	return {"status": "OK"}
	
	
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
	return get_swagger_ui_html(
		openapi_url=app.openapi_url,
		title=app.title + " - Swagger UI",
		oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
		swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
		swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
	)


if __name__ == "__main__":
	uvicorn.run("main:app", reload=True)



	