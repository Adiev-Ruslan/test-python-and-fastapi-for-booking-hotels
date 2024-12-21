from fastapi import Depends, Query
from pydantic import BaseModel
from typing import Annotated


class PaginationParams(BaseModel):
	page: Annotated[int | None, Query(None, ge=1, description="Номер страницы (начинается с 1)")]
	per_page: Annotated[int | None, Query(None, ge=1, le=30, description="Кол-во отелей на странице")]
	
	
PaginationDep = Annotated[PaginationParams, Depends()]