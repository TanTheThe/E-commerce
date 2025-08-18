from typing import Optional
from sqlalchemy import ColumnElement
from src.database.models import Size
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

class SizeRepository:
    async def get_all_size(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(Size).where(condition)
        result = await session.exec(statement)
        sizes = result.all()
        return sizes

    async def get_size(self, condition: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Size).where(condition)
        result = await session.exec(statement)
        return result.one_or_none()
