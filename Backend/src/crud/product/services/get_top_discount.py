from datetime import datetime
from sqlalchemy.orm import selectinload, joinedload
from sqlmodel import desc
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.database.models import Product, Categories, Product_Variant, Special_Offer

product_repository = ProductRepository()
categories_repository = CategoriesRepository()
cate_product_repository = CategoriesProductRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
size_repository = SizeRepository()
get_detail_product_service = GetDetailProductService()
product_variant_service = ProductVariantService()
categories_product_service = CategoriesProductService()
color_service = ColorService()


class GetTopDiscountService:
    async def get_top_discount(self, session: AsyncSession, limit: int = 12):
        condition = [
            Product.deleted_at.is_(None),
            Product.status == "active"
        ]

        order_by = desc(Product.created_at)

        joins = [
            selectinload(Product.categories).options(
                joinedload(Categories.parent)
            ).load_only(
                Categories.id,
                Categories.name,
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
                Special_Offer.discount,
                Special_Offer.type,
                Special_Offer.used_quantity,
                Special_Offer.total_quantity,
                Special_Offer.start_time,
                Special_Offer.end_time,
                Special_Offer.deleted_at
            ),
        ]

        products, _ = await product_repository.get_all_product(
            condition, session, joins, skip=0,
            limit=limit * 10,
            order_by_clause=order_by
        )

        products_with_discount = []

        for product in products:
            p = product[0]

            valid_categories = [cat for cat in p.categories if cat.deleted_at is None]
            if not valid_categories:
                continue

            active_variants = [
                variant for variant in p.product_variant
                if variant.deleted_at is None and variant.quantity > 0
            ]

            if not active_variants:
                continue

            prices = [variant.price for variant in active_variants if variant.price is not None]
            if not prices:
                continue

            price_min = min(prices)

            if price_min <= 0:
                continue

            offer = p.special_offer
            valid_offer = self._is_offer_valid(offer)

            if not valid_offer or not offer.discount or offer.type != "percent":
                continue

            if offer.discount <= 0:
                continue

            offer_discount = offer.discount
            original_price = price_min

            raw_discounted_price = original_price * (1 - offer_discount / 100)
            discounted_price = int(round(raw_discounted_price / 1000) * 1000)

            if discounted_price < 0 or discounted_price >= original_price:
                continue

            product_data = {
                "id": str(p.id),
                "name": p.name,
                "images": p.images,
                "avg_rating": p.avg_rating,
                "total_sold": p.total_sold,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "discount_percent": offer_discount,
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                    }
                    for category in valid_categories
                ]
            }

            products_with_discount.append(product_data)

        products_with_discount.sort(key=lambda x: x["discount_percent"], reverse=True)

        product_list = []
        for product_data in products_with_discount[:limit]:
            product_data.pop("discount_percent", None)
            product_list.append(product_data)

        return product_list

    def _is_offer_valid(self, offer: Special_Offer) -> bool:
        if not offer:
            return False

        if offer.deleted_at is not None:
            return False

        now = datetime.now()
        if offer.start_time > now or offer.end_time < now:
            return False

        if offer.used_quantity >= offer.total_quantity:
            return False

        return True
