from datetime import datetime
from sqlalchemy import exists
from sqlalchemy.orm import selectinload, joinedload
from src.crud.product.services.utils import UtilProductsService
from src.database.models import Product, Categories, Product_Variant, Special_Offer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, desc
from src.crud.product.repositories import ProductRepository

product_repository = ProductRepository()
utils_service = UtilProductsService()


class GetLatestProductsService:
    MAX_LIMIT = 50
    
    async def get_latest_products(self, session: AsyncSession, limit_per_category: int = 12):
        limit = min(limit_per_category, self.MAX_LIMIT)

        condition = [
            Product.deleted_at.is_(None),
            Product.status == "active",

            exists().where(
                and_(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None),
                    Product_Variant.quantity > 0
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
        ]

        products, total = await product_repository.get_all_product(
            session=session,
            where_conditions=condition,
            options=options,
            skip=0,
            limit=limit,
            order_by=order_by
        )

        product_list = []
        for product_tuple in products:
            product = product_tuple[0]
            
            valid_categories = [
                cat for cat in product.categories 
                if cat.deleted_at is None
            ]

            if not valid_categories:
                continue

            active_variants = [
                variant for variant in product.product_variant
                if variant.deleted_at is None and variant.quantity > 0
            ]

            if not active_variants:
                continue

            prices = [v.price for v in active_variants if v.price is not None]
            if not prices:
                continue
            
            price_min = min(prices)

            offer = product.special_offer
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

            product_data = {
                "id": str(product.id),
                "name": product.name,
                "slug": product.slug,
                "images": product.images if product.images else [],
                "description": product.short_description,
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
                "discount_percentage": round(
                    ((original_price - discounted_price) / original_price * 100), 2
                ) if original_price > 0 else 0,
                "avg_rating": float(product.avg_rating) if product.avg_rating else 0.0,
                "total_sold": product.total_sold if product.total_sold else 0,
                "in_stock": True,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "is_new": self.is_new_product(product.created_at) if product.created_at else False
            }

            product_list.append(product_data)

        return {
            "products": product_list,
            "total": len(product_list),
        }
        
        
    def is_new_product(self, created_at: datetime) -> bool:
        if not created_at:
            return False
        
        now = datetime.now()
        days_old = (now - created_at).days
        
        return days_old <= 30
