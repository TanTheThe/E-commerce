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

        session.add_all(receipt_details)

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
    
    
    async def get_all_goods_receipt_detail(self, session: AsyncSession,
                                    select_columns: Optional[List[Any]] = None,
                                    joins: Optional[List[Tuple[Any, dict]]] = None,
                                    where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    group_by_columns: Optional[List[Any]] = None,
                                    having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    order_by: Optional[Any] = None,
                                    skip: int = 0, limit: int = 10,
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

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.exec(count_query)
        total = count_result.one() or 0

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        grs_details = result.all()

        return grs_details, total


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
