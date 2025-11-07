from src.database.models import Special_Offer
from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import SpecialOfferUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime
from typing import Any

special_offer_repository = SpecialOfferRepository()


class UpdateSpecialOfferService:
    async def update_special_offer(self, id: str, special_offer_update: SpecialOfferUpdateModel,
                                           session: AsyncSession):
        condition = [Special_Offer.id == id, Special_Offer.deleted_at.is_(None)]
        special_offer = await special_offer_repository.get_special_offer(session=session, where_conditions=condition)

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

        new_scope = update_data.get("scope")
        old_scope = special_offer.scope

        if new_scope:
            if old_scope == "order" and new_scope == "product":
                update_data["condition"] = None
                special_offer.condition = None
            elif old_scope == "product" and new_scope == "order":
                if "condition" not in update_data:
                    update_data["condition"] = special_offer.condition
        else:
            if "condition" not in update_data:
                update_data["condition"] = special_offer.condition

        for k, v in update_data.items():
            if isinstance(v, datetime):
                update_data[k] = v.replace(tzinfo=None)

        await special_offer_repository.update_special_offer(special_offer, update_data, session)

        def serialize(obj: Any):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return {k: serialize(v) for k, v in update_data.items()}









