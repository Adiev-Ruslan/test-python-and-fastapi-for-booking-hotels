from pydantic import BaseModel, ConfigDict, Field


class RoomAdd(BaseModel):
	room_num: int
	room_type: str
	price: int
	quantity: int
	

class RoomPATCH(BaseModel):
	room_num: int = Field(None)
	room_type: str = Field(None)
	price: int = Field(None)
	quantity: int = Field(None)
	

class RoomAddWithHotel(RoomAdd):
	hotel_id: int  # Поле для связки с отелем


class Room(RoomAddWithHotel):
	id: int
	model_config = ConfigDict(from_attributes=True)
