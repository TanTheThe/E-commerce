from src.database.models import Special_Offer
from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import SpecialOfferCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime

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

        return self.serialize_special_offer(new_special_offer)


    def serialize_special_offer(self, special_offer: Special_Offer) -> dict:
        return {
            "id": str(special_offer.id),
            "code": special_offer.code,
            "name": special_offer.name,
            "discount": special_offer.discount,
            "condition": special_offer.condition,
            "type": special_offer.type,
            "scope": special_offer.scope,
            "total_quantity": special_offer.total_quantity,
            "used_quantity": special_offer.used_quantity,
            "start_time": special_offer.start_time.isoformat(),
            "end_time": special_offer.end_time.isoformat(),
            "created_at": special_offer.created_at.isoformat(),
        }










