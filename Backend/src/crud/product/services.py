from sqlalchemy.orm import selectinload, load_only, joinedload, noload
from collections import defaultdict
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories_Product, Categories, Product_Variant, Color, Order_Detail, Evaluate, \
    Special_Offer, Size
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, desc, asc, or_, func, select
from datetime import datetime
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.color import ColorException
from src.errors.product import ProductException
from src.errors.categories import CategoriesException
from src.schemas.product import DeleteMultipleProductModel, ProductFilterModel, SortBy

product_repository = ProductRepository()
categories_repository = CategoriesRepository()
cate_product_repository = CategoriesProductRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
size_repository = SizeRepository()

product_variant_service = ProductVariantService()
categories_product_service = CategoriesProductService()
color_service = ColorService()


class ProductService:
    async def create_product(self, product_data, session: AsyncSession):
        if not product_data.name:
            ProductException.invalid_name()

        if not product_data.images:
            ProductException.invalid_images()

        if not product_data.categories_id:
            ProductException.invalid_categories()

        if not product_data.product_variant:
            ProductException.invalid_variant()

        try:
            category_ids = product_data.categories_id
            condition = [Categories.id.in_(category_ids), Categories.deleted_at.is_(None)]
            joins = [
                noload(Categories.categories_product),
                noload(Categories.products),
                noload(Categories.children),
                noload(Categories.parent),
            ]
            existing_categories, total = await categories_repository.get_all_categories(condition, session, 0, 1000, joins)

            existing_ids = {c.id for c in existing_categories}
            missing_ids = set(category_ids) - existing_ids
            if missing_ids:
                CategoriesException.categories_not_exist()

            color_ids = []
            for variant in product_data.product_variant:
                if variant.color_id:
                    if variant.color_name or variant.color_code:
                        ColorException.invalid_color_format()
                    color_ids.append(variant.color_id)
                elif variant.color_name and variant.color_code:
                    pass
                else:
                    ColorException.invalid_color_format()

            if color_ids:
                condition = [Color.id.in_(color_ids), Color.deleted_at.is_(None)]
                joins = [noload(Color.product_variant)]
                existing_colors, _ = await color_repository.get_all_color(condition, session, 0, 1000, joins)
                existing_color_ids = {str(c.id) for c in existing_colors}
                missing_color_ids = set(color_ids) - existing_color_ids
                if missing_color_ids:
                    ColorException.color_not_exists()

            new_product = await product_repository.create_product(product_data, session)

            await cate_product_repository.create_cate_product(existing_categories, new_product.id, session)

            await product_variant_repository.create_product_variant(product_data.product_variant, new_product.id,
                                                                    session)

            await session.commit()
            await session.refresh(new_product)

            product_dict = {
                "id": str(new_product.id),
                "name": new_product.name,
                "images": new_product.images,
                "description": new_product.description,
                "created_at": str(new_product.created_at),
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                        "parent_id": str(category.parent_id) if category.parent_id else None
                    } for category in existing_categories
                ],
                "status": new_product.status,
                "product_variant": [item.dict() for item in product_data.product_variant]
            }

            return product_dict
        except:
            await session.rollback()
            ProductException.invalid_create_product()

    async def get_detail_product(self, product_id: str, session: AsyncSession):
        condition = and_(Product.id == product_id, Product.deleted_at.is_(None))
        joins = [
            selectinload(Product.categories_product).options(
                noload(Categories_Product.product),
                joinedload(Categories_Product.categories).options(
                    noload(Categories.categories_product),
                    noload(Categories.products),
                    noload(Categories.children),
                    noload(Categories.parent)
                ).load_only(
                    Categories.id,
                    Categories.name,
                    Categories.parent_id,
                    Categories.deleted_at
                )
            ),

            selectinload(Product.product_variant).options(
                noload(Product_Variant.order_detail),
                noload(Product_Variant.evaluate),
                noload(Product_Variant.product),
                joinedload(Product_Variant.color).options(
                    noload(Color.product_variant)
                ).load_only(
                    Color.id,
                    Color.name,
                    Color.code,
                )
            ).load_only(
                Product_Variant.id,
                Product_Variant.size,
                Product_Variant.price,
                Product_Variant.quantity,
                Product_Variant.sku,
                Product_Variant.color_name,
                Product_Variant.color_code,
                Product_Variant.deleted_at
            ),

            selectinload(Product.special_offer).options(
                noload(Special_Offer.products)
            ).load_only(
                Special_Offer.id,
                Special_Offer.discount,
                Special_Offer.type
            ),

            noload(Product.order_detail),
            noload(Product.categories),
            noload(Product.evaluate),
        ]

        product_obj = await product_repository.get_product(condition, session, joins)

        if not product_obj:
            ProductException.not_found()

        product = product_obj[0]
        product_dict = product.model_dump()

        product_dict["categories"] = [
            {
                "id": str(cp.categories.id),
                "name": cp.categories.name,
                "parent_id": str(cp.categories.parent_id) if cp.categories.parent_id else None
            }
            for cp in product.categories_product
            if cp.categories
        ]

        offer = product.special_offer
        offer_type = offer.type if offer else None
        offer_discount = offer.discount if offer else None

        product_dict["product_variant"] = []
        for variant in product.product_variant:
            if variant.deleted_at is None:
                original_price = variant.price
                discounted_price = original_price

                if offer_type and offer_discount is not None:
                    if offer_type == "percent":
                        raw_discounted_price = original_price * (1 - offer_discount / 100)
                        discounted_price = int(round(raw_discounted_price / 1000) * 1000)
                    elif offer_type == "fixed":
                        raw_discounted_price = max(0, original_price - offer_discount)
                        discounted_price = int(round(raw_discounted_price / 1000) * 1000)

                variant_data = {
                    "id": str(variant.id),
                    "size": variant.size,
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

                product_dict["product_variant"].append(variant_data)

        return product_dict

    async def get_detail_product_admin_service(self, product_id: str, session: AsyncSession):
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
            "categories": product["categories"],
            "status": product["status"],
            "product_variant": product_variant
        }

        return product_dict

    async def get_detail_product_customer_service(self, product_id: str, session: AsyncSession):
        product = await self.get_detail_product(product_id, session)

        if product is None:
            ProductException.not_found()

        product_variant = [
            {
                "id": str(item["id"]),
                "size": item["size"],
                "color": item["color"],
                "price": item["price"],
                "quantity": item["quantity"],
            }
            for item in product["product_variant"]
        ]

        product_dict = {
            "id": str(product["id"]),
            "name": product["name"],
            "images": product["images"],
            "description": product["description"],
            "categories": product["categories"],
            "product_variant": product_variant
        }

        return product_dict

    async def get_products_popular_service(self, parent_category_id: str, session: AsyncSession,
                                           limit_per_category: int = 12):
        conditions = and_(
            Product.deleted_at.is_(None),
            Product.status == "active",
            Categories.deleted_at.is_(None),
            Categories_Product.deleted_at.is_(None),
            Product_Variant.deleted_at.is_(None),
            Categories.parent_id == parent_category_id
        )

        products = await product_repository.get_popular_products_by_category(conditions, session, limit_per_category)

        categories_dict = defaultdict(list)

        for product in products:
            offer_type = product.type_offer if product.type_offer else None
            offer_discount = product.discount if product.discount else None

            original_price = product.min_price
            discounted_price = original_price

            if offer_type and offer_discount is not None:
                if offer_type == "percent":
                    raw_discounted_price = original_price * (1 - offer_discount / 100)
                    discounted_price = int(round(raw_discounted_price / 1000) * 1000)
                elif offer_type == "fixed":
                    raw_discounted_price = max(0, original_price - offer_discount)
                    discounted_price = int(round(raw_discounted_price / 1000) * 1000)

            categories_dict[str(parent_category_id)].append({
                "id": str(product.product_id),
                "name": product.product_name,
                "images": product.images,
                "avg_rating": product.avg_rating,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "categories": product.categories
            })

        return categories_dict


    async def get_filters_info_service(self, category_id: str, session: AsyncSession):
        condition_parent_category = and_(Categories.id == category_id, Categories.deleted_at.is_(None))
        joins_parent_category = [
            noload(Categories.categories_product),
            noload(Categories.products),
            noload(Categories.children),
            noload(Categories.parent),
        ]
        parent_category = await categories_repository.get_category(condition_parent_category, session, joins_parent_category)
        if not parent_category:
            CategoriesException.not_found()

        condition_child_categories = and_(Categories.parent_id == category_id, Categories.deleted_at.is_(None))
        joins_child_categories = [
            noload(Categories.categories_product),
            noload(Categories.products),
            noload(Categories.children),
            noload(Categories.parent),
        ]
        child_categories, _ = await categories_repository.get_all_categories(condition_child_categories, session, 0, 1000,
                                                                          joins_child_categories)

        type_size = parent_category.type_size
        sizes = await size_repository.get_all_size(Size.type == type_size, session)

        join_colors = [noload(Color.product_variant)]
        colors, _ = await color_repository.get_all_color([Color.deleted_at.is_(None)], session, 0, 1000, join_colors)

        return {
            "categories": [
                {"id": str(category.id), "name": category.name}
                for category in child_categories
            ],
            "sizes": [
                {"id": str(size.id), "name": size.name}
                for size in sizes
            ],
            "colors": [
                {"id": str(color.id), "name": color.name}
                for color in colors
            ]
        }

    async def get_latest_products_service(self, session: AsyncSession, limit_per_category: int = 12):
        condition = [Product.deleted_at.is_(None), Product.status == "active"]
        order_by = desc(Product.created_at)

        joins = [
            selectinload(Product.categories).options(
                noload(Categories.categories_product),
                noload(Categories.products),
                noload(Categories.children),
                joinedload(Categories.parent).options(
                    noload(Categories.categories_product),
                    noload(Categories.products),
                    noload(Categories.children),
                    noload(Categories.parent)
                )
            ).load_only(
                Categories.id,
                Categories.name,
                Categories.parent_id,
                Categories.deleted_at
            ),

            selectinload(Product.product_variant).options(
                noload(Product_Variant.order_detail),
                noload(Product_Variant.evaluate),
                noload(Product_Variant.product),
                noload(Product_Variant.color)
            ).load_only(
                Product_Variant.id,
                Product_Variant.price,
                Product_Variant.deleted_at
            ),

            selectinload(Product.special_offer).options(
                noload(Special_Offer.products)
            ).load_only(
                Special_Offer.id,
                Special_Offer.discount,
                Special_Offer.type
            ),

            noload(Product.order_detail),
            noload(Product.categories_product),
            noload(Product.evaluate),
        ]

        products, _ = await product_repository.get_all_product(condition, session, joins, skip=0,
                                                               limit=limit_per_category, order_by_clause=order_by)

        product_list = []
        for product in products:
            valid_categories = [cat for cat in product[0].categories if cat.deleted_at is None]

            active_variants = [
                variant for variant in product[0].product_variant if variant.deleted_at is None
            ]

            offer = product[0].special_offer
            offer_type = offer.type if offer else None
            offer_discount = offer.discount if offer else None

            price_min = 0
            if active_variants:
                prices = [variant.price for variant in active_variants if variant.price is not None]
                if prices:
                    price_min = min(prices)

            original_price = price_min
            discounted_price = original_price

            if offer_type and offer_discount is not None:
                if offer_type == "percent":
                    raw_discounted_price = original_price * (1 - offer_discount / 100)
                    discounted_price = int(round(raw_discounted_price / 1000) * 1000)
                elif offer_type == "fixed":
                    raw_discounted_price = max(0, original_price - offer_discount)
                    discounted_price = int(round(raw_discounted_price / 1000) * 1000)

            product_data = {
                "id": str(product[0].id),
                "name": product[0].name,
                "images": product[0].images,
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

        return product_list

    async def get_top_discount_service(self, session: AsyncSession, limit: int = 12):
        products = await product_repository.get_top_discount(session, limit)

        product_list = []
        for product in products:
            offer_discount = product.discount if product.discount else None

            original_price = product.min_price
            discounted_price = original_price

            if offer_discount is not None:
                raw_discounted_price = original_price * (1 - offer_discount / 100)
                discounted_price = int(round(raw_discounted_price / 1000) * 1000)

            product_list.append({
                "id": str(product.product_id),
                "name": product.product_name,
                "images": product.images,
                "avg_rating": product.avg_rating,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "categories": product.categories
            })

        return product_list

    async def get_all_products_customer_service(self, category_id: str, filter_data: ProductFilterModel, session: AsyncSession, skip: int = 0, limit: int = 16):
        condition_cate = and_(Categories.id == category_id,Categories.deleted_at.is_(None))
        joins = [
            noload(Categories.categories_product),
            noload(Categories.products),
            noload(Categories.children),
            noload(Categories.parent),
        ]
        category = await categories_repository.get_category(condition_cate, session, joins)

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
                noload(Categories.categories_product),
                noload(Categories.products),
                noload(Categories.children),
                joinedload(Categories.parent).options(
                    noload(Categories.categories_product),
                    noload(Categories.products),
                    noload(Categories.children),
                    noload(Categories.parent)
                )
            ).load_only(
                Categories.id,
                Categories.name,
                Categories.parent_id,
                Categories.deleted_at
            ),

            selectinload(Product.product_variant).options(
                noload(Product_Variant.order_detail),
                noload(Product_Variant.evaluate),
                noload(Product_Variant.product),
                noload(Product_Variant.color)
            ).load_only(
                Product_Variant.id,
                Product_Variant.price,
                Product_Variant.deleted_at
            ),

            selectinload(Product.special_offer).options(
                noload(Special_Offer.products)
            ).load_only(
                Special_Offer.id,
                Special_Offer.discount,
                Special_Offer.type
            ),

            noload(Product.order_detail),
            noload(Product.categories_product),
            noload(Product.evaluate),
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
            joins = [noload(Categories.products), noload(Categories.categories_product), noload(Categories.children), noload(Categories.parent)]
            child_categories, _ = await categories_repository.get_all_categories(condition, session, 0, 1000, joins)

            child_category_ids = [str(row.id) for row in child_categories]

            return [str(category.id)] + child_category_ids
        else:
            return [str(category.id)]


    async def get_all_product_admin_service(self, filter_data: ProductFilterModel, session: AsyncSession, skip: int = 0,
                                            limit: int = 10,
                                            include_status: bool = True):

        joins = [
            selectinload(Product.categories).options(
                noload(Categories.categories_product),
                noload(Categories.products),
                noload(Categories.children),
                joinedload(Categories.parent).options(
                    noload(Categories.categories_product),
                    noload(Categories.products),
                    noload(Categories.children),
                    noload(Categories.parent)
                )
            ).load_only(
                Categories.id,
                Categories.name,
                Categories.parent_id,
                Categories.deleted_at
            ),

            selectinload(Product.product_variant).options(
                noload(Product_Variant.order_detail),
                noload(Product_Variant.evaluate),
                noload(Product_Variant.product),
                noload(Product_Variant.color)
            ).load_only(
                Product_Variant.id,
                Product_Variant.price,
                Product_Variant.deleted_at
            ),

            selectinload(Product.special_offer).options(
                noload(Special_Offer.products)
            ).load_only(
                Special_Offer.id,
                Special_Offer.name,
            ),

            noload(Product.order_detail),
            noload(Product.evaluate),
            noload(Product.categories_product),
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
            price_conditions = []
            if filter_data.min_price is not None:
                price_conditions.append(Product_Variant.price >= filter_data.min_price)
            if filter_data.max_price is not None:
                price_conditions.append(Product_Variant.price <= filter_data.max_price)

            filters.append(
                Product.product_variant.any(
                    and_(
                        *price_conditions,
                        Product_Variant.deleted_at.is_(None)
                    )
                )
            )

        if filter_data.colors:
            filters.append(
                Product.product_variant.any(
                    and_(
                        Product_Variant.color_name.in_(filter_data.colors),
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


    async def update_product(self, product_id: str, product_data, session: AsyncSession):
        try:
            condition = and_(Product.id == product_id)
            joins = [
                noload(Product.order_detail),
                noload(Product.categories),
                noload(Product.evaluate),
                noload(Product.special_offer),
                noload(Product.categories_product),
                noload(Product.product_variant),
            ]
            product_to_update = await product_repository.get_product(condition, session, joins)

            if not product_to_update:
                ProductException.not_found()

            product_data_dict = product_data.model_dump(exclude_none=True)

            deleted_ids = product_data_dict.pop("deleted_variant_ids", [])
            if deleted_ids:
                for variant_id in deleted_ids:
                    condition = and_(Product_Variant.id == variant_id)
                    await product_variant_repository.delete_product_variant(condition, session)
                await session.commit()

            new_variants = product_data_dict.pop("product_variant", None)
            new_category_ids = product_data_dict.pop("categories_id", None)

            if not product_data_dict and new_variants is None and new_category_ids is None:
                ProductException.not_enough_infor_to_update()

            if new_variants is not None:
                await product_variant_service.update_product_variant(product_id, new_variants, session)

            if new_category_ids is not None:
                await categories_product_service.update_categories_product(product_id, new_category_ids, session)

            for k, v in product_data_dict.items():
                setattr(product_to_update[0], k, v)

            product_to_update[0].updated_at = datetime.now()

            await session.flush()
            await session.commit()

            return await self.updated_product_response(product_id, session)
        except:
            await session.rollback()
            raise

    async def updated_product_response(self, product_id: str, session: AsyncSession):
        response = await self.get_detail_product(product_id, session)

        product_variant = [
            {
                "id": str(item["id"]),
                "size": item["size"],
                "color_id": str(item.get("color_id")),
                "color_name": item.get("color_name"),
                "color_code": item.get("color_code"),
                "price": item["price"],
                "quantity": item["quantity"],
                "sku": item["sku"]
            }
            for item in response["product_variant"]
        ]

        product_dict = {
            "id": str(response["id"]),
            "name": response["name"],
            "images": response["images"],
            "description": response["description"],
            "categories": response["categories"],
            "product_variant": product_variant
        }

        return product_dict

    async def delete_product(self, product_id: str, session: AsyncSession):
        condition = and_(Product.id == product_id)
        product_delete = await product_repository.delete_product(condition, session)
        return product_delete

    async def delete_multiple_product(self, data: DeleteMultipleProductModel, session: AsyncSession):
        product_ids = await product_repository.delete_multiple_product(data, session)
        return product_ids

    async def count_all_products(self, session: AsyncSession):
        count_products = await product_repository.count_products(None, session)

        if count_products is None:
            ProductException.fail_count_products()

        return count_products[0]

    async def get_all_product_for_offer(self, categories_id: list, session: AsyncSession):
        joins = [
            selectinload(Product.categories).options(
                noload(Categories.categories_product),
                noload(Categories.products),
                noload(Categories.children),
                joinedload(Categories.parent).options(
                    noload(Categories.categories_product),
                    noload(Categories.products),
                    noload(Categories.children),
                    noload(Categories.parent)
                )
            ).load_only(
                Categories.id,
                Categories.name,
                Categories.parent_id,
                Categories.deleted_at
            ),
            noload(Product.product_variant),
            noload(Product.order_detail),
            noload(Product.evaluate),
            noload(Product.categories_product),
            noload(Product.special_offer)
        ]

        conditions = [
            Product.deleted_at.is_(None),
            Product.status == 'active',
            Product.categories.any(
                and_(
                    Categories.id.in_(categories_id),
                    Categories.deleted_at.is_(None)
                )
            )
        ]

        products, _ = await product_repository.get_all_product(conditions, session, joins, 0, 1000)

        categories_products = {}
        processed_products = set()

        for product in products:
            product_id = str(product[0].id)

            if product_id in processed_products:
                continue

            valid_categories = [cat for cat in product[0].categories if cat.deleted_at is None]

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
