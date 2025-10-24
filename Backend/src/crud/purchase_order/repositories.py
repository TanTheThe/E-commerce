from typing import Optional, List, Any, Tuple, Dict
from sqlalchemy import ColumnElement, delete, update
from src.database.models import PurchaseOrder, PurchaseOrderDetail
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, or_
from datetime import datetime


class PurchaseOrderRepository:
    async def generate_po_number(self, session: AsyncSession) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"PO{today}"

        statement = select(func.count(PurchaseOrder.id)).where(
            PurchaseOrder.po_number.like(f"{prefix}%")
        )
        result = await session.exec(statement)

        count = result.one_or_none()

        sequence = str(count + 1).zfill(3)
        return f"{prefix}{sequence}"


    async def create_purchase_order(self, po_data: PurchaseOrder, po_details: List[PurchaseOrderDetail], session: AsyncSession):
        session.add(po_data)
        await session.flush()

        for detail in po_details:
            detail.purchase_order_id = po_data.id
            session.add(detail)

        await session.commit()
        await session.refresh(po_data)

        return po_data


    async def get_purchase_order(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            options: Optional[list] = None):

        if select_columns is None:
            query = select(PurchaseOrder)
        else:
            query = select(*select_columns).select_from(PurchaseOrder)

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
        po = result.one_or_none()

        return po


    async def get_all_purchase_orders(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):

        if select_columns is None:
            query = select(PurchaseOrder)
        else:
            query = select(*select_columns).select_from(PurchaseOrder)

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
        pos = result.all()

        return pos, total


    async def update_purchase_order(self, session: AsyncSession, po: PurchaseOrder,
                                    new_details: Optional[List[PurchaseOrderDetail]] = None):
        if new_details is not None:
            if po.po_details:
                for detail in po.po_details:
                    session.expunge(detail)
                po.po_details.clear()

            statement = delete(PurchaseOrderDetail).where(
                PurchaseOrderDetail.purchase_order_id == po.id
            )
            await session.exec(statement)
            await session.flush()

            for d in new_details:
                new_detail = PurchaseOrderDetail(
                    purchase_order_id=po.id,
                    product_variant_id=d.product_variant_id,
                    quantity=d.quantity,
                    received_quantity=0,
                    unit_cost=d.unit_cost,
                    total_cost=d.total_cost,
                    product_snapshot=d.product_snapshot,
                    created_at=datetime.now(),
                    notes=d.notes,
                )
                session.add(new_detail)

        po.updated_at = datetime.now()
        session.add(po)

        await session.commit()
        await session.refresh(po)

        return po


    async def update_po_some_field(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(PurchaseOrder)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)


    async def delete_purchase_order(self, session: AsyncSession, po_id: str):
        condition = [PurchaseOrder.id == po_id]
        po = await self.get_purchase_order(session=session, where_conditions=condition)
        if not po:
            return False

        detail_statement = select(PurchaseOrderDetail).where(
            PurchaseOrderDetail.purchase_order_id == po_id
        )
        result = await session.exec(detail_statement)
        details = result.all()
        for detail in details:
            await session.delete(detail)

        await session.delete(po)
        await session.commit()
        return True
