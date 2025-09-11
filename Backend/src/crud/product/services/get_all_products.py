from sqlalchemy import exists
from sqlalchemy.orm import selectinload, joinedload
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories, Product_Variant, Special_Offer
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
    async def get_all_products_customer_service(self, category_id: str, filter_data: ProductFilterModel,
                                                session: AsyncSession, skip: int = 0, limit: int = 16):
        condition_cate = and_(Categories.id == category_id, Categories.deleted_at.is_(None))
        category = await categories_repository.get_category(condition_cate, session)

        if not category:
            CategoriesException.not_found()

        category_ids_to_filter = await self.get_category_ids_for_filter(category, session)

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
                Product_Variant.deleted_at
            ),

            selectinload(Product.special_offer).load_only(
                Special_Offer.id,
                Special_Offer.discount,
                Special_Offer.type
            ),
        ]

        filters, order_by_clause = await self.filter_product(filter_data, session)
        products, total = await product_repository.get_all_product(filters, session, joins, skip, limit,
                                                                   order_by_clause)

        product_list = []
        for product in products:
            valid_categories = [cat for cat in product[0].categories if cat.deleted_at is None]

            active_variants = [
                variant for variant in product[0].product_variant if variant.deleted_at is None
            ]

            offer = product[0].special_offer
            offer_discount = offer.discount if offer else None

            price_min = 0
            if active_variants:
                prices = [variant.price for variant in active_variants if variant.price is not None]
                if prices:
                    price_min = min(prices)

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
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                    }
                    for category in valid_categories
                ],
                "original_price": original_price,
                "discounted_price": discounted_price,
                "avg_rating": product[0].avg_rating
            }

            product_list.append(product_data)

        return {
            "data": product_list,
            "total": total[0]
        }

    async def get_category_ids_for_filter(self, category: Categories, session: AsyncSession):
        if category.parent_id is None:
            condition = [Categories.parent_id == category.id, Categories.deleted_at.is_(None)]
            child_categories, _ = await categories_repository.get_all_categories(condition, session, 0, 1000)

            child_category_ids = [str(row.id) for row in child_categories]

            return [str(category.id)] + child_category_ids
        else:
            return [str(category.id)]

    async def get_all_product_admin_service(self, filter_data: ProductFilterModel, session: AsyncSession, skip: int = 0,
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
                Product_Variant.deleted_at
            ),

            selectinload(Product.special_offer).load_only(
                Special_Offer.id,
                Special_Offer.name,
            ),
        ]

        filters, order_by_clause = await self.filter_product(filter_data, session)
        products, total = await product_repository.get_all_product(filters, session, joins, skip, limit,
                                                                   order_by_clause)

        product_list = []
        for product in products:
            valid_categories = [cat for cat in product[0].categories if cat.deleted_at is None]

            active_variants = [
                variant for variant in product[0].product_variant if variant.deleted_at is None
            ]
            variant_count = len(active_variants)

            price_range = None
            if active_variants:
                prices = [variant.price for variant in active_variants if variant.price is not None]
                if prices:
                    price_range = {
                        "min": min(prices),
                        "max": max(prices)
                    }

            product_data = {
                "id": str(product[0].id),
                "name": product[0].name,
                "images": product[0].images,
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                        "parent_id": str(category.parent_id) if category.parent_id else None
                    }
                    for category in valid_categories
                ],
                "created_at": str(product[0].created_at),
                "variant_count": variant_count,
                "price_range": price_range,
                "avg_rating": product[0].avg_rating,
                "offer_name": product[0].special_offer.name if product[0].special_offer else None,
            }
            if include_status:
                product_data["status"] = product[0].status

            product_list.append(product_data)

        return {
            "data": product_list,
            "total": total[0]
        }

    async def filter_product(self, filter_data: ProductFilterModel, session: AsyncSession):
        filters = [Product.deleted_at.is_(None)]

        if filter_data.search:
            filters.append(Product.name.ilike(f"%{filter_data.search}%"))

        if filter_data.category_ids:
            filters.append(
                Product.categories.any(
                    and_(
                        Categories.id.in_(filter_data.category_ids),
                        Categories.deleted_at.is_(None)
                    )
                )
            )

        if filter_data.min_price is not None or filter_data.max_price is not None:
            min_variant_price = (
                select(func.min(Product_Variant.price))
                .where(
                    Product_Variant.product_id == Product.id,
                    Product_Variant.deleted_at.is_(None)
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
                        Product_Variant.deleted_at.is_(None)
                    )
                )
            )

        if filter_data.sizes:
            filters.append(
                Product.product_variant.any(
                    and_(
                        Product_Variant.size.in_(filter_data.sizes),
                        Product_Variant.deleted_at.is_(None)
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

        order_by_clause = await self.filter_sort_product(filter_data.sort_by, session)
        return filters, order_by_clause

    async def filter_sort_product(self, sort_by: SortBy, session: AsyncSession):
        if not sort_by or sort_by == SortBy.newest:
            return desc(Product.created_at)

        elif sort_by == SortBy.price_asc:
            min_price_subquery = (
                select(func.min(Product_Variant.price))
                .where(Product_Variant.product_id == Product.id)
                .where(Product_Variant.deleted_at.is_(None))
                .scalar_subquery()
            )
            return asc(min_price_subquery)

        elif sort_by == SortBy.price_desc:
            min_price_subquery = (
                select(func.min(Product_Variant.price))
                .where(Product_Variant.product_id == Product.id)
                .where(Product_Variant.deleted_at.is_(None))
                .scalar_subquery()
            )
            return desc(min_price_subquery)

        elif sort_by == SortBy.name_asc:
            return asc(Product.name)

        elif sort_by == SortBy.name_desc:
            return desc(Product.name)

        elif sort_by == SortBy.best_seller:
            pass

        elif sort_by == SortBy.sale_desc:
            discount_subquery = (
                select(func.coalesce(Special_Offer.discount, 0))
                .where(Special_Offer.id == Product.special_offer_id)
                .where(Special_Offer.deleted_at.is_(None))
                .scalar_subquery()
            )
            return desc(discount_subquery)

        else:
            return desc(Product.created_at)
