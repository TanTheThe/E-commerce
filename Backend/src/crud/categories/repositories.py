from typing import Optional, List, Any, Tuple
from sqlalchemy import ColumnElement
from src.database.models import Categories
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_
from datetime import datetime
from src.errors.categories import CategoriesException


class CategoriesRepository:
    async def create_categories(self, categories_data_dict, session: AsyncSession):
        new_categories = Categories(
            **categories_data_dict,
            created_at=datetime.now()
        )
        session.add(new_categories)
        await session.commit()
        await session.refresh(new_categories)

        return new_categories


    async def get_all_categories(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):
        if select_columns is None:
            query = select(Categories)
        else:
            query = select(*select_columns).select_from(Categories)

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
        categories = result.all()

        return categories, total


    async def get_category(self, session: AsyncSession,
                        select_columns: Optional[List[Any]] = None,
                        joins: Optional[List[Tuple[Any, dict]]] = None,
                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                        group_by_columns: Optional[List[Any]] = None,
                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                        order_by: Optional[Any] = None,
                        options: Optional[List[Any]] = None):

        if select_columns is None:
            query = select(Categories)
        else:
            query = select(*select_columns).select_from(Categories)

        if joins:
            for table, config in joins:
                if config.get("type") == "outer":
                    query = query.outerjoin(table, config["on"])
                else:
                    query = query.join(table, config["on"])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        result = await session.exec(query)

        category = result.one_or_none()

        return category

    async def update_categories(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if v is not None:
                setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()

        return data_need_update

    async def delete_categories(self, condition: Optional[List[ColumnElement[bool]]], session: AsyncSession):
        categories_to_delete = await self.get_category(session, where_conditions=condition)

        if categories_to_delete is None:
            CategoriesException.not_found_to_delete()

        categories_to_delete.deleted_at = datetime.now()

    async def delete_sub_categories(self, condition: Optional[List[ColumnElement[bool]]], session: AsyncSession):
        sub_categories, total = await self.get_all_categories(session=session, where_conditions=condition, skip=0, limit=1000)

        if sub_categories is None:
            CategoriesException.not_found_to_delete()

        for sub_cat in sub_categories:
            sub_cat.deleted_at = datetime.now()
