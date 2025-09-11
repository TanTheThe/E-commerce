from sqlalchemy.orm import selectinload, joinedload
from collections import defaultdict
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.database.models import Product, Categories_Product, Categories, Product_Variant, Color, Special_Offer, Size
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, desc
from datetime import datetime
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.product import ProductException
from src.errors.categories import CategoriesException
from src.schemas.product import DeleteMultipleProductModel

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


class ProductService:
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
                "total_sold": product.total_sold,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "categories": product.categories
            })

        return categories_dict


    async def get_filters_info_service(self, category_id: str, session: AsyncSession):
        condition_parent_category = and_(Categories.id == category_id, Categories.deleted_at.is_(None))
        parent_category = await categories_repository.get_category(condition_parent_category, session)
        if not parent_category:
            CategoriesException.not_found()

        condition_child_categories = [Categories.parent_id == category_id, Categories.deleted_at.is_(None)]
        child_categories, _ = await categories_repository.get_all_categories(condition_child_categories, session, 0, 1000,)

        type_size = parent_category.type_size
        sizes = await size_repository.get_all_size(Size.type == type_size, session)

        colors, _ = await color_repository.get_all_color([Color.deleted_at.is_(None)], session, 0, 1000)

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

        return product_list


    async def get_related_products_service(self, product_id: str, session: AsyncSession, limit_per_category: int = 12,
                                           price_range: float = 0.4):
        condition_product = and_(Product.id == product_id, Product.deleted_at.is_(None), Product.status == "active")
        joins_product = [
            selectinload(Product.categories).load_only(Categories.id),
            selectinload(Product.product_variant).load_only(
                Product_Variant.id,
                Product_Variant.price,
                Product_Variant.deleted_at
            )
        ]
        current_product_tuple = await product_repository.get_product(condition_product, session, joins_product)
        current_product = current_product_tuple[0]

        if not current_product:
            return []

        active_variants = [
            variant for variant in current_product.product_variant if variant.deleted_at is None
        ]
        current_price = 0
        if active_variants:
            prices = [variant.price for variant in active_variants if variant.price is not None]
            if prices:
                current_price = min(prices)

        min_price = current_price * (1 - price_range)
        max_price = current_price * (1 + price_range)

        condition = [
            Product.deleted_at.is_(None),
            Product.status == "active",
            Product.id != product_id,
            Product.categories.any(Categories.id.in_([c.id for c in current_product.categories]))
        ]
        order_by = desc(Product.created_at)

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

        products, _ = await product_repository.get_all_product(condition, session, joins, skip=0,
                                                               limit=limit_per_category, order_by_clause=order_by)

        product_list = []
        for product in products:
            p = product[0]

            valid_categories = [cat for cat in p.categories if cat.deleted_at is None]
            active_variants = [v for v in p.product_variant if v.deleted_at is None]
            prices = [v.price for v in active_variants if v.price is not None]

            if not prices:
                continue

            price_min = min(prices)

            if price_min < min_price or price_min > max_price:
                continue

            offer = p.special_offer
            offer_type = offer.type if offer else None
            offer_discount = offer.discount if offer else None

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
                "id": str(p.id),
                "name": p.name,
                "images": p.images,
                "total_sold": p.total_sold,
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
                "total_sold": product.total_sold,
                "original_price": original_price,
                "discounted_price": discounted_price,
                "categories": product.categories
            })

        return product_list

    async def update_product(self, product_id: str, product_data, session: AsyncSession):
        try:
            condition = and_(Product.id == product_id)
            joins = [
                selectinload(Product.categories_product).options(
                    joinedload(Categories_Product.categories).load_only(
                        Categories.id,
                        Categories.name,
                        Categories.parent_id,
                        Categories.deleted_at
                    )
                ),

                selectinload(Product.product_variant).options(
                    joinedload(Product_Variant.color).load_only(
                        Color.id,
                        Color.name,
                        Color.code,
                    )
                ).load_only(
                    Product_Variant.id,
                    Product_Variant.size,
                    Product_Variant.price,
                    Product_Variant.quantity,
                    Product_Variant.image,
                    Product_Variant.sku,
                    Product_Variant.color_name,
                    Product_Variant.color_code,
                    Product_Variant.deleted_at
                ),
            ]
            product_to_update = await product_repository.get_product(condition, session, joins)

            if not product_to_update:
                ProductException.not_found()

            product_data_dict = product_data.model_dump()

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
        response = await get_detail_product_service.get_detail_product(product_id, session)

        product_variant = [
            {
                "id": str(item["id"]),
                "size": item["size"],
                "image": item["image"],
                "color_id": str(item.get("color_id")),
                "color_name": item.get("color_name"),
                "color_code": item.get("color_code"),
                "price": item["original_price"],
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
            "short_description": response["short_description"],
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
                joinedload(Categories.parent)
            ).load_only(
                Categories.id,
                Categories.name,
                Categories.parent_id,
                Categories.deleted_at
            ),
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
