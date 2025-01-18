from pydantic import BaseModel, ConfigDict, Field


class RoomAdd(BaseModel):
	room_num: int
	room_type: str
	price: int
	is_occupied: bool
	

class RoomPATCH(BaseModel):
	room_num: int = Field(None)
	room_type: str = Field(None)
	price: int = Field(None)
	is_occupied: bool = Field(None)


class RoomAddWithHotel(RoomAdd):
	hotel_id: int  # Поле для связки с отелем


class Room(RoomAddWithHotel):
	id: int
	model_config = ConfigDict(from_attributes=True)
