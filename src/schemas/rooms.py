from pydantic import BaseModel, ConfigDict


class RoomAdd(BaseModel):
	room_num: int
	room_type: str
	price: int
	quantity: int
	is_occupied: bool


class RoomAddWithHotel(RoomAdd):
	hotel_id: int  # Поле для связки с отелем


class Room(RoomAddWithHotel):
	id: int
	model_config = ConfigDict(from_attributes=True)
