from datetime import datetime
from sqlalchemy.orm import selectinload, joinedload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product.repositories import ProductRepository
from src.crud.product.services.get_detail_product import GetDetailProductService
from src.crud.product.services.update_product.association_manager import ProductAssociationManager
from src.crud.product.services.update_product.update_validator import ProductUpdateValidator
from src.crud.product.services.update_product.variant_manager import ProductVariantManager
from src.database.models import Product, Categories_Product, Categories, Product_Variant, Color
from src.errors.product import ProductException
import logging

logger = logging.getLogger(__name__)
product_repository = ProductRepository()
get_detail_product_service = GetDetailProductService()
variant_manager = ProductVariantManager()
association_manager = ProductAssociationManager()
validator = ProductUpdateValidator()


class UpdateProductService:
    async def update_product(self, product_id: str, product_data, session: AsyncSession):
        try:
            product_to_update = await self.load_product(product_id, session)
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
                await variant_manager.delete_variants(
                    product_id, deleted_ids, product_to_update[0], session
                )

            if new_variants is not None:
                await variant_manager.update_variants(
                    product_id, new_variants, session
                )

            if new_category_ids is not None:
                await association_manager.update_categories(
                    product_id, new_category_ids, session
                )

            if new_brand_id is not None:
                await association_manager.update_brand(
                    product_to_update[0], new_brand_id, session
                )

            if new_materials is not None:
                await association_manager.update_materials(
                    product_id, new_materials, session
                )

            if new_tags_id is not None:
                await association_manager.update_tags(
                    product_id, new_tags_id, session
                )

            if product_data_dict:
                validator.validate_basic_fields(product_data_dict)
                for k, v in product_data_dict.items():
                    setattr(product_to_update[0], k, v)

            product_to_update[0].updated_at = datetime.now()
            await session.flush()

            await validator.validate_has_active_variants(product_id, session)
            await session.commit()

            return await self.build_response(product_id, session)

        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error when updating product {product_id}: {str(e)}")
            raise ProductException.update_failed()


    async def load_product(self, product_id: str, session: AsyncSession):
        condition = [Product.id == product_id, Product.deleted_at.is_(None)]
        options = [
            selectinload(Product.categories_product).options(
                joinedload(Categories_Product.categories).load_only(
                    Categories.id, Categories.name, Categories.parent_id, Categories.deleted_at
                )
            ),
            selectinload(Product.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.id, Color.name, Color.code
                )
            ).load_only(
                Product_Variant.id, Product_Variant.size, Product_Variant.price,
                Product_Variant.quantity, Product_Variant.image, Product_Variant.sku,
                Product_Variant.color_name, Product_Variant.color_code, Product_Variant.deleted_at
            ),
        ]
        return await product_repository.get_product(
            session=session, where_conditions=condition, options=options
        )


    async def build_response(self, product_id: str, session: AsyncSession):
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

        return {
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