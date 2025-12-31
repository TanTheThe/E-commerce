import uuid
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, update
from src.database.models import Warehouse, StockTransaction
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, or_
from datetime import datetime


class WareHouseRepository:
    async def create_warehouse(self, warehouse_data: dict, session: AsyncSession):
        warehouse = Warehouse(
            **warehouse_data,
            created_at=datetime.now()
        )
        session.add(warehouse)

        return warehouse

    async def generate_warehouse_code(self, session: AsyncSession) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"WH{today}"

        unique_suffix = uuid.uuid4().hex[:8].upper()

        return f"{prefix}{unique_suffix}"

    async def get_all_warehouse(self, session: AsyncSession,
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
            query = select(Warehouse)
        else:
            query = select(*select_columns)
            if select_from:
                query = query.select_from(select_from)
            else:
                query = query.select_from(Warehouse)

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
        warehouses = result.all()

        return warehouses, total


    async def get_warehouse(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            options: Optional[List[Any]] = None,
                            for_update: Optional[bool] = False):

        if select_columns is None:
            query = select(Warehouse)
        else:
            query = select(*select_columns).select_from(Warehouse)

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

        if for_update:
            query = query.with_for_update()

        result = await session.exec(query)

        warehouse = result.one_or_none()

        return warehouse


    async def update_warehouse(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any],
                               session: AsyncSession):
        stmt = (
            update(Warehouse)
            .where(condition)
            .values(**values)
        )

        await session.exec(stmt)
