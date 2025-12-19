from typing import List, Dict, Any
from sqlalchemy import exists
from sqlalchemy.orm import selectinload, joinedload
from src.crud.product.services.utils import UtilProductsService
from src.database.models import Product, Categories, Product_Variant, Special_Offer, Brand
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, desc
from src.crud.product.repositories import ProductRepository
from src.errors.product import ProductException

product_repository = ProductRepository()
utils_service = UtilProductsService()


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

        current_product_tuple = await product_repository.get_product(session=session, where_conditions=condition, options=options)
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

        products, total = await product_repository.get_all_product(session=session,
            where_conditions=conditions,
            options=options,
            skip=0,
            limit=limit * 3,
            order_by=order_by
        )

        related_products = await self.filter_and_rank_products(products, product_info, limit)

        return {
            "products": related_products,
            "total": len(related_products),
            "limit": limit,
            "reference_product": {
                "id": str(current_product.id),
                "name": current_product.name,
                "price": product_info["current_price"]
            },
            "filters_applied": {
                "price_range_percent": price_range * 100,
                "min_price": product_info["min_price"],
                "max_price": product_info["max_price"],
                "categories": product_info["categories"]
            }
        }


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


    async def filter_and_rank_products(self, products: List, product_info: Dict[str, Any], limit: int):
        related_products = []
        min_price = product_info["min_price"]
        max_price = product_info["max_price"]
        current_category_ids = set(str(cat_id) for cat_id in product_info["category_ids"])

        for product_tuple in products:
            if len(related_products) >= limit:
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

            if price_min < min_price or price_min > max_price:
                continue

            product_category_ids = set(str(cat.id) for cat in valid_categories)
            matching_categories = current_category_ids.intersection(product_category_ids)
            relevance_score = len(matching_categories)

            offer = p.special_offer
            offer_status = utils_service.get_offer_status(offer)

            original_price = price_min
            discounted_price = original_price

            if offer_status["is_valid"] and offer:
                if offer.type == "percent":
                    raw_discounted = original_price * (1 - offer.discount / 100)
                    discounted_price = int(round(raw_discounted / 1000) * 1000)
                elif offer.type == "fixed":
                    raw_discounted = max(0, original_price - offer.discount)
                    discounted_price = int(round(raw_discounted / 1000) * 1000)

            discounted_price = max(0, discounted_price)

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
                "brand": {
                    "id": str(p.brand.id),
                    "name": p.brand.name,
                    "slug": p.brand.slug
                } if p.brand and p.brand.deleted_at is None else None,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "discount_percentage": round(
                    ((original_price - discounted_price) / original_price * 100), 2
                ) if original_price > 0 else 0,
                "avg_rating": float(p.avg_rating) if p.avg_rating else 0.0,
                "total_sold": p.total_sold if p.total_sold else 0,
                "in_stock": True,
                "relevance_score": relevance_score,
                "price_difference_percent": round(
                    abs((price_min - product_info["current_price"]) / product_info["current_price"] * 100), 2
                )
            }

            related_products.append(product_data)

        related_products.sort(key=lambda x: (-x["relevance_score"], -x["total_sold"], -x["avg_rating"]))

        return related_products
