from datetime import datetime

from sqlalchemy import exists
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
from src.errors.product import ProductException

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
    MAX_LIMIT = 50
    DEFAULT_PRICE_RANGE = 0.4  
    MIN_PRICE_RANGE = 0.1      
    MAX_PRICE_RANGE = 1.0
    
    async def get_related_products(self, product_id: str, session: AsyncSession, limit: int = 12, price_range: float = 0.4):
        limit = min(limit, self.MAX_LIMIT)
        price_range = max(self.MIN_PRICE_RANGE, min(price_range, self.MAX_PRICE_RANGE))
        
        condition = [
            Product.id == product_id,
            Product.deleted_at.is_(None),
            Product.status == "active"
        ]
        
        options = [
            selectinload(Product.categories).load_only(
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
            )
        ]

        current_product_tuple = await product_repository.get_product(session=session, condition=condition, options=options)
        current_product = current_product_tuple[0]

        if not current_product:
            ProductException.not_found()
            
        product_info = await self.extract_product_info(current_product)

        if not product_info:
            return {
                "products": [],
                "total": 0,
                "limit": limit,
                "reference_product": {
                    "id": str(current_product.id),
                    "name": current_product.name,
                    "price": None
                },
                "filters_applied": {
                    "price_range_percent": price_range * 100,
                    "categories": []
                }
            }

        conditions = [
            Product.deleted_at.is_(None),
            Product.status == "active",
            Product.id != product_id,
            Product.categories.any(
                and_(
                    Categories.id.in_(product_info["category_ids"]),
                    Categories.deleted_at.is_(None)
                )
            ),
            exists().where(
                and_(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None),
                    Product_Variant.quantity > 0,
                    Product_Variant.price >= product_info["min_price"],
                    Product_Variant.price <= product_info["max_price"]
                )
            )
        ]
        order_by = desc(Product.created_at)

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
            selectinload(Product.brand).load_only(
                Brand.id,
                Brand.name,
                Brand.slug,
                Brand.deleted_at
            )
        ]

        products, _ = await product_repository.get_all_product(session=session, where_conditions=condition,
                                                               options=joins, skip=0, limit=limit_per_category * 3,
                                                               order_by=order_by)

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
                "slug": p.slug,
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


    async def extract_product_info(self, product: Product):
        valid_categories = [
            cat for cat in product.categories 
            if cat.deleted_at is None
        ]
        
        if not valid_categories:
            return None
        
        active_variants = [
            variant for variant in product.product_variant
            if variant.deleted_at is None and variant.quantity > 0
        ]
        
        if not active_variants:
            return None
        
        prices = [v.price for v in active_variants if v.price is not None and v.price > 0]
        
        if not prices:
            return None
        
        current_price = min(prices)
        
        price_range = self.DEFAULT_PRICE_RANGE
        min_price = current_price * (1 - price_range)
        max_price = current_price * (1 + price_range)
        
        return {
            "current_price": current_price,
            "min_price": min_price,
            "max_price": max_price,
            "category_ids": [cat.id for cat in valid_categories],
            "categories": [
                {
                    "id": str(cat.id),
                    "name": cat.name,
                    "slug": cat.slug if hasattr(cat, 'slug') else None
                }
                for cat in valid_categories
            ]
        }
