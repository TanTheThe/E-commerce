from typing import Optional, List, Any, Tuple
from sqlalchemy import ColumnElement
from src.database.models import Brand
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


    async def get_all_brand(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):
        if select_columns is None:
            query = select(Brand)
        else:
            query = select(*select_columns).select_from(Brand)

        if joins:
            for table, config in joins:
                if config.get('type') == 'outer':
                    query = query.outerjoin(table, config['on'])
                else:
                    query = query.join(table, config['on'])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.exec(count_query)
        total = count_result.one() or 0

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        brands = result.all()

        return brands, total


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
