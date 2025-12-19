import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import exists
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories, Product_Variant, Special_Offer, Brand, Material, Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, desc, asc, or_, func, select, case
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.schemas.product import ProductFilterModel, SortBy

product_repository = ProductRepository()
categories_repository = CategoriesRepository()
cate_product_repository = CategoriesProductRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
size_repository = SizeRepository()

product_variant_service = ProductVariantService()
categories_product_service = CategoriesProductService()
color_service = ColorService()


class UtilProductsService:
    def is_offer_valid(self, offer: Optional[Special_Offer]) -> bool:
        if not offer or offer.deleted_at is not None:
            return False

        if offer.deleted_at is not None:
            return False

        now = datetime.now()
        if offer.start_time > now or offer.end_time < now:
            return False

        if offer.used_quantity >= offer.total_quantity:
            return False

        return True
    
    
    def is_valid_uuid(self, identifier: str) -> bool:
        try:
            uuid.UUID(identifier)
            return True
        except (ValueError, AttributeError):
            return False
        
        
    def get_offer_status(self, offer: Special_Offer) -> dict:
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


    async def filter_product(self, filter_data: ProductFilterModel, session: AsyncSession):
        filters = [Product.deleted_at.is_(None), Product.status == "active"]

        if filter_data.search:
            search_conditions = [
                Product.name.ilike(f"%{filter_data.search}%"),
                Product.tags.any(
                    and_(
                        Tag.name.ilike(f"%{filter_data.search}%"),
                        Tag.deleted_at.is_(None),
                        Tag.is_active == True
                    )
                )
            ]
            filters.append(or_(*search_conditions))

        if filter_data.category_ids:
            filters.append(
                Product.categories.any(
                    and_(
                        Categories.id.in_(filter_data.category_ids),
                        Categories.deleted_at.is_(None)
                    )
                )
            )

        if filter_data.brand_id:
            filters.append(
                and_(
                    Product.brand_id == filter_data.brand_id,
                    Product.brand.has(
                        and_(
                            Brand.deleted_at.is_(None),
                            Brand.is_active == True
                        )
                    )
                )
            )

        if filter_data.material_ids:
            filters.append(
                Product.materials.any(
                    and_(
                        Material.id.in_(filter_data.material_ids),
                        Material.deleted_at.is_(None),
                        Material.is_active == True
                    )
                )
            )

        if filter_data.min_price is not None or filter_data.max_price is not None:
            min_variant_price = (
                select(func.min(Product_Variant.price))
                .where(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None),
                    Product_Variant.quantity > 0
                )
                .correlate(Product)
                .scalar_subquery()
            )

            final_price = case(
                (
                    and_(
                        Product.special_offer_id.isnot(None),
                        exists().where(
                            and_(
                                Special_Offer.id == Product.special_offer_id,
                                Special_Offer.scope == "product",
                                Special_Offer.start_time <= func.now(),
                                Special_Offer.end_time >= func.now(),
                                Special_Offer.used_quantity < Special_Offer.total_quantity,
                                Special_Offer.deleted_at.is_(None)
                            )
                        )
                    ),
                    min_variant_price * (1 - (
                            select(Special_Offer.discount)
                            .where(Special_Offer.id == Product.special_offer_id)
                            .scalar_subquery() / 100.0
                    ))
                ),
                else_=min_variant_price
            )

            price_conditions = []
            if filter_data.min_price is not None:
                price_conditions.append(final_price >= filter_data.min_price)
            if filter_data.max_price is not None:
                price_conditions.append(final_price <= filter_data.max_price)

            if price_conditions:
                filters.extend(price_conditions)

        if filter_data.colors:
            filters.append(
                Product.product_variant.any(
                    and_(
                        Product_Variant.color_id.in_(filter_data.colors),
                        Product_Variant.deleted_at.is_(None),
                        Product_Variant.quantity > 0
                    )
                )
            )

        if filter_data.sizes:
            filters.append(
                Product.product_variant.any(
                    and_(
                        Product_Variant.size.in_(filter_data.sizes),
                        Product_Variant.deleted_at.is_(None),
                        Product_Variant.quantity > 0
                    )
                )
            )

        if filter_data.rating:
            rating_conditions = []
            for rating in filter_data.rating:
                rating_conditions.append(
                    and_(
                        Product.avg_rating >= rating,
                        Product.avg_rating < rating + 1
                    )
                )

            filters.append(or_(*rating_conditions))

        filters.append(
            exists().where(
                and_(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None),
                    Product_Variant.quantity > 0
                )
            )
        )

        order_by_clause = await self.filter_sort_product(filter_data.sort_by, session)
        return filters, order_by_clause


    async def filter_sort_product(self, sort_by: SortBy, session: AsyncSession):
        if not sort_by or sort_by == SortBy.newest:
            return desc(Product.created_at)

        elif sort_by == SortBy.price_asc:
            min_price_subquery = (
                select(func.min(Product_Variant.price))
                .where(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None),
                    Product_Variant.quantity > 0
                )
                .scalar_subquery()
            )
            return asc(min_price_subquery)

        elif sort_by == SortBy.price_desc:
            min_price_subquery = (
                select(func.min(Product_Variant.price))
                .where(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None),
                    Product_Variant.quantity > 0
                )
                .scalar_subquery()
            )
            return desc(min_price_subquery)

        elif sort_by == SortBy.name_asc:
            return asc(Product.name)

        elif sort_by == SortBy.name_desc:
            return desc(Product.name)

        elif sort_by == SortBy.best_seller:
            return desc(Product.total_sold)

        elif sort_by == SortBy.sale_desc:
            discount_subquery = (
                select(func.coalesce(Special_Offer.discount, 0))
                .where(
                    and_(
                        Special_Offer.id == Product.special_offer_id,
                        Special_Offer.start_time <= func.now(),
                        Special_Offer.end_time >= func.now(),
                        Special_Offer.used_quantity < Special_Offer.total_quantity,
                        Special_Offer.deleted_at.is_(None)
                    )
                )
                .scalar_subquery()
            )
            return desc(discount_subquery)

        else:
            return desc(Product.created_at)