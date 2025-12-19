from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement
from sqlalchemy.dialects.postgresql import insert

from src.database.models import Special_Offer, UserSpecialOffer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_, func, update
import uuid
from datetime import datetime
import time
from src.errors.special_offer import SpecialOfferException


class SpecialOfferRepository:
    async def create_special_offer(self, special_offer_data, session: AsyncSession):
        new_special_offer = Special_Offer(
            **special_offer_data
        )
        new_special_offer.created_at = datetime.now()
        new_special_offer.code = str(int(time.time() * 1000))
        session.add(new_special_offer)
        await session.commit()

        return new_special_offer

    async def create_user_special_offer(self, user_special_offer_data, session: AsyncSession):
        new_special_offer = UserSpecialOffer(
            **user_special_offer_data
        )
        session.add(new_special_offer)

        return new_special_offer


    async def bulk_create_assignments(self, assignments, session: AsyncSession):
        stmt = insert(UserSpecialOffer).values(assignments)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['special_offer_id', 'user_id']
        )

        await session.execute(stmt)


    async def get_all_special_offer(self, session: AsyncSession,
                                    select_columns: Optional[List[Any]] = None,
                                    joins: Optional[List[Tuple[Any, dict]]] = None,
                                    where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    group_by_columns: Optional[List[Any]] = None,
                                    having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    order_by: Optional[Any] = None,
                                    skip: int = 0, limit: int = 10,
                                    options: Optional[list] = None,
                                    for_update: Optional[bool] = False):

        if select_columns is None:
            query = select(Special_Offer)
        else:
            query = select(*select_columns).select_from(Special_Offer)

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

        if for_update:
            query = query.with_for_update()

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        offers = result.all()

        return offers, total


    async def get_special_offer(self, session: AsyncSession,
                                select_columns: Optional[List[Any]] = None,
                                joins: Optional[List[Tuple[Any, dict]]] = None,
                                where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                group_by_columns: Optional[List[Any]] = None,
                                having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                order_by: Optional[Any] = None,
                                options: Optional[list] = None,
                                populate_existing: bool = False,
                                for_update: Optional[bool] = False):

        if select_columns is None:
            query = select(Special_Offer)
        else:
            query = select(*select_columns).select_from(Special_Offer)

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

        if for_update:
            query = query.with_for_update()

        result = await session.exec(query)
        offer = result.one_or_none()

        return offer

    async def get_all_user_special_offer(self, session: AsyncSession,
                                    select_columns: Optional[List[Any]] = None,
                                    joins: Optional[List[Tuple[Any, dict]]] = None,
                                    where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    group_by_columns: Optional[List[Any]] = None,
                                    having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                    order_by: Optional[Any] = None,
                                    skip: int = 0, limit: int = 10,
                                    options: Optional[list] = None,
                                    for_update: Optional[bool] = False):

        if select_columns is None:
            query = select(UserSpecialOffer)
        else:
            query = select(*select_columns).select_from(UserSpecialOffer)

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

        if for_update:
            query = query.with_for_update()

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        user_offers = result.all()

        return user_offers, total


    async def get_user_special_offer(self, session: AsyncSession,
                                select_columns: Optional[List[Any]] = None,
                                joins: Optional[List[Tuple[Any, dict]]] = None,
                                where_conditions: Optional[List[ColumnElement[bool]]] = None,
                                group_by_columns: Optional[List[Any]] = None,
                                having_conditions: Optional[List[ColumnElement[bool]]] = None,
                                order_by: Optional[Any] = None,
                                options: Optional[list] = None,
                                populate_existing: bool = False,
                                for_update: Optional[bool] = False):

        if select_columns is None:
            query = select(UserSpecialOffer)
        else:
            query = select(*select_columns).select_from(UserSpecialOffer)

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

        if for_update:
            query = query.with_for_update()

        result = await session.exec(query)
        user_offer = result.one_or_none()

        return user_offer


    async def update_special_offer(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if isinstance(v, datetime):
                v = v.replace(tzinfo=None)

            setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()

        await session.commit()
        await session.refresh(data_need_update)
        return data_need_update

    async def update_offer_some_field(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any],
                                         session: AsyncSession, bulk_update: bool = False, updates: list = None):
        stmt = (
            update(Special_Offer)
            .where(condition)
            .values(**values)
            .returning(Special_Offer)
        )
        if bulk_update:
            stmt = stmt.execution_options(synchronize_session=False)
            result = await session.execute(stmt, updates)
        else:
            result = await session.execute(stmt)

        return result.one_or_none()

    async def update_user_offer_some_field(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(UserSpecialOffer)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)


    async def delete_special_offer(self, condition: Optional[List[Optional[ColumnElement[bool]]]], session: AsyncSession):
        special_offer_to_delete = await self.get_special_offer(session=session, where_conditions=condition)

        if special_offer_to_delete is None:
            SpecialOfferException.not_found_to_delete()

        special_offer_to_delete.deleted_at = datetime.now()
        await session.commit()

        return {}



