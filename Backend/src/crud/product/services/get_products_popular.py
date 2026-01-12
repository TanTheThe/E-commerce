from sqlalchemy import exists
from sqlalchemy.orm import selectinload, joinedload
from collections import defaultdict
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product.services.utils import UtilProductsService
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
from src.errors.categories import CategoriesException

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
utils_service = UtilProductsService()


class GetProductsPopularService:
    async def get_products_popular(self, parent_category_id: str, session: AsyncSession, 
                                   limit_per_category: int = 12):
        parent_category = await self.verify_parent_category(parent_category_id, session)
        
        child_categories = await self.get_child_categories(parent_category_id, session)
        
        if not child_categories:
            return {}
        
        child_category_ids = [str(cat.id) for cat in child_categories]
        
        condition = [
            Product.deleted_at.is_(None),
            Product.status == "active",
            Product.categories.any(
                and_(
                    Categories.id.in_(child_category_ids),
                    Categories.deleted_at.is_(None)
                )
            ),
            exists().where(
                and_(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None),
                    Product_Variant.quantity > 0
                )
            )
        ]

        order_by = desc(Product.popularity_score)

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

        products, _ = await product_repository.get_all_product(
            session=session,
            where_conditions=condition,
            options=options,
            skip=0,
            limit=len(child_category_ids) * limit_per_category * 2,
            order_by=order_by
        )

        categories_dict = defaultdict(list)
        category_counts = defaultdict(int)

        for product_tuple in products:
            product = product_tuple[0]
            
            valid_categories = [
                cat for cat in product.categories
                if (cat.deleted_at is None and str(cat.parent_id) == parent_category_id)
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
                "avg_rating": float(product.avg_rating) if product.avg_rating else 0.0,
                "total_sold": product.total_sold if product.total_sold else 0,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "discount_percentage": round(((original_price - discounted_price) / original_price * 100), 2) if original_price > 0 else 0,
                "in_stock": True,
                "categories": [
                    {
                        "id": str(cat.id),
                        "name": cat.name,
                        "slug": cat.slug if hasattr(cat, 'slug') else None
                    }
                    for cat in valid_categories
                ]
            }
            
            for category in valid_categories:
                category_id = str(category.id)
                
                if category_counts[category_id] < limit_per_category:
                    existing_ids = [p["id"] for p in categories_dict[category_id]]
                    if str(product.id) not in existing_ids:
                        categories_dict[category_id].append(product_data)
                        category_counts[category_id] += 1
                        
        result = {}
        for child_cat in child_categories:
            cat_id = str(child_cat.id)
            if cat_id in categories_dict:
                result[cat_id] = {
                    "category_id": cat_id,
                    "category_name": child_cat.name,
                    "category_slug": child_cat.slug if hasattr(child_cat, 'slug') else None,
                    "product_count": len(categories_dict[cat_id]),
                    "products": categories_dict[cat_id]
                }

        return result


    async def verify_parent_category(self, parent_category_id: str, session: AsyncSession):
        condition = [
            Categories.id == parent_category_id,
            Categories.deleted_at.is_(None),
            Categories.parent_id.is_(None)
        ]
        
        parent_category = await categories_repository.get_category(
            session=session,
            where_conditions=condition
        )
        
        if not parent_category:
            CategoriesException.not_found()
        
        return parent_category
    
    
    async def get_child_categories(self, parent_category_id: str, session: AsyncSession):
        condition = [
            Categories.parent_id == parent_category_id,
            Categories.deleted_at.is_(None)
        ]
        
        child_categories, _ = await categories_repository.get_all_categories(
            session=session,
            where_conditions=condition,
            skip=0,
            limit=1000
        )
        
        return child_categories
    
    
