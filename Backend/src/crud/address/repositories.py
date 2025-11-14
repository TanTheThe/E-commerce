from typing import Optional, Any, List, Tuple
from sqlalchemy import ColumnElement, func
from src.database.models import Address, Province, Ward
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_
from datetime import datetime
from src.errors.address import AddressException


class AddressRepository:
    async def create_address(self, address_dict, session: AsyncSession):
        address = Address(**address_dict)
        session.add(address)
        await session.flush()
        await session.refresh(address)

        return address

    async def get_all_addresses(self, session: AsyncSession,
                                select_columns: Optional[List[Any]] = None,
                                joins: Optional[List[Tuple[Any, dict]]] = None,
                                where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                group_by_columns: Optional[List[Any]] = None,
                                having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                order_by: Optional[Any] = None,
                                options: Optional[List[Any]] = None,
                                skip: int = 0, limit: int = 10):

        if select_columns is None:
            query = select(Address)
        else:
            query = select(*select_columns).select_from(Address)

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

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.exec(count_query)
        total = count_result.one() or 0

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)

        addresses = result.all()

        return addresses, total


    async def get_address(self, session: AsyncSession,
                                select_columns: Optional[List[Any]] = None,
                                joins: Optional[List[Tuple[Any, dict]]] = None,
                                where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                group_by_columns: Optional[List[Any]] = None,
                                having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                order_by: Optional[Any] = None,
                                options: Optional[List[Any]] = None):

        if select_columns is None:
            query = select(Address)
        else:
            query = select(*select_columns).select_from(Address)

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

        result = await session.exec(query)

        address = result.one_or_none()

        return address


    async def get_province(self, session: AsyncSession,
                           joins: Optional[List[Tuple[Any, dict]]] = None,
                           where_conditions: Optional[List[ColumnElement[bool]]] = None,
                           order_by: Optional[Any] = None,
                           options: Optional[List[Any]] = None):

        query = select(Province)

        if joins:
            for table, config in joins:
                if config.get("type") == "outer":
                    query = query.outerjoin(table, config["on"])
                else:
                    query = query.join(table, config["on"])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        result = await session.exec(query)

        province = result.one_or_none()

        return province


    async def get_all_provinces(self, session: AsyncSession,
                           joins: Optional[List[Tuple[Any, dict]]] = None,
                           where_conditions: Optional[List[ColumnElement[bool]]] = None,
                           order_by: Optional[Any] = None,
                           options: Optional[List[Any]] = None):

        query = select(Province)

        if joins:
            for table, config in joins:
                if config.get("type") == "outer":
                    query = query.outerjoin(table, config["on"])
                else:
                    query = query.join(table, config["on"])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        result = await session.exec(query)

        provinces = result.all()

        return provinces


    async def get_ward(self, session: AsyncSession,
                           joins: Optional[List[Tuple[Any, dict]]] = None,
                           where_conditions: Optional[List[ColumnElement[bool]]] = None,
                           order_by: Optional[Any] = None,
                           options: Optional[List[Any]] = None):

        query = select(Ward)

        if joins:
            for table, config in joins:
                if config.get("type") == "outer":
                    query = query.outerjoin(table, config["on"])
                else:
                    query = query.join(table, config["on"])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        result = await session.exec(query)

        ward = result.one_or_none()

        return ward


    async def get_all_wards(self, session: AsyncSession,
                           joins: Optional[List[Tuple[Any, dict]]] = None,
                           where_conditions: Optional[List[ColumnElement[bool]]] = None,
                           order_by: Optional[Any] = None,
                           options: Optional[List[Any]] = None):

        query = select(Ward)

        if joins:
            for table, config in joins:
                if config.get("type") == "outer":
                    query = query.outerjoin(table, config["on"])
                else:
                    query = query.join(table, config["on"])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        result = await session.exec(query)

        wards = result.all()

        return wards


    async def delete_address(self, where_conditions: Optional[List[ColumnElement[bool]]], session: AsyncSession):
        address_to_delete = await self.get_address(session=session, where_conditions=where_conditions)

        if address_to_delete is None:
            AddressException.not_found_to_delete()

        address_to_delete.deleted_at = datetime.now()
        await session.commit()

        return {}



