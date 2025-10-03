import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import ColumnElement, update
from src.database.models import Warehouse, StockTransaction, StockTransfer
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
        result = await session.exec(
            select(func.max(Warehouse.code))
        )
        max_code = result.one_or_none()

        if not max_code:
            return "WH001"

        last_number = int(max_code.replace("WH", ""))
        new_number = last_number + 1
        return f"WH{new_number:03d}"


    async def get_all_warehouse(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, skip: int = 0, limit: int = 10,
                                joins: list = None, order_by_clause=None, options: list = None):
        count_stmt = select(func.count(Warehouse.id))

        if joins:
            for join_table, join_condition in joins:
                count_stmt = count_stmt.outerjoin(join_table, join_condition)

        if conditions:
            count_stmt = count_stmt.where(*conditions)

        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Warehouse)

        if joins:
            for join_table, join_condition in joins:
                statement = statement.outerjoin(join_table, join_condition)

        if conditions:
            statement = statement.where(*conditions)

        if options:
            statement = statement.options(*options)

        if order_by_clause is not None:
            statement = statement.order_by(order_by_clause)

        statement = statement.offset(skip).limit(limit)

        result = await session.exec(statement)
        warehouses = result.all()

        return warehouses, total


    async def get_warehouse(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Warehouse).options(
            *joins if joins else []
        ).where(conditions)
        result = await session.exec(statement)

        return result.one_or_none()


    async def update_warehouse(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Warehouse)
            .where(condition)
            .values(**values)
        )

        await session.exec(stmt)


    async def get_activity_summary(self, user_id: str, session: AsyncSession,
                                   warehouse_id: Optional[str] = None,
                                   from_date: Optional[datetime] = None,
                                   to_date: Optional[datetime] = None):
        base_query = select(StockTransaction).where(
            StockTransaction.performed_by == user_id
        )

        if warehouse_id:
            base_query = base_query.where(StockTransaction.warehouse_id == warehouse_id)
        if from_date:
            base_query = base_query.where(StockTransaction.created_at >= from_date)
        if to_date:
            base_query = base_query.where(StockTransaction.created_at <= to_date)

        total_query = select(func.count(StockTransaction.id)).select_from(base_query.subquery())
        total_result = await session.exec(total_query)
        total_transactions = total_result.one() or 0

        inbound_query = base_query.where(StockTransaction.transaction_type == "inbound")
        inbound_count_query = select(func.count(StockTransaction.id)).select_from(inbound_query.subquery())
        inbound_result = await session.exec(inbound_count_query)
        total_inbound = inbound_result.one() or 0

        outbound_query = base_query.where(StockTransaction.transaction_type == "outbound")
        outbound_count_query = select(func.count(StockTransaction.id)).select_from(outbound_query.subquery())
        outbound_result = await session.exec(outbound_count_query)
        total_outbound = outbound_result.one() or 0

        adjustment_query = base_query.where(StockTransaction.transaction_type == "adjustment")
        adjustment_count_query = select(func.count(StockTransaction.id)).select_from(adjustment_query.subquery())
        adjustment_result = await session.exec(adjustment_count_query)
        total_adjustments = adjustment_result.one() or 0

        value_query = select(func.sum(StockTransaction.total_cost)).select_from(base_query.subquery())
        value_result = await session.exec(value_query)
        total_value = value_result.one() or 0

        first_activity_query = select(func.min(StockTransaction.created_at)).select_from(base_query.subquery())
        first_result = await session.exec(first_activity_query)
        first_activity = first_result.one_or_none()

        last_activity_query = select(func.max(StockTransaction.created_at)).select_from(base_query.subquery())
        last_result = await session.exec(last_activity_query)
        last_activity = last_result.one_or_none()

        transfer_sent_query = select(func.count(StockTransfer.id)).where(
            or_(
                StockTransfer.requested_by == user_id,
                StockTransfer.approved_by == user_id,
                StockTransfer.shipped_by == user_id
            )
        )
        if warehouse_id:
            transfer_sent_query = transfer_sent_query.where(StockTransfer.from_warehouse_id == warehouse_id)
        if from_date:
            transfer_sent_query = transfer_sent_query.where(StockTransfer.requested_at >= from_date)
        if to_date:
            transfer_sent_query = transfer_sent_query.where(StockTransfer.requested_at <= to_date)

        transfer_sent_result = await session.exec(transfer_sent_query)
        total_transfers_sent = transfer_sent_result.one() or 0

        transfer_received_query = select(func.count(StockTransfer.id)).where(
            StockTransfer.received_by == user_id
        )
        if warehouse_id:
            transfer_received_query = transfer_received_query.where(StockTransfer.to_warehouse_id == warehouse_id)
        if from_date:
            transfer_received_query = transfer_received_query.where(StockTransfer.received_at >= from_date)
        if to_date:
            transfer_received_query = transfer_received_query.where(StockTransfer.received_at <= to_date)

        transfer_received_result = await session.exec(transfer_received_query)
        total_transfers_received = transfer_received_result.one() or 0

        return {
            "total_transactions": total_transactions,
            "total_inbound": total_inbound,
            "total_outbound": total_outbound,
            "total_adjustments": total_adjustments,
            "total_transfers_sent": total_transfers_sent,
            "total_transfers_received": total_transfers_received,
            "total_value_handled": total_value,
            "first_activity_date": first_activity,
            "last_activity_date": last_activity
        }