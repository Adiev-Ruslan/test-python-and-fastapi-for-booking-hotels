from pydantic import BaseModel, ConfigDict, Field
from src.schemas.facilities import Facility


class RoomAddRequest(BaseModel):
    title: str
    description: str | None = None
    price: int
    quantity: int
    facilities_ids: list[int] = []


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str | None = None
    price: int
    quantity: int


class Room(RoomAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)


class RoomWithRels(Room):
    facilities: list[Facility]


class RoomPatchRequest(BaseModel):
    title: str = Field(None)
    description: str = Field(None)
    price: int = Field(None)
    quantity: int = Field(None)
    facilities_ids: list[int] = []


class RoomPatch(BaseModel):
    hotel_id: int = Field(None)
    title: str = Field(None)
    description: str = Field(None)
    price: int = Field(None)
    quantity: int = Field(None)
