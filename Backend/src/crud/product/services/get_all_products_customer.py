import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import selectinload, joinedload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.utils import UtilProductsService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories, Product_Variant, Special_Offer, Brand, Material
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.categories import CategoriesException
from src.schemas.product import ProductFilterModel

product_repository = ProductRepository()
categories_repository = CategoriesRepository()
cate_product_repository = CategoriesProductRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
size_repository = SizeRepository()

product_variant_service = ProductVariantService()
categories_product_service = CategoriesProductService()
color_service = ColorService()
utils_service = UtilProductsService()


class GetAllProductsCustomerService:
    async def get_all_products_customer(self, category_identifier: str, filter_data: ProductFilterModel,
                                                session: AsyncSession, skip: int = 0, limit: int = 16):
        category = await self.find_category_by_identifier(category_identifier, session)
        if not category:
            CategoriesException.not_found()

        category_ids_to_filter = await self.get_category_ids_for_filter(category, session)
        
        filter_data.category_ids = await self.resolve_category_filters(
            category_identifier, category_ids_to_filter, filter_data, session
        )

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
            selectinload(Product.brand).load_only(
                Brand.id,
                Brand.name,
                Brand.deleted_at
            ),
            selectinload(Product.materials).load_only(
                Material.id,
                Material.name,
                Material.deleted_at
            ),
        ]

        filters, order_by_clause = await utils_service.filter_product(filter_data, session)
        
        products, total = await product_repository.get_all_product(session=session, where_conditions=filters, options=joins,
                                                                   skip=skip, limit=limit, order_by=order_by_clause)

        product_list = []
        for product_tuple in products:
            product = product_tuple[0]
            
            valid_categories = [
                cat for cat in product.categories 
                if cat.deleted_at is None
            ]

            active_variants = [
                variant for variant in product.product_variant
                if variant.deleted_at is None and variant.quantity > 0
            ]

            if not active_variants:
                continue

            offer = product.special_offer
            prices = [v.price for v in active_variants if v.price is not None]
            
            if not prices:
                continue
            
            price_min = min(prices)
            original_price = price_min
            discounted_price = price_min
            
            if utils_service.is_offer_valid(offer):
                discount_multiplier = 1 - (offer.discount / 100)
                raw_discounted = original_price * discount_multiplier
                discounted_price = int(round(raw_discounted / 1000) * 1000)

            product_data = {
                "id": str(product.id),
                "name": product.name,
                "images": product.images,
                "description": product.description,
                "short_description": product.short_description,
                "total_sold": product.total_sold,
                "slug": product.slug,
                "categories": [
                    {
                        "id": str(cat.id),
                        "name": cat.name,
                    }
                    for cat in valid_categories
                ],
                "original_price": original_price,
                "discounted_price": discounted_price,
                "discount_percentage": offer.discount if utils_service.is_offer_valid(offer) else 0,
                "avg_rating": float(product.avg_rating) if product.avg_rating else 0.0,
                "brand": {
                    "id": str(product.brand.id),
                    "name": product.brand.name
                } if product.brand and product.brand.deleted_at is None else None
            }

            product_list.append(product_data)

        return {
            "data": product_list,
            "total": len(product_list)
        }


    async def find_category_by_identifier(self, identifier: str, session: AsyncSession):
        is_uuid = utils_service.is_valid_uuid(identifier)

        if is_uuid:
            condition = [Categories.id == identifier, Categories.deleted_at.is_(None)]
        else:
            condition = [Categories.slug == identifier, Categories.deleted_at.is_(None)]

        return await categories_repository.get_category(session=session, where_conditions=condition)
        
    
    async def resolve_category_filters(self, category_identifier: str, category_ids_to_filter: List[str], 
                                       filter_data: ProductFilterModel, session: AsyncSession) -> List[str]:
        is_category_uuid = utils_service.is_valid_uuid(category_identifier)

        if is_category_uuid:
            if filter_data.category_ids:
                url_set = set(category_ids_to_filter)
                filter_set = set(filter_data.category_ids)
                intersection = url_set.intersection(filter_set)
                return list(intersection) if intersection else []
            else:
                return category_ids_to_filter
        else:
            if filter_data.category_slugs:
                selected_ids = await self.convert_slugs_to_ids(
                    filter_data.category_slugs, session
                )
                
                url_set = set(category_ids_to_filter)
                filter_set = set(selected_ids)
                intersection = url_set.intersection(filter_set)
                return list(intersection) if intersection else []
            else:
                return category_ids_to_filter


    async def get_category_ids_for_filter(self, category: Categories, session: AsyncSession):
        if category.parent_id is None:
            condition = [Categories.parent_id == category.id, Categories.deleted_at.is_(None)]
            child_categories, _ = await categories_repository.get_all_categories(session=session, where_conditions=condition, skip=0, limit=1000)

            child_category_ids = [str(row.id) for row in child_categories]

            return [str(category.id)] + child_category_ids
        else:
            return [str(category.id)]


    async def convert_slugs_to_ids(self, slugs: List[str], session: AsyncSession):
        if not slugs:
            return []

        condition = [
            Categories.slug.in_(slugs),
            Categories.deleted_at.is_(None)
        ]
        categories, _ = await categories_repository.get_all_categories(session=session, where_conditions=condition)

        category_ids = [str(category.id) for category in categories]

        return category_ids