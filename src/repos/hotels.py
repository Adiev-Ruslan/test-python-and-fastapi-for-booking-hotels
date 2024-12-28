from sqlalchemy import func, select

from src.models.hotels import HotelsOrm
from src.repos.base import BaseRepository


class HotelsRepository(BaseRepository):
	model = HotelsOrm
	
	async def get_all(self, location, title, limit, offset):
		query = select(HotelsOrm)
		if title:
			query = query.filter(HotelsOrm.title.ilike(f"%{title}%"))
		if location:
			query = query.filter(HotelsOrm.location.ilike(f"%{location}%"))
		
		# Запрос для подсчета общего количества записей
		count_query = select(func.count()).select_from(query.subquery())
		total_count_result = await self.session.execute(count_query)
		total_count = total_count_result.scalar()
		
		# Запрос с пагинацией
		paginated_query = (
			query
			.limit(limit)
			.offset(offset)
		)
		print(query.compile(compile_kwargs={"literal_binds": True}))
		result = await self.session.execute(paginated_query)
		hotels = result.scalars().all()
	
		return {"hotels": hotels, "total_count": total_count}
