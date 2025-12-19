from src.database.models import Special_Offer, UserSpecialOffer
from src.schemas.special_offer import SpecialOfferFilterModel, QuantityStatusEnum, TimeStatusEnum, OfferScopeEnum
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, or_, select, desc, asc
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime
from typing import Optional

special_offer_repository = SpecialOfferRepository()


class GetAllSpecialOfferService:
    async def get_all_special_offer_admin(self, session: AsyncSession, filter_data: SpecialOfferFilterModel, skip: int = 0, limit: int = 10):
        conditions = [Special_Offer.deleted_at.is_(None)]

        if filter_data.search:
            search_term = f"%{filter_data.search}%"
            conditions.append(or_(
                Special_Offer.code.ilike(search_term),
                Special_Offer.name.ilike(search_term)
            ))

        if filter_data.type:
            conditions.append(Special_Offer.type == filter_data.type.value)

        if filter_data.scope:
            conditions.append(Special_Offer.scope == filter_data.scope.value)

        if filter_data.discount_min is not None:
            conditions.append(Special_Offer.discount >= filter_data.discount_min)
        if filter_data.discount_max is not None:
            conditions.append(Special_Offer.discount <= filter_data.discount_max)

        if filter_data.quantity_status:
            if filter_data.quantity_status == QuantityStatusEnum.REMAINING:
                conditions.append(Special_Offer.total_quantity > Special_Offer.used_quantity)
            elif filter_data.quantity_status == QuantityStatusEnum.OUT:
                conditions.append(Special_Offer.total_quantity <= Special_Offer.used_quantity)

        now = datetime.now().replace(microsecond=0)
        if filter_data.time_status:
            if filter_data.time_status == TimeStatusEnum.UPCOMING:
                conditions.append(Special_Offer.start_time > now)
            elif filter_data.time_status == TimeStatusEnum.ACTIVE:
                conditions.append(and_(
                    Special_Offer.start_time <= now,
                    Special_Offer.end_time >= now
                ))
            elif filter_data.time_status == TimeStatusEnum.EXPIRED:
                conditions.append(Special_Offer.end_time < now)

        special_offers, total = await special_offer_repository.get_all_special_offer(session=session, where_conditions=conditions,
                                                                                     skip=skip, limit=limit, order_by=desc(Special_Offer.created_at))

        response = []
        for offer in special_offers:
            offer_dict = {
                "id": str(offer.id),
                "code": offer.code,
                "name": offer.name,
                "discount": offer.discount,
                "type": offer.type,
                "scope": offer.scope,
                "condition": offer.condition,
                "total_quantity": offer.total_quantity,
                "used_quantity": offer.used_quantity,
                "start_time": str(offer.start_time),
                "end_time": str(offer.end_time),
            }
            response.append(offer_dict)

        return {
            "data": response,
            "total": total
        }


    async def get_all_special_offer_customer(self, user_id: str, session: AsyncSession, search: Optional[str], skip: int = 0, limit: int = 10):
        conditions = [
            Special_Offer.deleted_at.is_(None),
            Special_Offer.scope == OfferScopeEnum.ORDER.value,
            Special_Offer.start_time <= datetime.now(),
            Special_Offer.end_time >= datetime.now(),
            Special_Offer.total_quantity > Special_Offer.used_quantity
        ]

        if search:
            search = search.strip()
            if search:
                search = search.replace('%', '\\%').replace('_', '\\_')
                search_term = f"%{search}%"
                conditions.append(or_(
                    Special_Offer.name.ilike(search_term),
                    Special_Offer.code.ilike(search_term),
                ))

        subquery = (
            select(UserSpecialOffer.special_offer_id)
            .where(
                and_(
                    UserSpecialOffer.user_id == user_id,
                    UserSpecialOffer.used_at.is_(None)
                )
            )
        )
        conditions.append(Special_Offer.id.in_(subquery))

        special_offers, total = await special_offer_repository.get_all_special_offer(
            session=session,
            where_conditions=conditions,
            skip=skip,
            limit=limit,
            order_by=asc(Special_Offer.end_time)
        )

        response = []
        for offer in special_offers:
            offer_dict = {
                "id": str(offer.id),
                "code": offer.code,
                "name": offer.name,
                "discount": offer.discount,
                "type": offer.type,
                "scope": offer.scope,
                "condition": offer.condition,
                "total_quantity": offer.total_quantity,
                "used_quantity": offer.used_quantity,
                "start_time": str(offer.start_time),
                "end_time": str(offer.end_time),
            }
            response.append(offer_dict)

        return {
            "data": response,
            "total": total
        }











