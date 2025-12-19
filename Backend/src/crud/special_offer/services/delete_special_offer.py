from datetime import datetime
from sqlmodel import and_
from src.crud.product.repositories import ProductRepository
from src.database.models import Special_Offer, UserSpecialOffer, Order, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.errors.special_offer import SpecialOfferException
import logging

logger = logging.getLogger(__name__)


special_offer_repository = SpecialOfferRepository()
product_repository = ProductRepository()


class DeleteSpecialOfferService:
    async def delete_special_offer(self, offer_id: str, session: AsyncSession):
        special_offer = await self.get_offer_with_lock(offer_id, session)

        deletion_check = await self.check_deletion_eligibility(special_offer, session)

        if deletion_check['can_delete'] is False:
            SpecialOfferException.cant_delete_offer(deletion_check)

        await self.cleanup_relationships(special_offer, session)

        special_offer.deleted_at = datetime.now().replace(microsecond=0)

        await session.commit()

        return {
            "id": str(special_offer.id),
            "code": special_offer.code,
            "name": special_offer.name,
            "deleted_at": special_offer.deleted_at.isoformat(),
            "warnings": deletion_check['warnings']
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


    async def check_deletion_eligibility(self, special_offer: Special_Offer, session: AsyncSession):
        blockers = []
        warnings = []

        now = datetime.now().replace(microsecond=0)
        is_active = special_offer.start_time <= now <= special_offer.end_time

        if is_active:
            condition_user_offer = [
                UserSpecialOffer.special_offer_id == special_offer.id,
                UserSpecialOffer.used_at.is_(None)
            ]
            _, unused_count = await special_offer_repository.get_all_user_special_offer(
                session=session, where_conditions=condition_user_offer
            )

            if unused_count > 0:
                blockers.append(
                    f"Offer đang active và có {unused_count} users chưa sử dụng. "
                    f"Vui lòng thu hồi hoặc đợi offer hết hạn"
                )

        condition_order = [
            Order.special_offer_id == special_offer.id,
            Order.deleted_at.is_(None)
        ]
        _, order_count = await special_offer_repository.get_all_special_offer(
            session=session, where_conditions=condition_order
        )
        if order_count > 0:
            warnings.append(
                f"Offer đã được sử dụng trong {order_count} đơn hàng. "
                f"Thông tin order vẫn giữ nguyên sau khi xóa."
            )

        condition_product = [
            Product.special_offer_id == special_offer.id,
            Product.deleted_at.is_(None)
        ]
        _, product_count = await product_repository.get_all_product(session=session, where_conditions=condition_product)

        if product_count > 0:
            warnings.append(
                f"Offer đang được gắn vào {product_count} sản phẩm. "
                f"Sẽ tự động gỡ offer khỏi các sản phẩm này."
            )

        return {
            'can_delete': len(blockers) == 0,
            'blockers': blockers,
            'warnings': warnings
        }


    async def cleanup_relationships(self, special_offer: Special_Offer, session: AsyncSession):
        if special_offer.scope == "product":
            conditions = and_(
                Product.special_offer_id == special_offer.id,
                Product.deleted_at.is_(None)
            )
            product = await special_offer_repository.update_offer_some_field(conditions, {"special_offer_id": None}, session)
            product_count = len(product)
            if product_count > 0:
                logger.info(f"Removed offer from {product_count} products")

        conditions_soft_delete = and_(
            UserSpecialOffer.special_offer_id == special_offer.id,
            UserSpecialOffer.used_at.is_(None)
        )
        product = await special_offer_repository.update_offer_some_field(conditions_soft_delete,
                                                                         {"deleted_at": datetime.now().replace(microsecond=0)},
                                                                         session)
        unused_count = len(product)
        if unused_count > 0:
            logger.info(f"Soft deleted {unused_count} unused assignments")
