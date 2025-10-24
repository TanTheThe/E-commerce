from datetime import datetime

from sqlalchemy.orm import selectinload, joinedload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories, Product_Variant, Special_Offer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
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


class GetAllProductsOfferService:
    async def get_all_product_for_offer(self, categories_id: list, session: AsyncSession):
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
                Special_Offer.name,
                Special_Offer.used_quantity,
                Special_Offer.total_quantity,
                Special_Offer.start_time,
                Special_Offer.end_time,
                Special_Offer.deleted_at
            ),
        ]

        conditions = [
            Product.deleted_at.is_(None),
            Product.status == 'active',
            Product.categories.any(
                and_(
                    Categories.id.in_(categories_id),
                    Categories.deleted_at.is_(None)
                )
            )
        ]

        products, _ = await product_repository.get_all_product(conditions, session, joins, 0, 1000)

        categories_products = {}
        processed_products = set()

        for product in products:
            p = product[0]
            product_id = str(p.id)

            if product_id in processed_products:
                continue

            valid_categories = [cat for cat in p.categories if cat.deleted_at is None]
            if not valid_categories:
                continue

            active_variants = [
                variant for variant in p.product_variant
                if (variant.deleted_at is None and
                    variant.quantity is not None and variant.quantity >= 0 and
                    variant.price is not None and variant.price > 0)
            ]

            if not active_variants:
                continue

            first_category = None
            for requested_cat_id in categories_id:
                for category in valid_categories:
                    if str(category.id) == requested_cat_id:
                        first_category = category
                        break
                if first_category:
                    break

            if not first_category:
                continue

            offer = p.special_offer
            offer_status = self._get_offer_status(offer)

            product_data = {
                "id": product_id,
                "name": product[0].name,
                "images": product[0].images,
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                    }
                    for category in valid_categories
                ],
                "current_offer": {
                    "id": str(offer.id) if offer else None,
                    "type": offer.type if offer else None,
                    "discount": offer.discount if offer else None,
                    "is_valid": offer_status["is_valid"],
                    "reason": offer_status["reason"] if not offer_status["is_valid"] else None
                }
            }

            cat_id = str(first_category.id)

            if cat_id not in categories_products:
                categories_products[cat_id] = {
                    "category_info": {
                        "id": cat_id,
                        "name": first_category.name,
                    },
                    "products": []
                }

            categories_products[cat_id]["products"].append(product_data)
            processed_products.add(product_id)

        return categories_products


    def _get_offer_status(self, offer: Special_Offer) -> dict:
        if not offer:
            return {"is_valid": True, "reason": None}

        if offer.deleted_at is not None:
            return {"is_valid": False, "reason": "offer_deleted"}

        now = datetime.now()

        if offer.start_time > now:
            return {"is_valid": False, "reason": "not_started"}

        if offer.end_time < now:
            return {"is_valid": False, "reason": "expired"}

        if offer.used_quantity >= offer.total_quantity:
            return {"is_valid": False, "reason": "sold_out"}

        return {"is_valid": True, "reason": None}


