from typing import Optional, List, Dict, Any
from sqlalchemy import ColumnElement
from src.database.models import Special_Offer, UserSpecialOffer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_, func, update
from sqlalchemy.orm import noload
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
        new_special_offer.created_at = datetime.now()
        session.add(new_special_offer)
        await session.commit()

        return new_special_offer

    async def bulk_create_user_special_offer(self, user_offers: list[UserSpecialOffer], session: AsyncSession):
        session.add_all(user_offers)
        await session.commit()
        return user_offers

    async def get_all_special_offer(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, skip: int = 0,
                            limit: int = 10, joins: list = None, for_update: bool = False):
        count_stmt = select(func.count()).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Special_Offer).options(
            *joins if joins else []
        ).where(*conditions).offset(skip).limit(limit)

        if for_update:
            statement = statement.with_for_update()

        result = await session.exec(statement)
        special_offers = result.all()

        return special_offers, total


    async def get_special_offer(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None,
                                for_update: bool = False):
        statement = select(Special_Offer).where(conditions).options(*joins if joins else [])

        if for_update:
            statement = statement.with_for_update()

        result = await session.exec(statement)

        return result.one_or_none()


    async def get_all_user_special_offer(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, joins: list = None):
        statement = select(UserSpecialOffer).options(
            *joins if joins else []
        ).where(*conditions)

        result = await session.exec(statement)
        special_offers = result.all()

        return special_offers

    async def get_user_special_offer(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(UserSpecialOffer).options(
            *joins if joins else []
        ).where(*conditions)

        result = await session.exec(statement)
        special_offers = result.one_or_none()

        return special_offers

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
        )
        if bulk_update:
            stmt = stmt.execution_options(synchronize_session=False)
            await session.execute(stmt, updates)
        else:
            await session.execute(stmt)

    async def update_user_offer_some_field(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(UserSpecialOffer)
            .where(condition)
            .values(**values)
        )
        await session.exec(stmt)

    async def delete_special_offer(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        special_offer_to_delete = await self.get_special_offer(condition, session)

        if special_offer_to_delete is None:
            SpecialOfferException.not_found_to_delete()

        special_offer_to_delete.deleted_at = datetime.now()
        await session.commit()

        return {}



