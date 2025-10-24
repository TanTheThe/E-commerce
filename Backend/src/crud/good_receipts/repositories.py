from typing import Optional, List, Any, Tuple, Dict
from sqlalchemy import ColumnElement, delete, update
from src.database.models import PurchaseOrder, PurchaseOrderDetail, GoodsReceipt, GoodsReceiptDetail
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func
from datetime import datetime


class GoodsReceiptRepository:
    async def generate_gr_number(self, session: AsyncSession) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"GR{today}"

        statement = select(func.count(GoodsReceipt.id)).where(
            GoodsReceipt.receipt_number.like(f"{prefix}%")
        )
        result = await session.exec(statement)

        count = result.one_or_none()

        sequence = str(count + 1).zfill(3)
        return f"{prefix}{sequence}"


    async def create_goods_receipt(self, goods_receipt: GoodsReceipt, receipt_details: List[GoodsReceiptDetail], session: AsyncSession):
        session.add(goods_receipt)
        await session.flush()

        for detail in receipt_details:
            detail.goods_receipt_id = goods_receipt.id
            session.add(detail)

        await session.commit()
        await session.refresh(goods_receipt)

        return goods_receipt


    async def get_goods_receipt(self, session: AsyncSession,
                                select_columns: Optional[List[Any]] = None,
                                joins: Optional[List[Tuple[Any, dict]]] = None,
                                where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                group_by_columns: Optional[List[Any]] = None,
                                having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                order_by: Optional[Any] = None,
                                options: Optional[list] = None,
                                populate_existing: bool = False):

        if select_columns is None:
            query = select(GoodsReceipt)
        else:
            query = select(*select_columns).select_from(GoodsReceipt)

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

        if populate_existing:
            query = query.execution_options(populate_existing=True)

        result = await session.exec(query)
        gr = result.one_or_none()

        return gr

    async def get_all_goods_receipt(self, session: AsyncSession,
                                    select_columns: Optional[List[Any]] = None,
                                    joins: Optional[List[Tuple[Any, dict]]] = None,
                                    where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    group_by_columns: Optional[List[Any]] = None,
                                    having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    order_by: Optional[Any] = None,
                                    skip: int = 0, limit: int = 10,
                                    options: Optional[list] = None):

        if select_columns is None:
            query = select(GoodsReceipt)
        else:
            query = select(*select_columns).select_from(GoodsReceipt)

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
        grs = result.all()

        return grs, total


    async def get_goods_receipt_detail(self, session: AsyncSession,
                                select_columns: Optional[List[Any]] = None,
                                joins: Optional[List[Tuple[Any, dict]]] = None,
                                where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                group_by_columns: Optional[List[Any]] = None,
                                having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                order_by: Optional[Any] = None,
                                options: Optional[list] = None):

        if select_columns is None:
            query = select(GoodsReceiptDetail)
        else:
            query = select(*select_columns).select_from(GoodsReceiptDetail)

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
        gr_detail = result.one_or_none()

        return gr_detail


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


    async def update_gr_detail_some_field(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(GoodsReceiptDetail)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)


    async def delete_goods_receipt(self, session: AsyncSession, goods_receipt_id: str):
        condition = [GoodsReceipt.id == goods_receipt_id]
        pr = await self.get_goods_receipt(session=session, where_conditions=condition)
        if not pr:
            return False

        detail_statement = select(GoodsReceiptDetail).where(
            GoodsReceiptDetail.goods_receipt_id == goods_receipt_id
        )
        result = await session.exec(detail_statement)
        details = result.all()
        for detail in details:
            await session.delete(detail)

        await session.delete(pr)
        await session.commit()
        return True
