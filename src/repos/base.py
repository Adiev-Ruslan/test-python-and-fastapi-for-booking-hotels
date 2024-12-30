from pydantic import BaseModel

from fastapi import HTTPException

from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound


class BaseRepository:
	model = None
	
	def __init__(self, session):
		self.session = session
	
	async def get_all(self, *args, **kwargs):
		query = select(self.model)
		result = await self.session.execute(query)
		return result.scalars().all()
	
	async def get_one_or_none(self, **filter_by):
		query = select(self.model).filter_by(**filter_by)
		result = await self.session.execute(query)
		return result.scalars().one_or_none()
	
	async def add(self, data: BaseModel):
		add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
		result = await self.session.execute(add_data_stmt)
		return result.scalars().one()
	
	async def edit(self, data: BaseModel, **filter_by) -> None:
		query = (
			select(self.model)
			.where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
		)
		result = await self.session.execute(query)
		objects = result.scalars().all()
		
		if not objects:
			raise HTTPException(status_code=404, detail="Нет такого отеля")
		if len(objects) > 1:
			raise HTTPException(status_code=422, detail="Ожидается 1 отель")
		
		await self.session.execute(
			update(self.model)
			.where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
			.values(**data.model_dump())
		)
		await self.session.commit()
	
	async def delete(self, **filter_by) -> None:
		query = (
			select(self.model)
			.where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
		)
		result = await self.session.execute(query)
		objects = result.scalars().all()
		
		if not objects:
			raise HTTPException(status_code=404, detail="Нет такого отеля")
		if len(objects) > 1:
			raise HTTPException(status_code=422, detail="Ожидается 1 отель")
		
		await self.session.execute(
			delete(self.model)
			.where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
		)
		await self.session.commit()
