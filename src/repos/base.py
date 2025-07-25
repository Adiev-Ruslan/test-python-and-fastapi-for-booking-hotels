from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound, IntegrityError
from asyncpg.exceptions import UniqueViolationError

from src.repos.mappers.base import DataMapper
from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException


class BaseRepository:
    model = None
    mapper: DataMapper = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def update_by_id(self, item_id: int, data: dict):
        query = select(self.model).where(self.model.id == item_id)
        result = await self.session.execute(query)
        obj = result.scalars().first()

        if not obj:
            raise HTTPException(status_code=404, detail="Объект не найден")

        update_stmt = (
            update(self.model)
            .where(self.model.id == item_id)
            .values(**data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(update_stmt)

    async def add(self, data: BaseModel):
        try:
            add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            result = await self.session.execute(add_data_stmt)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            print(f"{type(ex.orig.__cause__)=}")
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjectAlreadyExistsException from ex
            else:
                raise ex

    async def add_bulk(self, data: list[BaseModel]):
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_data_stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        query = select(self.model).where(
            *[getattr(self.model, key) == value for key, value in filter_by.items()]
        )
        result = await self.session.execute(query)
        objects = result.scalars().all()

        if not objects:
            raise HTTPException(status_code=404, detail="Нет такого отеля или номера")

        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        query = select(self.model).where(
            *[getattr(self.model, key) == value for key, value in filter_by.items()]
        )
        result = await self.session.execute(query)
        objects = result.scalars().all()

        if not objects:
            raise HTTPException(status_code=404, detail="Нет такого отеля или номера")

        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
