from src.database.models import Special_Offer
from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import SpecialOfferCreateModel, SpecialOfferUpdateModel, SpecialOfferFilterModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, or_, func
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime
from typing import Any

special_offer_repository = SpecialOfferRepository()


class SpecialOfferService:
    async def create_special_offer_service(self, special_offer_data: SpecialOfferCreateModel, session: AsyncSession):
        create_data = special_offer_data.model_dump(exclude_none=True)

        if 'start_time' in create_data and 'end_time' in create_data:
            if create_data['end_time'] <= create_data['start_time']:
                SpecialOfferException.end_after_start_time()

        if 'total_quantity' in create_data:
            if create_data['total_quantity'] < 0:
                SpecialOfferException.total_greater_used()

        for k, v in create_data.items():
            if isinstance(v, datetime):
                create_data[k] = v.replace(tzinfo=None)

        new_special_offer = await special_offer_repository.create_special_offer(create_data, session)

        def serialize(obj: Any):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return {k: serialize(v) for k, v in create_data.items()}


    async def get_all_special_offer_service(self, session: AsyncSession, filter_data: SpecialOfferFilterModel, skip: int = 0, limit: int = 10):
        conditions = [Special_Offer.deleted_at.is_(None)]

        if filter_data.search:
            conditions.append(or_(
                Special_Offer.code.ilike(f"%{filter_data.search}%"),
                Special_Offer.name.ilike(f"%{filter_data.search}%")
            ))

        if filter_data.type in ["percent", "fixed"]:
            conditions.append(Special_Offer.type == filter_data.type)

        if filter_data.discount_min is not None:
            conditions.append(Special_Offer.discount >= filter_data.discount_min)
        if filter_data.discount_max is not None:
            conditions.append(Special_Offer.discount <= filter_data.discount_max)

        if filter_data.quantity_status == "remaining":
            conditions.append(Special_Offer.total_quantity > Special_Offer.used_quantity)
        elif filter_data.quantity_status == "out":
            conditions.append(Special_Offer.total_quantity <= Special_Offer.used_quantity)

        now = datetime.now().replace(microsecond=0)
        if filter_data.time_status == "upcoming":
            conditions.append(Special_Offer.start_time > now)
        elif filter_data.time_status == "active":
            conditions.append(and_(
                Special_Offer.start_time <= now,
                Special_Offer.end_time >= now
            ))
        elif filter_data.time_status == "expired":
            conditions.append(Special_Offer.end_time < now)

        special_offers, total = await special_offer_repository.get_all_special_offer(conditions, session, skip=skip, limit=limit)

        response = []
        for offer in special_offers:
            offer_dict = {
                "id": str(offer.id),
                "code": offer.code,
                "name": offer.name,
                "discount": offer.discount,
                "type": offer.type,
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

    async def update_special_offer_service(self, id: str, special_offer_update: SpecialOfferUpdateModel,
                                           session: AsyncSession):
        condition = and_(Special_Offer.id == id)
        special_offer = await special_offer_repository.get_special_offer(condition, session)

        if not special_offer:
            SpecialOfferException.not_found()

        update_data = special_offer_update.model_dump(exclude_none=True)

        if special_offer.used_quantity > 0:
            allowed_fields = {'name', 'end_time'}
            not_allowed_fields = set(update_data.keys()) - allowed_fields
            if not_allowed_fields:
                SpecialOfferException.not_update_fields()

        if 'start_time' in update_data and 'end_time' in update_data:
            if update_data['end_time'] <= update_data['start_time']:
                SpecialOfferException.end_after_start_time()
        elif 'end_time' in update_data:
            if update_data['end_time'] <= special_offer.start_time:
                SpecialOfferException.end_after_start_time()
        elif 'start_time' in update_data:
            if special_offer.end_time <= update_data['start_time']:
                SpecialOfferException.end_after_start_time()

        if 'total_quantity' in update_data:
            if update_data['total_quantity'] < special_offer.used_quantity:
                SpecialOfferException.total_greater_used()

        for k, v in update_data.items():
            if isinstance(v, datetime):
                update_data[k] = v.replace(tzinfo=None)

        await special_offer_repository.update_special_offer(special_offer, update_data, session)

        def serialize(obj: Any):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return {k: serialize(v) for k, v in update_data.items()}

    async def delete_categories_service(self, id: str, session: AsyncSession):
        condition = and_(Special_Offer.id == id)
        return await special_offer_repository.delete_special_offer(condition, session)
