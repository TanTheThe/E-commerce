from typing import Optional, List
from sqlalchemy import ColumnElement
from src.database.models import Categories
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_
from sqlalchemy.orm import noload
from datetime import datetime
from src.errors.categories import CategoriesException


class CategoriesRepository:
    async def create_categories(self, categories_data, session: AsyncSession):
        categories_data_dict = categories_data.model_dump()

        if "image" in categories_data_dict and categories_data_dict["image"]:
            base64_image = categories_data_dict["image"]

            if base64_image.startswith('data:image'):
                categories_data_dict["image"] = base64_image

        new_categories = Categories(
            **categories_data_dict,
            created_at=datetime.now()
        )
        session.add(new_categories)
        await session.commit()
        await session.refresh(new_categories)

        return new_categories

    async def get_all_categories(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession,
                                 skip: int = 0, limit: int = 5, joins: list = None):
        count_stmt = select(func.count()).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Categories).options(
            *joins if joins else []
        ).where(*conditions).offset(skip).limit(limit)

        result = await session.exec(statement)

        categories = result.all()

        return categories, total

    async def get_category(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        base_condition = Categories.deleted_at.is_(None)
        if conditions is not None:
            combined_condition = and_(base_condition, conditions)
        else:
            combined_condition = base_condition

        statement = select(Categories).options(
            *joins if joins else []
        ).where(combined_condition)
        result = await session.exec(statement)

        return result.one_or_none()

    async def update_categories(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if v is not None:
                setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()

        return data_need_update

    async def delete_categories(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        joins = [
            noload(Categories.categories_product),
            noload(Categories.products),
            noload(Categories.children),
            noload(Categories.parent),
        ]
        categories_to_delete = await self.get_category(condition, session, joins)

        if categories_to_delete is None:
            CategoriesException.not_found_to_delete()

        categories_to_delete.deleted_at = datetime.now()

    async def delete_sub_categories(self, condition: List[Optional[ColumnElement[bool]]], session: AsyncSession):
        joins = [
            noload(Categories.categories_product),
            noload(Categories.products),
            noload(Categories.children),
            noload(Categories.parent),
        ]
        sub_categories, total = await self.get_all_categories(condition, session, 0, 1000, joins)

        if sub_categories is None:
            CategoriesException.not_found_to_delete()

        for sub_cat in sub_categories:
            sub_cat.deleted_at = datetime.now()
