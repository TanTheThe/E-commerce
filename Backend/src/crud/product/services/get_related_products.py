from datetime import datetime

from sqlalchemy.orm import selectinload, joinedload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories, Product_Variant, Special_Offer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, desc
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService

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


class GetRelatedProductsService:
    async def get_related_products(self, product_id: str, session: AsyncSession, limit_per_category: int = 12,
                                           price_range: float = 0.4):
        condition_product = and_(Product.id == product_id, Product.deleted_at.is_(None), Product.status == "active")
        joins_product = [
            selectinload(Product.categories).load_only(
                Categories.id,
                Categories.deleted_at
            ),
            selectinload(Product.product_variant).load_only(
                Product_Variant.id,
                Product_Variant.price,
                Product_Variant.quantity,
                Product_Variant.deleted_at
            )
        ]
        current_product_tuple = await product_repository.get_product(condition_product, session, joins_product)
        current_product = current_product_tuple[0]

        if not current_product:
            return []

        valid_current_categories = [cat for cat in current_product.categories if cat.deleted_at is None]
        if not valid_current_categories:
            return []

        active_variants = [
            variant for variant in current_product.product_variant
            if variant.deleted_at is None and variant.quantity > 0
        ]

        if not active_variants:
            return []

        prices = [variant.price for variant in active_variants if variant.price is not None]
        if not prices:
            return []

        current_price = min(prices)

        if current_price <= 0:
            return []

        min_price = current_price * (1 - price_range)
        max_price = current_price * (1 + price_range)

        condition = [
            Product.deleted_at.is_(None),
            Product.status == "active",
            Product.id != product_id,
            Product.categories.any(Categories.id.in_([c.id for c in valid_current_categories]))
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
            limit=limit_per_category * 3,
            order_by_clause=order_by
        )

        product_list = []
        for product in products:
            if len(product_list) >= limit_per_category:
                break

            p = product[0]

            valid_categories = [cat for cat in p.categories if cat.deleted_at is None]
            if not valid_categories:
                continue

            active_variants = [
                v for v in p.product_variant
                if v.deleted_at is None and v.quantity > 0
            ]

            if not active_variants:
                continue

            prices = [v.price for v in active_variants if v.price is not None]
            if not prices:
                continue

            price_min = min(prices)

            if price_min <= 0 or price_min < min_price or price_min > max_price:
                continue

            offer = p.special_offer
            valid_offer = self._is_offer_valid(offer)
            offer_discount = offer.discount if valid_offer else None
            offer_type = offer.type if valid_offer else None

            original_price = price_min
            discounted_price = original_price

            if offer_type and offer_discount is not None:
                if offer_type == "percent":
                    raw_discounted_price = original_price * (1 - offer_discount / 100)
                    discounted_price = int(round(raw_discounted_price / 1000) * 1000)
                elif offer_type == "fixed":
                    raw_discounted_price = max(0, original_price - offer_discount)
                    discounted_price = int(round(raw_discounted_price / 1000) * 1000)

            if discounted_price < 0:
                discounted_price = 0

            product_data = {
                "id": str(p.id),
                "name": p.name,
                "images": p.images,
                "total_sold": p.total_sold,
                "categories": [
                    {"id": str(category.id), "name": category.name}
                    for category in valid_categories
                ],
                "original_price": original_price,
                "discounted_price": discounted_price,
                "avg_rating": p.avg_rating,
            }

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
