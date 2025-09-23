from typing import Optional, List
from sqlalchemy import ColumnElement
from src.database.models import Brand, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, update
from datetime import datetime
from src.errors.brand import BrandException
from src.schemas.brand import DeleteMultipleBrandsModel, BrandUpdateModel


class BrandRepository:
    async def create_brand(self, brand_data_dict, session: AsyncSession):
        new_brand = Brand(
            **brand_data_dict,
            created_at=datetime.now()
        )
        session.add(new_brand)
        await session.flush()

        return new_brand


    async def get_all_brand(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, skip: int = 0, limit: int = 10
                            , joins: list = None, order_by_clause=None):
        count_stmt = select(func.count(Brand.id)).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Brand).where(*conditions).options(
            *joins if joins else []
        ).offset(skip).limit(limit)
        
        if order_by_clause is not None:
            statement = statement.order_by(order_by_clause)

        result = await session.exec(statement)

        colors = result.all()

        return colors, total


    async def get_brand(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Brand).options(
            *joins if joins else []
        ).where(*conditions)
        result = await session.exec(statement)

        return result.one_or_none()


    async def update_brand(self, condition: Optional[ColumnElement[bool]], brand_data: BrandUpdateModel,
                           new_slug: Optional[str], session: AsyncSession):
        update_data = {}

        if brand_data.name is not None:
            update_data['name'] = brand_data.name
        if brand_data.logo is not None:
            update_data['logo'] = brand_data.logo
        if new_slug:
            update_data['slug'] = new_slug
        if brand_data.is_active is not None:
            update_data['is_active'] = brand_data.is_active

        update_data['updated_at'] = datetime.now()

        stmt = (
            update(Brand)
            .where(condition)
            .values(**update_data)
            .returning(Brand)
        )
        result = await session.exec(stmt)
        await session.flush()
        await session.commit()

        return result.one_or_none()


    async def delete_brand(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        brand_delete = await self.get_brand(condition, session)

        if brand_delete is None:
            BrandException.brand_not_found()

        brand_delete.deleted_at = datetime.now()
        await session.commit()

        return str(brand_delete.id)


    async def delete_multiple_brand(self, data: DeleteMultipleBrandsModel, session: AsyncSession):
        conditions = [Brand.id.in_(data.brand_ids), Brand.deleted_at.is_(None)]
        brands, _ = await self.get_all_brand(conditions, session)
        existing_ids = {str(row.id) for row in brands}
        missing_ids = set(data.brand_ids) - existing_ids
        if missing_ids:
            BrandException.brand_not_found()

        condition_delete = and_(Brand.id.in_(data.brand_ids), Brand.deleted_at.is_(None))
        stmt = update(Brand).where(condition_delete).values(deleted_at=datetime.now())
        await session.exec(stmt)
        await session.commit()

        return data.brand_ids
