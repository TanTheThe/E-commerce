from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy import ColumnElement
from src.database.models import Categories
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, func
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
            created_at = datetime.now()
        )
        session.add(new_categories)
        await session.commit()
        await session.refresh(new_categories)

        return new_categories


    async def get_all_categories(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, skip: int = 0, limit: int = 10):
        count_stmt = select(func.count()).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Categories).where(*conditions).offset(skip).limit(limit)

        result = await session.exec(statement)

        categories = result.all()

        return categories, total


    async def get_category(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(Categories).where(conditions)
        result = await session.exec(statement)

        return result.one_or_none()


    async def update_categories(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if v is not None:
                setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()

        return data_need_update


    async def delete_categories(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        categories_to_delete = await self.get_category(condition, session)

        if categories_to_delete is None:
            CategoriesException.not_found_to_delete()

        categories_to_delete.deleted_at = datetime.now()

    async def delete_sub_categories(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        sub_categories = await self.get_all_categories(condition, session)

        if sub_categories is None:
            CategoriesException.not_found_to_delete()

        for sub_cat in sub_categories:
            sub_cat.deleted_at = datetime.now()



