from src.database.models import Order, Order_Detail, Product_Variant, Product, Special_Offer, UserSpecialOffer
from src.crud.order.repositories import OrderRepository
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.product.repositories import ProductRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, func

order_repository = OrderRepository()
special_offer_repository = SpecialOfferRepository()
product_repository = ProductRepository()
order_detail_repository = OrderDetailRepository()
product_variant_repository = ProductVariantRepository()


class InventoryRestorationService:
    async def restore_all(self, session: AsyncSession, order_id: str):
        await self.restore_special_offer_usage(session, order_id)
        await self.restore_product_quantities(session, order_id)


    async def restore_special_offer_usage(self, session: AsyncSession, order_id: str):
        condition = [Order.id == order_id, Order.special_offer_id.isnot(None)]
        order = await order_repository.get_order(session=session, where_conditions=condition)

        if not order or not order.special_offer_id:
            return

        await special_offer_repository.update_offer_some_field(
            and_(Special_Offer.id == order.special_offer_id),
            {"used_quantity": Special_Offer.used_quantity - 1},
            session
        )

        await special_offer_repository.update_user_offer_some_field(
            and_(
                UserSpecialOffer.special_offer_id == order.special_offer_id,
                UserSpecialOffer.user_id == order.user_id
            ),
            {"used_at": None},
            session
        )


    async def restore_product_quantities(self, session: AsyncSession, order_id: str):
        condition = [Order_Detail.order_id == order_id, Order_Detail.deleted_at.is_(None)]
        order_details, _ = await order_detail_repository.get_all_order_detail(session=session, where_conditions=condition,
                                                                              skip=0, limit=1000)

        for detail in order_details:
            if detail.product_variant_id:
                await product_variant_repository.update_product_variant(
                    {"quantity": Product_Variant.quantity + detail.quantity},
                    and_(Product_Variant.id == detail.product_variant_id),
                    session
                )

            if detail.product_id:
                await product_repository.update_product_some_field(
                    and_(Product.id == detail.product_id),
                    {
                        "total_sold": Product.total_sold - detail.quantity,
                        "popularity_score": func.greatest(Product.popularity_score - 1, 0)
                    },
                    session
                )

