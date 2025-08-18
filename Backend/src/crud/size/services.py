from src.crud.size.repositories import SizeRepository
from src.database.models import Color, Size
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from typing import List

size_repository = SizeRepository()


class SizeService:
    async def get_all_size(self, session: AsyncSession):
        sizes = await size_repository.get_all_size(None, session)

        response = []
        for size in sizes:
            response.append({
                "id": str(size.id),
                "name": size.name,
                "type": size.type,
            })

        return response

    async def get_all_size_by_type_size(self, type_sizes: List[str], session: AsyncSession):
        condition = and_(Size.type.in_(type_sizes))
        sizes = await size_repository.get_all_size(condition, session)

        response = []
        for size in sizes:
            response.append({
                "id": str(size.id),
                "name": size.name,
                "type": size.type,
            })

        return response

    async def get_size(self, type_size: str, session: AsyncSession):
        condition = and_(Size.type_size == type_size)
        size = await size_repository.get_size(condition, session)

        return {
            "id": str(size.id),
            "name": size.name,
            "type": size.type,
        }
