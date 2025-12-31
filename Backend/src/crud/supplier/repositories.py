from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, update
from src.database.models import Supplier, SupplierPayment, Supplier_Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func
from datetime import datetime


class SupplierRepository:
    async def get_all_suppliers(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):

        if select_columns is None:
            query = select(Supplier)
        else:
            query = select(*select_columns).select_from(Supplier)

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
        suppliers = result.all()

        return suppliers, total

    async def get_supplier(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            options: Optional[list] = None):

        if select_columns is None:
            query = select(Supplier)
        else:
            query = select(*select_columns).select_from(Supplier)

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
        supplier = result.one_or_none()

        return supplier

    async def create_supplier(self, supplier_data: dict, session: AsyncSession):
        supplier = Supplier(
            **supplier_data,
            is_active=True,
            created_at=datetime.now()
        )
        session.add(supplier)

        await session.commit()

        return supplier

    async def update_supplier(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Supplier)
            .where(condition)
            .values(**values)
        )

        await session.exec(stmt)


    async def delete_supplier(self, supplier_id: str, session: AsyncSession):
        condition = [Supplier.id == supplier_id]
        supplier = await self.get_supplier(session=session, where_conditions=condition)
        if not supplier:
            return False

        await self.update_supplier(and_(*condition), {'is_active': False, "updated_at": datetime.now()}, session)

        await session.commit()
        return True

    async def generate_supplier_code(self, session: AsyncSession) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"SUP-{today}"

        unique_suffix = uuid.uuid4().hex[:8].upper()

        return f"{prefix}-{unique_suffix}"


    async def get_supplier_payment(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            options: Optional[list] = None):

        if select_columns is None:
            query = select(SupplierPayment)
        else:
            query = select(*select_columns).select_from(SupplierPayment)

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
        supplier_payment = result.one_or_none()

        return supplier_payment


    async def get_all_suppliers_product(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):

        if select_columns is None:
            query = select(Supplier_Product)
        else:
            query = select(*select_columns).select_from(Supplier_Product)

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
        supplier_products = result.all()

        return supplier_products, total


    async def delete_supplier_product(self, condition: List[ColumnElement[bool]], session: AsyncSession):
        supplier = await self.get(session=session, where_conditions=condition)
        if not supplier:
            return False

        await self.update_supplier(and_(*condition), {'is_active': False, "updated_at": datetime.now()}, session)

        await session.commit()
        return True
