from typing import List
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
        special_offer = await self.validate_special_offer(data.special_offer_id, session)

        valid_product_ids = await self.validate_products(data.product_ids, session)

        if len(valid_product_ids) == 0:
            SpecialOfferException.no_valid_products()

        conflicts = await self.check_existing_offers(valid_product_ids, session)
        if conflicts:
            conflict_codes = ", ".join(conflicts[:5])
            SpecialOfferException.some_products_already_active_offers(conflict_codes, conflicts)

        condition_product = Product.id.in_(valid_product_ids)
        await product_repository.update_product_some_field(condition_product, {"special_offer_id": data.special_offer_id}, session)
        await session.commit()

        return {
            "updated_count": len(valid_product_ids),
            "special_offer_id": str(data.special_offer_id),
            "special_offer_code": special_offer.code
        }


    async def validate_special_offer(self, offer_id: str, session: AsyncSession):
        conditions = [
            Special_Offer.id == offer_id,
            Special_Offer.deleted_at.is_(None)
        ]

        special_offer = await special_offer_repository.get_special_offer(
            session=session,
            where_conditions=conditions
        )

        if not special_offer:
            SpecialOfferException.not_found()

        if special_offer.scope != "product":
            SpecialOfferException.invalid_scope_for_product()

        now = datetime.now().replace(microsecond=0)
        if now < special_offer.start_time:
            SpecialOfferException.offer_not_started_yet()

        if now > special_offer.end_time:
            SpecialOfferException.offer_has_expired()

        if special_offer.used_quantity >= special_offer.total_quantity:
            SpecialOfferException.insufficient_quantity()

        return special_offer


    async def validate_products(self, product_ids: List[str], session: AsyncSession):
        conditions = [
            Product.id.in_(product_ids),
            Product.deleted_at.is_(None)
        ]
        products, _ = product_repository.get_all_product(
            session=session,
            where_conditions=conditions
        )
        valid_ids = [str(row.id) for row in products]

        invalid_count = len(product_ids) - len(valid_ids)
        if invalid_count > 0:
            pass

        return valid_ids


    async def check_existing_offers(self, product_ids: List[str], session: AsyncSession):
        conditions = [
            Product.id.in_(product_ids),
            Product.deleted_at.is_(None),
            Special_Offer.deleted_at.is_(None),
            Special_Offer.start_time <= datetime.now(),
            Special_Offer.end_time >= datetime.now()
        ]

        joins = [
            (
                Special_Offer,
                {
                    "on": Product.special_offer_id == Special_Offer.id,
                    "type": "inner"
                }
            )
        ]

        products, _ = product_repository.get_all_product(session=session, joins=joins, where_conditions=conditions)
        conflict_codes = [row.code for row in products]

        return conflict_codes










