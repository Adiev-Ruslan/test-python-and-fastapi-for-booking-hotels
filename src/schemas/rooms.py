from pydantic import BaseModel, ConfigDict, Field


class RoomAddRequest(BaseModel):
	room_num: int
	room_type: str
	price: int
	quantity: int
	facilities_ids: list[int] | None = None
	
	
class RoomAdd(BaseModel):
	hotel_id: int
	room_num: int
	room_type: str
	price: int
	quantity: int
	
	
class Room(RoomAdd):
	id: int
	model_config = ConfigDict(from_attributes=True)

	
class RoomPatchRequest(BaseModel):
	room_num: int = Field(None)
	room_type: str = Field(None)
	price: int = Field(None)
	quantity: int = Field(None)
	
	
class RoomPatch(BaseModel):
	hotel_id: int = Field(None)
	room_num: int = Field(None)
	room_type: str = Field(None)
	price: int = Field(None)
	quantity: int = Field(None)
	
