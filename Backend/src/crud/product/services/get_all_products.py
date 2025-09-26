import uuid
from datetime import datetime
from typing import List

from sqlalchemy import exists
from sqlalchemy.orm import selectinload, joinedload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories, Product_Variant, Special_Offer, Brand, Material, Product_Material, \
    Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, desc, asc, or_, func, select, case
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.categories import CategoriesException
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


class GetAllProductsService:
    async def get_all_products_customer(self, category_identifier: str, filter_data: ProductFilterModel,
                                                session: AsyncSession, skip: int = 0, limit: int = 16):
        category = await self.find_category_by_identifier(category_identifier, session)

        if not category:
            CategoriesException.not_found()

        category_ids_to_filter = await self.get_category_ids_for_filter(category, session)

        is_category_uuid = await self.is_uuid(category_identifier)

        if is_category_uuid:
            if filter_data.category_ids:
                existing_categories = set(filter_data.category_ids)
                url_categories = set(category_ids_to_filter)
                combined_categories = existing_categories.intersection(url_categories)
                if combined_categories:
                    filter_data.category_ids = list(combined_categories)
                else:
                    filter_data.category_ids = []
            else:
                filter_data.category_ids = category_ids_to_filter
        else:
            if filter_data.category_slugs:
                selected_category_ids = await self.convert_slugs_to_ids(filter_data.category_slugs, session)

                existing_categories = set(selected_category_ids)

                url_categories = set(category_ids_to_filter)

                combined_categories = existing_categories.intersection(url_categories)

                if combined_categories:
                    filter_data.category_ids = list(combined_categories)
                else:
                    filter_data.category_ids = []
            else:
                filter_data.category_ids = category_ids_to_filter

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

        filters, order_by_clause = await self.filter_product(filter_data, session)
        products, total = await product_repository.get_all_product(filters, session, joins, skip, limit,
                                                                   order_by_clause)

        product_list = []
        for product in products:
            valid_categories = [cat for cat in product[0].categories if cat.deleted_at is None]

            active_variants = [
                variant for variant in product[0].product_variant
                if variant.deleted_at is None and variant.quantity > 0
            ]

            if not active_variants:
                continue

            offer = product[0].special_offer
            valid_offer = self._is_offer_valid(offer)
            offer_discount = offer.discount if valid_offer else None

            prices = [variant.price for variant in active_variants if variant.price is not None]
            price_min = min(prices) if prices else 0

            original_price = price_min
            discounted_price = original_price

            if offer_discount is not None:
                raw_discounted_price = original_price * (1 - offer_discount / 100)
                discounted_price = int(round(raw_discounted_price / 1000) * 1000)

            product_data = {
                "id": str(product[0].id),
                "name": product[0].name,
                "images": product[0].images,
                "description": product[0].description,
                "short_description": product[0].short_description,
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
                "avg_rating": product[0].avg_rating,
            }

            product_list.append(product_data)

        return {
            "data": product_list,
            "total": len(product_list)
        }

    async def find_category_by_identifier(self, identifier: str, session: AsyncSession):
        try:
            uuid.UUID(identifier)
            is_uuid = True
        except ValueError:
            is_uuid = False

        if is_uuid:
            condition = and_(Categories.id == identifier, Categories.deleted_at.is_(None))
        else:
            condition = and_(Categories.slug == identifier, Categories.deleted_at.is_(None))

        return await categories_repository.get_category(condition, session)

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

    async def get_category_ids_for_filter(self, category: Categories, session: AsyncSession):
        if category.parent_id is None:
            condition = [Categories.parent_id == category.id, Categories.deleted_at.is_(None)]
            child_categories, _ = await categories_repository.get_all_categories(condition, session, 0, 1000)

            child_category_ids = [str(row.id) for row in child_categories]

            return [str(category.id)] + child_category_ids
        else:
            return [str(category.id)]

    async def is_uuid(self, identifier: str):
        try:
            uuid.UUID(identifier)
            return True
        except ValueError:
            return False

    async def convert_slugs_to_ids(self, slugs: List[str], session: AsyncSession):
        if not slugs:
            return []

        condition = [
            Categories.slug.in_(slugs),
            Categories.deleted_at.is_(None)
        ]
        categories, _ = await categories_repository.get_all_categories(condition, session)

        category_ids = [str(category.id) for category in categories]

        return category_ids



# --------------------------------------------- Get all products admin ------------------------------------------------

    async def get_all_product_admin(self, filter_data: ProductFilterModel, session: AsyncSession, skip: int = 0,
                                            limit: int = 10,
                                            include_status: bool = True):

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
                Brand.logo,
                Brand.deleted_at
            ),

            selectinload(Product.materials).load_only(
                Material.id,
                Material.name,
                Material.slug,
                Material.deleted_at
            ),

            selectinload(Product.product_materials).load_only(
                Product_Material.id,
                Product_Material.material_id,
                Product_Material.percentage,
                Product_Material.deleted_at
            ),
        ]

        filters, order_by_clause = await self.filter_product(filter_data, session)
        products, total = await product_repository.get_all_product(filters, session, joins, skip, limit,
                                                                   order_by_clause)

        product_list = []
        for product in products:
            p = product[0]

            valid_categories = [cat for cat in p.categories if cat.deleted_at is None]

            active_variants = [
                variant for variant in p.product_variant
                if (variant.deleted_at is None and
                    variant.price is not None and variant.price >= 0 and
                    variant.quantity is not None and variant.quantity >= 0)
            ]

            variant_count = len(active_variants)

            price_range = None
            if active_variants:
                prices = [variant.price for variant in active_variants if
                          variant.price is not None and variant.price > 0]
                if prices:
                    price_range = {
                        "min": min(prices),
                        "max": max(prices)
                    }

            offer = p.special_offer
            offer_status = self._get_offer_status(offer)

            brand_data = None
            if p.brand and p.brand.deleted_at is None:
                brand_data = {
                    "id": str(p.brand.id),
                    "name": p.brand.name,
                    "slug": p.brand.slug,
                    "logo": p.brand.logo
                }

            materials_data = []
            if p.product_materials:
                for product_material in p.product_materials:
                    if product_material.deleted_at is None:
                        material = next(
                            (m for m in p.materials if m.id == product_material.material_id and m.deleted_at is None),
                            None
                        )
                        if material:
                            materials_data.append({
                                "id": str(material.id),
                                "name": material.name,
                                "slug": material.slug,
                                "percentage": product_material.percentage
                            })

            product_data = {
                "id": str(p.id),
                "name": p.name,
                "images": p.images if p.images else [],
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                        "parent_id": str(category.parent_id) if category.parent_id else None
                    }
                    for category in valid_categories
                ],
                "brand": brand_data,
                "materials": materials_data,
                "created_at": str(p.created_at) if p.created_at else "",
                "variant_count": variant_count,
                "price_range": price_range,
                "avg_rating": p.avg_rating if p.avg_rating is not None else 0,
                "offer_name": offer.name if offer else None,
                "offer_valid": offer_status["is_valid"] if offer else None,
                "offer_invalid_reason": offer_status["reason"] if offer and not offer_status["is_valid"] else None,
            }

            if include_status:
                product_data["status"] = p.status if p.status else "inactive"

            product_list.append(product_data)

        return {
            "data": product_list,
            "total": total[0]
        }



# ----------------------------------- Hàm dùng chung-----------------------------------------------------------

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

    async def filter_product(self, filter_data: ProductFilterModel, session: AsyncSession):
        filters = [Product.deleted_at.is_(None)]

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
