from datetime import datetime

from sqlalchemy.orm import selectinload, joinedload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories_Product, Categories, Product_Variant, Color, Special_Offer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.product import ProductException

product_repository = ProductRepository()
categories_repository = CategoriesRepository()
cate_product_repository = CategoriesProductRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
size_repository = SizeRepository()

product_variant_service = ProductVariantService()
categories_product_service = CategoriesProductService()
color_service = ColorService()


class GetDetailProductService:
    async def get_detail_product(self, product_id: str, session: AsyncSession):
        condition = and_(Product.id == product_id, Product.deleted_at.is_(None), Product.status == "active")
        joins = [
            selectinload(Product.categories_product).options(
                joinedload(Categories_Product.categories).load_only(
                    Categories.id,
                    Categories.name,
                    Categories.parent_id,
                    Categories.deleted_at
                )
            ),

            selectinload(Product.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.id,
                    Color.name,
                    Color.code,
                )
            ).load_only(
                Product_Variant.id,
                Product_Variant.size,
                Product_Variant.price,
                Product_Variant.quantity,
                Product_Variant.image,
                Product_Variant.sku,
                Product_Variant.color_name,
                Product_Variant.color_code,
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

        product_obj = await product_repository.get_product(condition, session, joins)

        if not product_obj:
            ProductException.not_found()

        product = product_obj[0]
        product_dict = product.model_dump()

        valid_categories = []
        for cp in product.categories_product:
            if cp.categories and cp.categories.deleted_at is None:
                valid_categories.append({
                    "id": str(cp.categories.id),
                    "name": cp.categories.name,
                    "parent_id": str(cp.categories.parent_id) if cp.categories.parent_id else None
                })

        if not valid_categories:
            ProductException.invalid_categories()

        product_dict["categories"] = valid_categories

        offer = product.special_offer
        valid_offer = self._is_offer_valid(offer)

        offer_type = offer.type if valid_offer else None
        offer_discount = offer.discount if valid_offer else None

        product_dict["offer"] = {
            "id": str(offer.id) if valid_offer else None,
            "type": offer.type if valid_offer else None,
            "discount": offer.discount if valid_offer else None,
            "name": offer.name if valid_offer else None
        }

        valid_variants = []
        for variant in product.product_variant:
            if variant.deleted_at is not None:
                continue

            if variant.price is None or variant.price < 0:
                continue

            if variant.quantity is None or variant.quantity < 0:
                continue

            original_price = variant.price
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

            variant_data = {
                "id": str(variant.id),
                "size": variant.size,
                "image": variant.image,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "quantity": variant.quantity,
                "sku": variant.sku
            }

            if variant.color:
                variant_data.update({
                    "color_id": str(variant.color.id),
                    "color_name": variant.color.name,
                    "color_code": variant.color.code
                })
            else:
                variant_data.update({
                    "color_id": None,
                    "color_name": variant.color_name,
                    "color_code": variant.color_code
                })

            valid_variants.append(variant_data)

        if not valid_variants:
            return None

        product_dict["product_variant"] = valid_variants

        return product_dict

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

    async def get_detail_product_admin(self, product_id: str, session: AsyncSession):
        product = await self.get_detail_product(product_id, session)

        if product is None:
            ProductException.not_found()

        product_variant = [
            {
                "id": str(item["id"]),
                "size": item["size"],
                "color_id": item.get("color_id"),
                "color_name": item.get("color_name"),
                "color_code": item.get("color_code"),
                "image": item["image"],
                "original_price": item["original_price"],
                "discounted_price": item["discounted_price"],
                "quantity": item["quantity"],
                "sku": item["sku"]
            }
            for item in product["product_variant"]
        ]

        product_dict = {
            "id": str(product["id"]),
            "name": product["name"],
            "images": product["images"],
            "description": product["description"],
            "short_description": product["short_description"],
            "categories": product["categories"],
            "offer": product["offer"],
            "status": product["status"],
            "product_variant": product_variant
        }

        return product_dict

    async def get_detail_product_customer(self, product_id: str, session: AsyncSession):
        product = await self.get_detail_product(product_id, session)

        if product is None:
            ProductException.not_found()

        product_variant = [
            {
                "id": str(item["id"]),
                "size": item["size"],
                "image": item["image"],
                "color_id": item.get("color_id"),
                "color_name": item.get("color_name"),
                "color_code": item.get("color_code"),
                "original_price": item["original_price"],
                "discounted_price": item["discounted_price"],
                "quantity": item["quantity"],
            }
            for item in product["product_variant"]
        ]

        product_dict = {
            "id": str(product["id"]),
            "name": product["name"],
            "images": product["images"],
            "description": product["description"],
            "short_description": product["short_description"],
            "categories": product["categories"],
            "total_sold": product["total_sold"],
            "review_count": product["review_count"],
            "avg_rating": product["avg_rating"],
            "offer": product["offer"],
            "product_variant": product_variant
        }

        return product_dict
