from typing import Any, Dict, List, Optional, Set
from sqlalchemy import exists
from sqlalchemy.orm import selectinload, joinedload
from src.crud.product.services.utils import UtilProductsService
from src.database.models import Product, Categories, Product_Variant, Special_Offer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, desc
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.errors.categories import CategoriesException

product_repository = ProductRepository()
categories_repository = CategoriesRepository()

utils_service = UtilProductsService()


class GetAllProductsOfferService:
    MAX_PRODUCTS_PER_CATEGORY = 1000
    
    async def get_all_product_for_offer(self, categories_id: List[str], session: AsyncSession):
        valid_categories = await self.verify_categories(categories_id, session)
        
        if not valid_categories:
            return {}
        
        valid_category_ids = [str(cat.id) for cat in valid_categories]
        
        conditions = [
            Product.deleted_at.is_(None),
            Product.status == 'active',
            Product.categories.any(
                and_(
                    Categories.id.in_(valid_category_ids),
                    Categories.deleted_at.is_(None)
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
                Product_Variant.sku,
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
            limit=self.MAX_PRODUCTS_PER_CATEGORY * len(valid_category_ids),
            order_by=desc(Product.created_at)
        )

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
            offer_status = utils_service.get_offer_status(offer)

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


    async def verify_categories(self, category_ids: List[str], session: AsyncSession):
        if not category_ids:
            return []
        
        condition = [
            Categories.id.in_(category_ids),
            Categories.deleted_at.is_(None)
        ]
        
        categories, _ = await categories_repository.get_all_categories(
            session=session,
            where_conditions=condition,
            skip=0,
            limit=len(category_ids)
        )
        
        found_ids = {str(cat.id) for cat in categories}
        missing_ids = set(category_ids) - found_ids
        
        if missing_ids:
            CategoriesException.categories_not_exist(list(missing_ids))
        
        return categories
    
    
    async def group_products_by_category(self, products: List, valid_categories: List[Categories], 
                                          requested_category_ids: List[str]) -> Dict[str, Any]:
        categories_products = {}
        processed_products: Set[str] = set()
        
        for category in valid_categories:
            cat_id = str(category.id)
            categories_products[cat_id] = {
                "category_info": {
                    "id": cat_id,
                    "name": category.name,
                    "slug": category.slug if hasattr(category, 'slug') else None,
                    "parent_id": str(category.parent_id) if category.parent_id else None
                },
                "products": [],
                "total_products": 0
            }
            
        for product_tuple in products:
            p = product_tuple[0]
            product_id = str(p.id)

            valid_product_categories = [
                cat for cat in p.categories 
                if cat.deleted_at is None
            ]

            if not valid_product_categories:
                continue

            active_variants = [
                variant for variant in p.product_variant
                if (variant.deleted_at is None and
                    variant.quantity is not None and variant.quantity > 0 and
                    variant.price is not None and variant.price > 0)
            ]

            if not active_variants:
                continue

            prices = [v.price for v in active_variants]
            price_range = {
                "min": min(prices),
                "max": max(prices)
            }
            
            total_stock = sum(v.quantity for v in active_variants)

            offer = p.special_offer
            offer_status = utils_service.get_offer_status(offer)

            product_data = {
                "id": product_id,
                "name": p.name,
                "slug": p.slug,
                "images": p.images if p.images else [],
                "variant_count": len(active_variants),
                "total_stock": total_stock,
                "price_range": price_range,
                "avg_rating": float(p.avg_rating) if p.avg_rating else 0.0,
                "total_sold": p.total_sold if p.total_sold else 0,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "categories": [
                    {
                        "id": str(cat.id),
                        "name": cat.name,
                        "slug": cat.slug if hasattr(cat, 'slug') else None
                    }
                    for cat in valid_product_categories
                ],
                "current_offer": self.build_offer_info(offer, offer_status)
            }

            for cat in valid_product_categories:
                cat_id = str(cat.id)
                if cat_id in requested_category_ids:
                    existing_ids = [p["id"] for p in categories_products[cat_id]["products"]]
                    if product_id not in existing_ids:
                        categories_products[cat_id]["products"].append(product_data)
                        categories_products[cat_id]["total_products"] += 1

            processed_products.add(product_id)

        categories_products = {
            cat_id: data 
            for cat_id, data in categories_products.items() 
            if data["total_products"] > 0
        }

        return categories_products
    
    
    def build_offer_info(self, offer: Optional[Special_Offer], offer_status: Dict[str, Any]) -> Dict[str, Any]:
        if not offer:
            return {
                "id": None,
                "name": None,
                "type": None,
                "discount": None,
                "is_valid": None,
                "reason": None,
                "can_apply_new_offer": True
            }

        return {
            "id": str(offer.id),
            "name": offer.name,
            "type": offer.type,
            "discount": offer.discount,
            "is_valid": offer_status["is_valid"],
            "reason": offer_status["reason"],
            "start_time": offer.start_time.isoformat() if offer.start_time else None,
            "end_time": offer.end_time.isoformat() if offer.end_time else None,
            "used_quantity": offer.used_quantity,
            "total_quantity": offer.total_quantity,
            "can_apply_new_offer": not offer_status["is_valid"]
        }
        
        


