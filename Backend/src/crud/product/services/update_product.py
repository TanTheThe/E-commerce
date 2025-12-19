from typing import List
from sqlalchemy.orm import selectinload, joinedload
from src.crud.brand.repositories import BrandRepository
from src.crud.color.repositories import ColorRepository
from src.crud.color.services import ColorService
from src.crud.material.repositories import MaterialRepository
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product_material.repositories import ProductMaterialRepository
from src.crud.product_tag.repositories import ProductTagRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.size.repositories import SizeRepository
from src.crud.tag.repositories import TagRepository
from src.database.models import Product, Categories_Product, Categories, Product_Variant, Color, Brand, Material, \
    Product_Material, Tag, Product_Tag, Order_Detail, Order
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.brand import BrandException
from src.errors.categories import CategoriesException
from src.errors.color import ColorException
from src.errors.material import MaterialException
from src.errors.product import ProductException
from src.errors.tag import TagException
import logging


logger = logging.getLogger(__name__)

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
brand_repository = BrandRepository()
product_material_repository = ProductMaterialRepository()
material_repository = MaterialRepository()
product_tag_repository = ProductTagRepository()
tag_repository = TagRepository()


class UpdateProductService:
    async def update_product(self, product_id: str, product_data, session: AsyncSession):
        try:
            condition = [Product.id == product_id, Product.deleted_at.is_(None)]
            options = [
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
            product_to_update = await product_repository.get_product(session=session, where_conditions=condition, options=options)

            if not product_to_update:
                ProductException.not_found()

            product_data_dict = product_data.model_dump()

            deleted_ids = product_data_dict.pop("deleted_variant_ids", [])
            new_variants = product_data_dict.pop("product_variant", None)
            new_category_ids = product_data_dict.pop("categories_id", None)
            new_brand_id = product_data_dict.pop("brand_id", None)
            new_materials = product_data_dict.pop("materials", None)
            new_tags_id = product_data_dict.pop("tags_id", None)

            if (not product_data_dict and new_variants is None and new_category_ids is None
                    and new_brand_id is None and new_materials is None and new_tags_id is None
                    and not deleted_ids):
                ProductException.not_enough_infor_to_update()

            if deleted_ids:
                await self.validate_and_delete_variants(product_id, deleted_ids, product_to_update[0], session)

            if new_variants is not None:
                await self.validate_variants(new_variants, product_id, session)
                await product_variant_service.update_product_variant(product_id, new_variants, session)

            if new_category_ids is not None:
                await self.validate_categories(new_category_ids, session)
                await categories_product_service.update_categories_product(product_id, new_category_ids, session)

            if new_brand_id is not None:
                if new_brand_id:
                    brand_condition = [
                        Brand.id == new_brand_id,
                        Brand.deleted_at.is_(None),
                        Brand.is_active == True
                    ]
                    brand_exists = await brand_repository.get_brand(session=session, where_conditions=brand_condition)
                    if not brand_exists:
                        BrandException.brand_not_found()

                product_to_update[0].brand_id = new_brand_id

            if new_materials is not None:
                await self.validate_and_update_materials(product_id, new_materials, session)

            if new_tags_id is not None:
                await self.validate_and_update_tags(product_id, new_tags_id, session)

            if product_data_dict:
                self.validate_basic_fields(product_data_dict)
                for k, v in product_data_dict.items():
                    setattr(product_to_update[0], k, v)

            product_to_update[0].updated_at = datetime.now()

            await session.flush()

            await self.validate_has_active_variants(product_id, session)

            await session.commit()

            return await self.updated_product_response(product_id, session)
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error when updating product {product_id}: {str(e)}")
            raise ProductException.update_failed()

    async def updated_product_response(self, product_id: str, session: AsyncSession):
        response = await get_detail_product_service.get_detail_product(product_id, session)

        product_variant = [
            {
                "id": str(item["id"]),
                "size": item["size"],
                "image": item["image"],
                "color_id": str(item.get("color_id")) if item.get("color_id") else None,
                "color_name": item.get("color_name"),
                "color_code": item.get("color_code"),
                "price": float(item["original_price"]) if item["original_price"] else None,
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
            "brand": response["brand"],
            "materials": response["materials"],
            "tags": response["tags"],
            "product_variant": product_variant
        }

        return product_dict

    async def validate_and_delete_variants(self, product_id: str, deleted_ids: List[str], product: Product,
                                            session: AsyncSession):

        existing_variant_ids = [str(v.id) for v in product.product_variant if v.deleted_at is None]
        invalid_ids = set(deleted_ids) - set(existing_variant_ids)
        if invalid_ids:
            ProductException.variant_not_belong_to_product(list(invalid_ids))

        for variant_id in deleted_ids:
            has_pending_orders = await self.check_variant_in_pending_orders(variant_id, session)
            if has_pending_orders:
                ProductException.variant_in_pending_order(variant_id)

        for variant_id in deleted_ids:
            condition = [Product_Variant.id == variant_id]
            await product_variant_repository.delete_product_variant(condition, session)

        await session.commit()

    async def check_variant_in_pending_orders(self, variant_id: str, session: AsyncSession):
        joins = [
            (
                Order_Detail,
                {
                    "type": "inner",
                    "on": Order_Detail.product_id == Product.id
                }
            ),
            (
                Order,
                {
                    "type": "inner",
                    "on": Order.id == Order_Detail.order_id
                }
            ),
        ]

        conditions = [
            Order_Detail.product_variant_id == variant_id,
            Order.status.in_(["pending", "processing", "confirmed"]),
        ]

        product = await product_repository.get_product(
            session=session,
            select_columns=[Product.id],
            joins=joins,
            where_conditions=conditions
        )

        return product is not None

    async def validate_variants(self, variants: List[dict], product_id: str, session: AsyncSession):
        if not variants or len(variants) == 0:
            ProductException.variants_required()

        skus = []
        for idx, variant in enumerate(variants):
            price = variant.get('price')
            if price is not None and (not isinstance(price, int) or price <= 0):
                ProductException.invalid_price(idx)

            quantity = variant.get('quantity')
            if quantity is not None and (not isinstance(quantity, int) or quantity < 0):
                ProductException.invalid_quantity(idx)

            sku = variant.get('sku')
            if sku:
                if sku in skus:
                    raise ProductException.duplicate_sku()
                skus.append(sku)

                conditions = [
                    Product_Variant.sku == sku,
                    Product_Variant.product_id != product_id,
                    Product_Variant.deleted_at.is_(None),
                ]

                existing = await product_variant_repository.get_product_variant(
                    session=session, where_conditions=conditions
                )

                if existing:
                    raise ProductException.sku_already_exists()

            size = variant.get('size')
            if size and not isinstance(size, str):
                raise ProductException.invalid_size(idx)

            color_id = variant.get('color_id')
            if color_id:
                conditions = [Color.id == color_id, Color.deleted_at.is_(None)]
                color_exists = await color_repository.get_color(session=session, where_conditions=conditions)
                if not color_exists:
                    raise ColorException.color_not_found()


    async def validate_categories(self, category_ids: List[str], session: AsyncSession):
        if not category_ids or len(category_ids) == 0:
            raise ProductException.categories_required()

        for cat_id in category_ids:
            cat_condition = [
                Categories.id == cat_id,
                Categories.deleted_at.is_(None),
                Categories.is_active == True
            ]
            cat_exists = await categories_repository.get_category(session=session, where_conditions=cat_condition)
            if not cat_exists:
                raise CategoriesException.category_not_found(cat_id)


    async def validate_and_update_materials(self, product_id: str, materials: List[dict], session: AsyncSession):
        if not materials or len(materials) == 0:
            MaterialException.materials_required()

        total_percentage = sum(m.get('percentage', 0) for m in materials)
        if total_percentage != 100:
            raise MaterialException.invalid_material_percentage(total_percentage)

        material_ids = []
        for material_data in materials:
            material_id = material_data.get("material_id")
            percentage = material_data.get("percentage")

            if not material_id:
                raise MaterialException.material_id_required()

            if material_id in material_ids:
                raise MaterialException.duplicate_material(material_id)
            material_ids.append(material_id)

            if not isinstance(percentage, (int, float)) or percentage <= 0 or percentage > 100:
                raise MaterialException.invalid_percentage(material_id)

            material_condition = [
                Material.id == material_id,
                Material.deleted_at.is_(None),
                Material.is_active == True
            ]
            material_exists = await material_repository.get_material(session=session, where_conditions=material_condition)
            if not material_exists:
                raise MaterialException.material_not_found()

        await product_material_repository.delete_product_material(product_id, session)

        for material_data in materials:
            product_material = Product_Material(
                product_id=product_id,
                material_id=material_data["material_id"],
                percentage=material_data["percentage"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            session.add(product_material)


    async def validate_and_update_tags(self, product_id: str, tags_id: List[str], session: AsyncSession):
        if tags_id is None:
            return

        for tag_id in tags_id:
            tag_condition = [
                Tag.id == tag_id,
                Tag.deleted_at.is_(None),
                Tag.is_active == True
            ]
            tag_exists = await tag_repository.get_tag(session=session, where_conditions=tag_condition, )
            if not tag_exists:
                raise TagException.tag_not_found()

        await product_tag_repository.delete_product_tag(product_id, session)

        for tag_id in tags_id:
            product_tag = Product_Tag(
                product_id=product_id,
                tag_id=tag_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            session.add(product_tag)


    def validate_basic_fields(self, data: dict):
        name = data.get('name')
        if name is not None:
            if not isinstance(name, str) or len(name.strip()) == 0:
                ProductException.invalid_name()
            if len(name) > 255:
                raise ProductException.name_too_long()

        description = data.get('description')
        if description is not None and not isinstance(description, str):
            raise ProductException.invalid_description()

        images = data.get('images')
        if images is not None:
            if not isinstance(images, list):
                raise ProductException.invalid_images()
            if len(images) > 10:
                raise ProductException.too_many_images()


    async def validate_has_active_variants(self, product_id: str, session: AsyncSession):
        variant = await product_variant_repository.get_product_variant(
            session=session,
            select_columns=[Product_Variant.id],
            where_conditions=[
                Product_Variant.product_id == product_id,
                Product_Variant.deleted_at.is_(None),
            ],
        )

        if variant is None:
            raise ProductException.no_active_variants()

