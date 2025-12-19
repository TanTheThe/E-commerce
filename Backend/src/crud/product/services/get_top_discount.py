from sqlalchemy import exists, func
from sqlalchemy.orm import selectinload, joinedload
from sqlmodel import desc, and_, select
from src.crud.product.services.utils import UtilProductsService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product.repositories import ProductRepository
from src.database.models import Product, Categories, Product_Variant, Special_Offer

product_repository = ProductRepository()

utils_service = UtilProductsService()


class GetTopDiscountService:
    MAX_LIMIT = 50

    async def get_top_discount(self, session: AsyncSession, limit: int = 12):
        limit = min(limit, self.MAX_LIMIT)

        conditions = [
            Product.deleted_at.is_(None),
            Product.status == "active",
            Product.special_offer_id.isnot(None),
            exists().where(
                and_(
                    Special_Offer.id == Product.special_offer_id,
                    Special_Offer.type == "percent",
                    Special_Offer.discount > 0,
                    Special_Offer.start_time <= func.now(),
                    Special_Offer.end_time >= func.now(),
                    Special_Offer.used_quantity < Special_Offer.total_quantity,
                    Special_Offer.deleted_at.is_(None)
                )
            ),
            exists().where(
                and_(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None),
                    Product_Variant.quantity > 0,
                    Product_Variant.price > 0
                )
            )
        ]

        order_by = [
            desc(
                select(Special_Offer.discount)
                .where(Special_Offer.id == Product.special_offer_id)
                .scalar_subquery()
            ),
            desc(Product.total_sold),
            desc(Product.avg_rating)
        ]

        options = [
            selectinload(Product.categories).options(
                joinedload(Categories.parent)
            ).load_only(
                Categories.id,
                Categories.name,
                Categories.slug,
                Categories.parent_id,
                Categories.deleted_at
            ),
            selectinload(Product.product_variant).load_only(
                Product_Variant.id,
                Product_Variant.price,
                Product_Variant.quantity,
                Product_Variant.deleted_at
            ),
            selectinload(Product.special_offer).load_only(
                Special_Offer.id,
                Special_Offer.name,
                Special_Offer.discount,
                Special_Offer.type,
                Special_Offer.used_quantity,
                Special_Offer.total_quantity,
                Special_Offer.start_time,
                Special_Offer.end_time,
                Special_Offer.deleted_at
            ),
        ]

        products, total = await product_repository.get_all_product(
            session=session,
            where_conditions=conditions,
            options=options,
            skip=0,
            limit=limit * 2,
            order_by=order_by
        )

        product_list = []

        for product_tuple in products:
            if len(product_list) >= limit:
                break

            p = product_tuple[0]

            valid_categories = [
                cat for cat in p.categories
                if cat.deleted_at is None
            ]

            if not valid_categories:
                continue

            active_variants = [
                v for v in p.product_variant
                if v.deleted_at is None and v.quantity > 0
            ]

            if not active_variants:
                continue

            prices = [v.price for v in active_variants if v.price is not None and v.price > 0]

            if not prices:
                continue

            price_min = min(prices)

            offer = p.special_offer

            if not offer or offer.type != "percent" or offer.discount <= 0:
                continue

            offer_status = utils_service.get_offer_status(offer)

            if not offer_status["is_valid"]:
                continue

            original_price = price_min
            raw_discounted = original_price * (1 - offer.discount / 100)
            discounted_price = int(round(raw_discounted / 1000) * 1000)

            if discounted_price >= original_price:
                continue

            discounted_price = max(0, discounted_price)

            discount_amount = original_price - discounted_price

            product_data = {
                "id": str(p.id),
                "name": p.name,
                "slug": p.slug,
                "images": p.images if p.images else [],
                "description": p.short_description,
                "categories": [
                    {
                        "id": str(cat.id),
                        "name": cat.name,
                        "slug": cat.slug if hasattr(cat, 'slug') else None
                    }
                    for cat in valid_categories
                ],
                "original_price": original_price,
                "discounted_price": discounted_price,
                "discount_percentage": float(offer.discount),
                "discount_amount": discount_amount,
                "savings": discount_amount,
                "avg_rating": float(p.avg_rating) if p.avg_rating else 0.0,
                "total_sold": p.total_sold if p.total_sold else 0,
                "in_stock": True,
                "offer": {
                    "id": str(offer.id),
                    "name": offer.name,
                    "type": offer.type,
                    "discount": offer.discount,
                    "start_time": offer.start_time.isoformat() if offer.start_time else None,
                    "end_time": offer.end_time.isoformat() if offer.end_time else None,
                    "remaining_quantity": offer.total_quantity - offer.used_quantity,
                    "total_quantity": offer.total_quantity
                }
            }

            product_list.append(product_data)

        return {
            "products": product_list,
            "total": len(product_list),
            "limit": limit,
            "highest_discount": product_list[0]["discount_percentage"] if product_list else 0,
            "lowest_discount": product_list[-1]["discount_percentage"] if product_list else 0,
            "average_discount": round(
                sum(p["discount_percentage"] for p in product_list) / len(product_list), 2
            ) if product_list else 0
        }
