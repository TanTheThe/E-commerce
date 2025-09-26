from datetime import datetime

from sqlalchemy.orm import selectinload, joinedload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories_Product, Categories, Product_Variant, Color, Special_Offer, Size
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


class GetLatestProductsService:
    async def get_latest_products(self, session: AsyncSession, limit_per_category: int = 12):
        condition = [Product.deleted_at.is_(None), Product.status == "active"]
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

        products, _ = await product_repository.get_all_product(condition, session, joins, skip=0,
                                                               limit=limit_per_category, order_by_clause=order_by)

        product_list = []
        for product in products:
            valid_categories = [cat for cat in product[0].categories if cat.deleted_at is None]

            if not valid_categories:
                continue

            active_variants = [
                variant for variant in product[0].product_variant
                if variant.deleted_at is None and variant.quantity > 0
            ]

            if not active_variants:
                continue

            prices = [variant.price for variant in active_variants if variant.price is not None]
            price_min = min(prices) if prices else 0

            offer = product[0].special_offer
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

            product_data = {
                "id": str(product[0].id),
                "name": product[0].name,
                "images": product[0].images,
                "total_sold": product[0].total_sold,
                "slug": product[0].slug,
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                    }
                    for category in valid_categories
                ],
                "original_price": original_price,
                "discounted_price": discounted_price,
                "avg_rating": product[0].avg_rating
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
