from pydantic import BaseModel, Field


class Hotel(BaseModel):
	title: str
	location: str


class HotelPATCH(BaseModel):
	title: str = Field(None),
	location: str = Field(None)
