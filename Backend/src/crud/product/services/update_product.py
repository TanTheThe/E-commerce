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
    Product_Material, Tag, Product_Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from datetime import datetime
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product_variant.services import ProductVariantService
from src.crud.categories_product.services import CategoriesProductService
from src.errors.brand import BrandException
from src.errors.material import MaterialException
from src.errors.product import ProductException
from src.errors.tag import TagException

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
            new_brand_id = product_data_dict.pop("brand_id", None)
            new_materials = product_data_dict.pop("materials", None)
            new_tags_id = product_data_dict.pop("tags_id", None)

            if (not product_data_dict and new_variants is None and new_category_ids is None
                    and new_brand_id is None and new_materials is None and new_tags_id is None):
                ProductException.not_enough_infor_to_update()

            if new_variants is not None:
                await product_variant_service.update_product_variant(product_id, new_variants, session)

            if new_category_ids is not None:
                await categories_product_service.update_categories_product(product_id, new_category_ids, session)

            if new_brand_id is not None:
                if new_brand_id:
                    brand_condition = and_(Brand.id == new_brand_id, Brand.deleted_at.is_(None),
                                           Brand.is_active == True)
                    brand_exists = await brand_repository.get_brand(brand_condition, session)
                    if not brand_exists:
                        BrandException.brand_not_found()

                product_to_update[0].brand_id = new_brand_id

            if new_materials is not None:
                await product_material_repository.delete_product_material(product_id, session)

                for material_data in new_materials:
                    material_id = material_data.get("material_id")
                    percentage = material_data.get("percentage")

                    material_condition = and_(Material.id == material_id, Material.deleted_at.is_(None),
                                              Material.is_active == True)
                    material_exists = await material_repository.get_material(material_condition, session)
                    if not material_exists:
                        MaterialException.material_not_found()

                    product_material = Product_Material(
                        product_id=product_id,
                        material_id=material_id,
                        percentage=percentage,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    session.add(product_material)

            if new_tags_id is not None:
                await product_tag_repository.delete_product_tag(product_id, session)

                for tag_id in new_tags_id:
                    tag_condition = and_(Tag.id == tag_id, Tag.deleted_at.is_(None), Tag.is_active == True)
                    tag_exists = await tag_repository.get_tag(tag_condition, session)
                    if not tag_exists:
                        TagException.tag_not_found()

                    product_tag = Product_Tag(
                        product_id=product_id,
                        tag_id=tag_id,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    session.add(product_tag)

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
            "brand": response["brand"],
            "materials": response["materials"],
            "tags": response["tags"],
            "product_variant": product_variant
        }

        return product_dict
