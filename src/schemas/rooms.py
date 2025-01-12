from pydantic import BaseModel, Field, ConfigDict


class RoomAdd(BaseModel):
	title: str = Field(description="Название комнаты")
	description: str = Field(description="Описание комнаты")
	price: int = Field(description="Цена за комнату")
	quantity: int = Field(description="Доступное кол-во комнат")


class Room(RoomAdd):
	id: int
	model_config = ConfigDict(from_attributes=True)


class RoomPATCH(BaseModel):
	title: str = Field(None, description="Название комнаты")
	description: str = Field(None, description="Описание комнаты")
	price: int = Field(None, description="Цена за комнату")
	quantity: int = Field(None, description="Доступное кол-во комнат")
