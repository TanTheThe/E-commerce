from typing import Optional, List, Any, Tuple, Dict
from sqlalchemy import ColumnElement, func
from src.database.models import Categories_Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, delete, and_
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

    async def get_all_cate_product(self, session: AsyncSession,
                                   select_columns: Optional[List[Any]] = None,
                                   select_from: Optional[Any] = None,
                                   joins: Optional[List[Tuple[Any, dict]]] = None,
                                   where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                   group_by_columns: Optional[List[Any]] = None,
                                   having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                   order_by: Optional[Any] = None,
                                   skip: int = 0, limit: int = 10,
                                   options: Optional[list] = None,
                                   subqueries: Optional[Dict[str, Any]] = None):
        if select_columns is None:
            query = select(Categories_Product)
        else:
            query = select(*select_columns)
            if select_from:
                query = query.select_from(select_from)
            else:
                query = query.select_from(Categories_Product)

        if subqueries:
            for alias, subquery_obj in subqueries.items():
                if 'join_condition' in subquery_obj:
                    if subquery_obj.get('join_type') == 'outer':
                        query = query.outerjoin(
                            subquery_obj['subquery'],
                            subquery_obj['join_condition']
                        )
                    else:
                        query = query.join(
                            subquery_obj['subquery'],
                            subquery_obj['join_condition']
                        )

        if joins:
            for table, config in joins:
                if config.get('type') == 'outer':
                    query = query.outerjoin(table, config['on'])
                else:
                    query = query.join(table, config['on'])

        if where_conditions:
            for condition in where_conditions:
                query = query.where(condition)

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
        cate_products = result.all()

        return cate_products, total

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
