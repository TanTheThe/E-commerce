import uuid
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, update
from src.database.models import Warehouse, StockTransaction, StockTransfer, Stock, Product_Variant, Product, \
    Product_Material, Product_Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, or_
from datetime import datetime


class StockRepository:
    async def get_warehouse_summary(self, warehouse_id: str, session: AsyncSession) -> dict:
        total_products_query = select(func.count(Stock.id)).where(
            Stock.warehouse_id == warehouse_id
        )
        total_products_result = await session.exec(total_products_query)
        total_products = total_products_result.one() or 0

        total_quantity_query = select(func.sum(Stock.quantity)).where(
            Stock.warehouse_id == warehouse_id
        )
        total_quantity_result = await session.exec(total_quantity_query)
        total_quantity = total_quantity_result.one() or 0

        total_available_query = select(func.sum(Stock.available_quantity)).where(
            Stock.warehouse_id == warehouse_id
        )
        total_available_result = await session.exec(total_available_query)
        total_available = total_available_result.one() or 0

        total_reserved_query = select(func.sum(Stock.reserved_quantity)).where(
            Stock.warehouse_id == warehouse_id
        )
        total_reserved_result = await session.exec(total_reserved_query)
        total_reserved = total_reserved_result.one() or 0

        total_value_query = select(
            func.sum(Stock.quantity * func.coalesce(Stock.cost_price, 0))
        ).where(Stock.warehouse_id == warehouse_id)
        total_value_result = await session.exec(total_value_query)
        total_value = total_value_result.one() or 0

        low_stock_query = select(func.count(Stock.id)).where(
            and_(
                Stock.warehouse_id == warehouse_id,
                Stock.min_stock_level.is_not(None),
                Stock.quantity < Stock.min_stock_level,
                Stock.quantity > 0
            )
        )
        low_stock_result = await session.exec(low_stock_query)
        low_stock_items = low_stock_result.one() or 0

        out_of_stock_query = select(func.count(Stock.id)).where(
            and_(
                Stock.warehouse_id == warehouse_id,
                Stock.quantity == 0
            )
        )
        out_of_stock_result = await session.exec(out_of_stock_query)
        out_of_stock_items = out_of_stock_result.one() or 0

        return {
            "total_products": total_products,
            "total_quantity": total_quantity,
            "total_available_quantity": total_available,
            "total_reserved_quantity": total_reserved,
            "total_inventory_value": int(total_value),
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items
        }

    async def get_product_summary(self, variant_id: str, session: AsyncSession) -> dict:
        total_quantity_query = select(func.sum(Stock.quantity)).where(
            Stock.product_variant_id == variant_id
        )
        total_quantity_result = await session.exec(total_quantity_query)
        total_quantity = total_quantity_result.one() or 0

        total_available_query = select(func.sum(Stock.available_quantity)).where(
            Stock.product_variant_id == variant_id
        )
        total_available_result = await session.exec(total_available_query)
        total_available = total_available_result.one() or 0

        total_reserved_query = select(func.sum(Stock.reserved_quantity)).where(
            Stock.product_variant_id == variant_id
        )
        total_reserved_result = await session.exec(total_reserved_query)
        total_reserved = total_reserved_result.one() or 0

        warehouses_count_query = select(func.count(Stock.id)).where(
            Stock.product_variant_id == variant_id
        )
        warehouses_count_result = await session.exec(warehouses_count_query)
        warehouses_count = warehouses_count_result.one() or 0

        avg_cost_query = select(func.avg(Stock.cost_price)).where(
            and_(
                Stock.product_variant_id == variant_id,
                Stock.cost_price.is_not(None)
            )
        )
        avg_cost_result = await session.exec(avg_cost_query)
        avg_cost = avg_cost_result.one_or_none()

        return {
            "total_quantity": total_quantity,
            "total_available_quantity": total_available,
            "total_reserved_quantity": total_reserved,
            "warehouses_count": warehouses_count,
            "average_cost_price": int(avg_cost) if avg_cost else None
        }

    async def get_all_stock_transactions(self, session: AsyncSession,
                                        select_columns: Optional[List[Any]] = None,
                                        joins: Optional[List[Tuple[Any, dict]]] = None,
                                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                        group_by_columns: Optional[List[Any]] = None,
                                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                        order_by: Optional[Any] = None,
                                        skip: int = 0, limit: int = 10,
                                        options: Optional[list] = None):

        if select_columns is None:
            query = select(StockTransaction)
        else:
            query = select(*select_columns).select_from(StockTransaction)

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
        stock_transactions = result.all()

        return stock_transactions, total


    async def get_stock_transfers(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession,
                                  skip: int = 0, limit: int = 10,
                                  joins: list = None, order_by_clause=None):
        count_stmt = select(func.count(StockTransfer.id)).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(StockTransfer).where(*conditions).options(
            *joins if joins else []
        ).offset(skip).limit(limit)

        if order_by_clause is not None:
            statement = statement.order_by(order_by_clause)

        result = await session.exec(statement)

        transfers = result.all()

        return transfers, total

    async def get_all_stocks(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):

        if select_columns is None:
            query = select(Stock)
        else:
            query = select(*select_columns).select_from(Stock)

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
        stocks = result.all()

        return stocks, total

    async def get_stock(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            options: Optional[list] = None):

        if select_columns is None:
            query = select(Stock)
        else:
            query = select(*select_columns).select_from(Stock)

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

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        result = await session.exec(query)
        stock = result.one_or_none()

        return stock

    async def get_aggregated_inventory_list(self, select_columns: List[Any],
                                            session: AsyncSession,
                                            joins: Optional[List[Tuple[Any, dict]]] = None,
                                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                            group_by_columns: Optional[List[Any]] = None,
                                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                            order_by: Optional[Any] = None, skip: int = 0, limit: int = 10):
        query = select(*select_columns).select_from(Stock)

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

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        rows = result.all()

        return rows, total

    async def get_aggregated_inventory_summary(self, select_columns: List[Any],
                                               session: AsyncSession,
                                               joins: Optional[List[Tuple[Any, dict]]] = None,
                                               where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                               group_by_columns: Optional[List[Any]] = None,
                                               having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                               order_by: Optional[Any] = None):
        query = select(*select_columns).select_from(Stock)

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

        if order_by is not None:
            query = query.order_by(order_by)

        result = await session.exec(query)
        return result.first()

    async def create_stock(self, stock_data: dict, session: AsyncSession):
        stock = Stock(
            **stock_data,
            created_at=datetime.now()
        )
        session.add(stock)

        return stock

    async def update_stock(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Stock)
            .where(condition)
            .values(**values)
        )

        await session.exec(stmt)

    async def create_stock_transaction(self, stock_transaction_data: dict, session: AsyncSession):
        stock_transaction = StockTransaction(
            **stock_transaction_data,
            created_at=datetime.now()
        )
        session.add(stock_transaction)

        return stock_transaction
