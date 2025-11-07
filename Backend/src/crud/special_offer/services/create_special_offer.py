from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import SpecialOfferCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime
from typing import Any

special_offer_repository = SpecialOfferRepository()


class CreateSpecialOfferService:
    async def create_special_offer(self, special_offer_data: SpecialOfferCreateModel, session: AsyncSession):
        create_data = special_offer_data.model_dump(exclude_none=True)

        scope = create_data.get("scope", "order")
        condition = create_data.get("condition")

        if scope == "order":
            if condition is not None and condition < 0:
                SpecialOfferException.invalid_condition()
        elif scope == "product":
            create_data["condition"] = None

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











