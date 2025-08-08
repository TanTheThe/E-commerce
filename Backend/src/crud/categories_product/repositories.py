from typing import Optional
from sqlalchemy import ColumnElement
from src.database.models import Categories_Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, delete
from datetime import datetime


class CategoriesProductRepository:
    async def create_cate_product(self, cate_product_data_list, product_id, session: AsyncSession):
        new_objects = [
            Categories_Product(
                product_id=product_id,
                categories_id=category.id,
                created_at=datetime.now()
            )
            for category in cate_product_data_list
        ]
        session.add_all(new_objects)

    async def get_all_cate_product(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(Categories_Product).order_by(desc(Categories_Product.created_at))
        if conditions:
            statement = statement.where(conditions)

        result = await session.exec(statement)
        return result.all()


    async def get_cate_product(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(Categories_Product).where(conditions)
        result = await session.exec(statement)

        return result.all()


    async def update_cate_product(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if v is not None:
                setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()
        await session.commit()

        return data_need_update


    async def delete_cate_product(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        delete_stmt = delete(Categories_Product).where(condition)
        await session.exec(delete_stmt)








