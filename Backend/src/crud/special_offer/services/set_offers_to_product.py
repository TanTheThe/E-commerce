from src.crud.product.repositories import ProductRepository
from src.database.models import Special_Offer, Product
from src.errors.special_offer import SpecialOfferException
from src.schemas.special_offer import SetOfferToProduct
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.special_offer.repositories import SpecialOfferRepository
from datetime import datetime

special_offer_repository = SpecialOfferRepository()
product_repository = ProductRepository()


class SetOfferToProductService:
    async def set_offer_to_product(self, data: SetOfferToProduct, session: AsyncSession):
        condition_offer = [Special_Offer.id == data.special_offer_id, Special_Offer.deleted_at.is_(None)]
        special_offer = await special_offer_repository.get_special_offer(session=session, where_conditions=condition_offer)
        if not special_offer:
            SpecialOfferException.not_found()

        if special_offer.scope != "product":
            SpecialOfferException.invalid_scope_for_product()

        now = datetime.utcnow()
        if not (special_offer.start_time <= now <= special_offer.end_time):
            SpecialOfferException.expired_or_not_started()

        if special_offer.used_quantity >= special_offer.total_quantity:
            SpecialOfferException.insufficient_quantity()

        condition_product = Product.id.in_(data.product_id)
        await product_repository.update_product_some_field(
            condition_product,
            {"special_offer_id": data.special_offer_id},
            session
        )










