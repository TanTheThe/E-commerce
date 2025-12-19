from src.crud.product.repositories import ProductRepository
from src.database.models import Special_Offer, Product
from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import SpecialOfferUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime

special_offer_repository = SpecialOfferRepository()
product_repository = ProductRepository()


class UpdateSpecialOfferService:
    async def update_special_offer(self, offer_id: str, update_data: SpecialOfferUpdateModel, session: AsyncSession):
        special_offer = await self.get_offer_with_lock(offer_id, session)

        update_dict = update_data.model_dump(exclude_none=True)

        if not update_dict:
            SpecialOfferException.no_data_available()

        if special_offer.used_quantity > 0:
            self.validate_update_for_used_offer(update_dict)

        self.validate_time_range(special_offer, update_dict)

        if 'total_quantity' in update_dict:
            if update_dict['total_quantity'] < special_offer.used_quantity:
                SpecialOfferException.total_must_less_than_used_quantity(update_dict, special_offer)

        self.handle_scope_and_condition(special_offer, update_dict)

        if 'scope' in update_dict and update_dict['scope'] != special_offer.scope:
            await self.validate_scope_change(special_offer, update_dict['scope'], session)

        updated_offer = await special_offer_repository.update_special_offer(special_offer, update_dict, session)

        return {
            "id": str(updated_offer.id),
            "code": updated_offer.code,
            "name": updated_offer.name,
            "discount": updated_offer.discount,
            "type": updated_offer.type,
            "scope": updated_offer.scope,
            "condition": updated_offer.condition,
            "total_quantity": updated_offer.total_quantity,
            "used_quantity": updated_offer.used_quantity,
            "start_time": updated_offer.start_time.isoformat(),
            "end_time": updated_offer.end_time.isoformat(),
            "updated_at": updated_offer.updated_at.isoformat() if updated_offer.updated_at else ""
        }


    async def get_offer_with_lock(self, offer_id: str, session: AsyncSession):
        conditions = [
            Special_Offer.id == offer_id,
            Special_Offer.deleted_at.is_(None)
        ]

        special_offer = await special_offer_repository.get_special_offer(session=session, where_conditions=conditions,
                                                                         for_update=True)

        if not special_offer:
            SpecialOfferException.not_found()

        return special_offer


    def validate_update_for_used_offer(self, update_dict: dict):
        allowed_fields = {'name', 'end_time'}
        updating_fields = set(update_dict.keys())
        not_allowed_fields = updating_fields - allowed_fields

        if not_allowed_fields:
            SpecialOfferException.fields_not_allowed_to_be_updated(allowed_fields, not_allowed_fields)


    def validate_time_range(self, special_offer: 'Special_Offer', update_dict: dict):
        new_start = update_dict.get('start_time', special_offer.start_time)
        new_end = update_dict.get('end_time', special_offer.end_time)

        if new_end <= new_start:
            SpecialOfferException.end_after_start_time()

        if 'start_time' in update_dict:
            now = datetime.now().replace(microsecond=0)
            if update_dict['start_time'] < now and special_offer.start_time >= now:
                SpecialOfferException.dont_change_start_time_to_past_time()

    def handle_scope_and_condition(self, special_offer: Special_Offer, update_dict: dict):
        new_scope = update_dict.get('scope')
        old_scope = special_offer.scope

        if new_scope and new_scope != old_scope:
            if new_scope == "product":
                update_dict['condition'] = None
            elif new_scope == "order":
                if 'condition' not in update_dict:
                    update_dict['condition'] = special_offer.condition

        if 'condition' in update_dict and update_dict.get('scope', old_scope) == "product":
            update_dict['condition'] = None

    async def validate_scope_change(self, special_offer: Special_Offer, new_scope: str, session: AsyncSession):
        if special_offer.scope == "product" and new_scope == "order":
            condition = [
                Product.special_offer_id == special_offer.id,
                Product.deleted_at.is_(None)
            ]
            has_products, _ = await product_repository.get_all_product(session=session, where_conditions=condition, limit=1)

            if has_products:
                SpecialOfferException.cant_change_scope_product_to_order()

        if special_offer.scope == "order" and new_scope == "product":
            if special_offer.used_quantity > 0:
                SpecialOfferException.cant_change_scope_order_to_product()




