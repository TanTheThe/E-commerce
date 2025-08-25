from typing import Optional, List
from sqlalchemy import ColumnElement
from sqlalchemy.orm import noload, load_only

from src.database.models import Color
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func
from datetime import datetime
from src.errors.color import ColorException


class ColorRepository:
    async def create_color(self, color_data, session: AsyncSession):
        color_data_dict = color_data.model_dump()

        new_color = Color(
            **color_data_dict,
            created_at=datetime.now()
        )
        session.add(new_color)

        return new_color


    async def get_all_color(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, skip: int = 0, limit: int = 10
                            , joins: list = None):
        count_stmt = select(func.count(Color.id)).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Color).where(*conditions).options(
            *joins if joins else []
        ).offset(skip).limit(limit)

        result = await session.exec(statement)

        colors = result.all()

        return colors, total


    async def get_color(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        base_condition = Color.deleted_at.is_(None)
        if conditions is not None:
            combined_condition = and_(base_condition, conditions)
        else:
            combined_condition = base_condition

        statement = select(Color).options(
            noload(Color.product_variant),
            load_only(Color.name, Color.code, Color.id)
        ).where(combined_condition)

        result = await session.exec(statement)

        return result.one_or_none()


    async def update_color(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if v is not None:
                setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()

        return data_need_update


    async def delete_color(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        color_delete = await self.get_color(condition, session)

        if color_delete is None:
            ColorException.color_not_found()

        color_delete.deleted_at = datetime.now()
        await session.commit()

        return str(color_delete.id)
