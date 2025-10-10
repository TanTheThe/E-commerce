from typing import Optional, List, Any, Tuple
from sqlalchemy import ColumnElement, delete
from src.database.models import PurchaseOrder, PurchaseOrderDetail, GoodsReceipt
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func
from datetime import datetime


class GoodsReceiptRepository:
    async def get_goods_receipt(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
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

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

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


    async def update_purchase_order(self, session: AsyncSession, po: PurchaseOrder,
                                    new_details: Optional[List[PurchaseOrderDetail]] = None):
        if new_details is not None:
            statement = delete(PurchaseOrderDetail).where(and_(PurchaseOrderDetail.purchase_order_id == po.id))
            await session.exec(statement)
            await session.flush()

            for detail in new_details:
                detail.purchase_order_id = po.id
                await session.exec(detail)

        po.updated_at = datetime.now()
        session.add(po)

        await session.commit()
        await session.refresh(po)

        return po
