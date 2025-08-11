from typing import Optional, List
from sqlalchemy import ColumnElement
from src.database.models import Special_Offer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_, func
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


    async def get_all_special_offer(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession, skip: int = 0,
                            limit: int = 10):
        count_stmt = select(func.count()).where(*conditions)
        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Special_Offer).where(*conditions).offset(skip).limit(limit)

        result = await session.exec(statement)
        special_offers = result.all()

        return special_offers, total


    async def get_special_offer(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(Special_Offer).where(conditions)

        result = await session.exec(statement)

        return result.one_or_none()


    async def update_special_offer(self, data_need_update, update_data: dict, session: AsyncSession):
        for k, v in update_data.items():
            if isinstance(v, datetime):
                v = v.replace(tzinfo=None)
            if v is not None:
                setattr(data_need_update, k, v)

        data_need_update.updated_at = datetime.now()

        await session.commit()

        return data_need_update


    async def delete_special_offer(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        special_offer_to_delete = await self.get_special_offer(condition, session)

        if special_offer_to_delete is None:
            SpecialOfferException.not_found_to_delete()

        special_offer_to_delete.deleted_at = datetime.now()
        await session.commit()

        return {}



