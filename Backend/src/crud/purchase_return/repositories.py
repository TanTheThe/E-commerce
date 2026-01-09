from typing import Optional, List, Any, Tuple, Dict
from sqlalchemy import ColumnElement
from src.database.models import PurchaseReturn, PurchaseReturnDetail
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func
from datetime import datetime


class PurchaseReturnRepository:
    async def generate_return_number(self, session: AsyncSession) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"PR{today}"

        statement = select(func.count(PurchaseReturn.id)).where(
            PurchaseReturn.return_number.like(f"{prefix}%")
        )
        result = await session.exec(statement)

        count = result.one_or_none()

        sequence = str(count + 1).zfill(3)
        return f"{prefix}{sequence}"
    
    
    async def generate_delivery_note_number(self, session: AsyncSession) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"DN{today}"

        statement = select(func.count(PurchaseReturn.id)).where(
            PurchaseReturn.delivery_note_number.like(f"{prefix}%")
        )
        result = await session.exec(statement)
        count = result.one_or_none() or 0

        sequence = str(count + 1).zfill(3)
        return f"{prefix}{sequence}"
    
    
    async def create_purchase_return(self, pr_data: Dict[str, Any], session: AsyncSession):
        pr = PurchaseReturn(**pr_data)
        
        session.add(pr)
        await session.flush()
        
        return pr
    
    async def create_purchase_return_detail(self, session: AsyncSession, detail_data: Dict[str, Any]):
        detail = PurchaseReturnDetail(**detail_data)
        
        session.add(detail)
        await session.flush()
        
        return detail

    async def get_purchase_return(self, session: AsyncSession,
                                  select_columns: Optional[List[Any]] = None,
                                  joins: Optional[List[Tuple[Any, dict]]] = None,
                                  where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                  group_by_columns: Optional[List[Any]] = None,
                                  having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                  order_by: Optional[Any] = None,
                                  options: Optional[list] = None):

        if select_columns is None:
            query = select(PurchaseReturn)
        else:
            query = select(*select_columns).select_from(PurchaseReturn)

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
        pr = result.one_or_none()

        return pr
    
    async def get_all_purchase_returns(self, session: AsyncSession,
                                     select_columns: Optional[List[Any]] = None,
                                     joins: Optional[List[Tuple[Any, dict]]] = None,
                                     where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                     group_by_columns: Optional[List[Any]] = None,
                                     having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                     order_by: Optional[Any] = None,
                                     skip: int = 0, limit: int = 10,
                                     options: Optional[list] = None):

        if select_columns is None:
            query = select(PurchaseReturn)
        else:
            query = select(*select_columns).select_from(PurchaseReturn)

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
        prs = result.all()

        return prs, total

    async def get_all_return_details(self, session: AsyncSession,
                                     select_columns: Optional[List[Any]] = None,
                                     joins: Optional[List[Tuple[Any, dict]]] = None,
                                     where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                     group_by_columns: Optional[List[Any]] = None,
                                     having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                     order_by: Optional[Any] = None,
                                     skip: int = 0, limit: int = 10,
                                     options: Optional[list] = None):

        if select_columns is None:
            query = select(PurchaseReturnDetail)
        else:
            query = select(*select_columns).select_from(PurchaseReturnDetail)

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
        return_details = result.all()

        return return_details, total

    async def get_purchase_return_detail(self, session: AsyncSession,
                                  select_columns: Optional[List[Any]] = None,
                                  joins: Optional[List[Tuple[Any, dict]]] = None,
                                  where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                  group_by_columns: Optional[List[Any]] = None,
                                  having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                  order_by: Optional[Any] = None,
                                  options: Optional[list] = None):

        if select_columns is None:
            query = select(PurchaseReturnDetail)
        else:
            query = select(*select_columns).select_from(PurchaseReturnDetail)

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
        pr_detail = result.one_or_none()

        return pr_detail

    async def delete_purchase_return(self, session: AsyncSession, purchase_return_id: str):
        condition = [PurchaseReturn.id == purchase_return_id]
        pr = await self.get_purchase_return(session=session, where_conditions=condition)
        if not pr:
            return False

        detail_statement = select(PurchaseReturnDetail).where(
            PurchaseReturnDetail.purchase_return_id == purchase_return_id
        )
        result = await session.exec(detail_statement)
        details = result.all()
        for detail in details:
            await session.delete(detail)

        await session.delete(pr)
        await session.commit()
        return True
