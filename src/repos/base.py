from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete


class BaseRepository:
	model = None
	schema: BaseModel = None
	
	def __init__(self, session):
		self.session = session
		
	async def get_filtered(self, *filter, **filter_by):
		query = (
			select(self.model)
			.filter(*filter)
			.filter_by(**filter_by)
		)
		result = await self.session.execute(query)
		return [self.schema.model_validate(model) for model in result.scalars().all()]
	
	async def get_all(self, *args, **kwargs):
		query = select(self.model)
		result = await self.session.execute(query)
		return [
			self.schema.model_validate(model, from_attributes=True)
			for model in result.scalars().all()
		]
	
	async def get_one_or_none(self, **filter_by):
		query = select(self.model).filter_by(**filter_by)
		result = await self.session.execute(query)
		model = result.scalars().one_or_none()
		if model is None:
			return None
		return self.schema.model_validate(model, from_attributes=True)
	
	async def add(self, data: BaseModel):
		add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
		result = await self.session.execute(add_data_stmt)
		model = result.scalars().one()
		return self.schema.model_validate(model, from_attributes=True)
	
	async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
		query = (
			select(self.model)
			.where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
		)
		result = await self.session.execute(query)
		objects = result.scalars().all()
		
		if not objects:
			raise HTTPException(status_code=404, detail="Нет такого отеля или номера в БД")
		
		update_stmt = (
			update(self.model)
			.filter_by(**filter_by)
			.values(**data.model_dump(exclude_unset=exclude_unset))
		)
		await self.session.execute(update_stmt)
	
	async def exists(self, hotel_id: int) -> bool:
		query = select(self.model.id).filter_by(id=hotel_id)
		result = await self.session.execute(query)
		return result.scalar() is not None
		
	async def delete(self, **filter_by) -> None:
		query = (
			select(self.model)
			.where(*[getattr(self.model, key) == value for key, value in filter_by.items()])
		)
		result = await self.session.execute(query)
		objects = result.scalars().all()
		
		if not objects:
			raise HTTPException(status_code=404, detail="Нет такого отеля или номера в БД")
		
		delete_stmt = delete(self.model).filter_by(**filter_by)
		await self.session.execute(delete_stmt)
		