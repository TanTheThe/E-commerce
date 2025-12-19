from src.crud.brand.repositories import BrandRepository
from src.crud.color.repositories import ColorRepository
from src.crud.material.repositories import MaterialRepository
from src.crud.product.utils import generate_slug
from src.crud.product_material.repositories import ProductMaterialRepository
from src.crud.product_tag.repositories import ProductTagRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.tag.repositories import TagRepository
from src.database.models import Categories, Color, Brand, Material, Product_Variant, Tag, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product.repositories import ProductRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.errors.brand import BrandException
from src.errors.color import ColorException
from src.errors.material import MaterialException
from src.errors.product import ProductException
from src.errors.categories import CategoriesException
from src.errors.tag import TagException
from src.schemas.product import ProductCreateModel
import logging

logger = logging.getLogger(__name__)

product_repository = ProductRepository()
categories_repository = CategoriesRepository()
cate_product_repository = CategoriesProductRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
brand_repository = BrandRepository()
material_repository = MaterialRepository()
tag_repository = TagRepository()
product_material_repository = ProductMaterialRepository()
product_tag_repository = ProductTagRepository()


class CreateProductService:
    async def create_product(self, product_data: ProductCreateModel, session: AsyncSession):
        try:
            skus = [v.sku for v in product_data.product_variant if v.sku]
            if skus and len(skus) != len(set(skus)):
                ProductException.duplicate_sku()
                
            if skus:
                condition = [Product_Variant.sku.in_(skus), Product_Variant.deleted_at.is_(None)]
                existing_variants, _ = await product_variant_repository.get_all_product_variant(
                    session=session, where_conditions=condition
                )
                if existing_variants:
                    ProductException.sku_already_exists()
            
            category_ids = product_data.categories_id
            condition = [Categories.id.in_(category_ids), Categories.deleted_at.is_(None)]
            existing_categories, total = await categories_repository.get_all_categories(
                session=session, where_conditions=condition, skip=0, limit=1000
            )
            
            if len(existing_categories) != len(category_ids):
                existing_ids = {c.id for c in existing_categories}
                missing_ids = set(category_ids) - existing_ids
                CategoriesException.categories_not_exist(list(missing_ids))

            existing_brand = None
            if product_data.brand_id:
                condition = [Brand.id == product_data.brand_id, Brand.deleted_at.is_(None), Brand.is_active == True]
                existing_brand = await brand_repository.get_brand(session=session, where_conditions=condition)
                if not existing_brand:
                    BrandException.brand_not_found()

            existing_materials = []
            if product_data.materials:
                material_ids = [material.material_id for material in product_data.materials]
                condition = [Material.id.in_(material_ids), Material.deleted_at.is_(None), Material.is_active == True]
                existing_materials, _ = await material_repository.get_all_material(session=session, where_conditions=condition, skip=0, limit=1000)

                if len(existing_materials) != len(material_ids):
                    existing_material_ids = {m.id for m in existing_materials}
                    missing_material_ids = set(material_ids) - existing_material_ids
                    MaterialException.materials_not_found(list(missing_material_ids))

            existing_tags = []
            if product_data.tags_id:
                condition = [Tag.id.in_(product_data.tags_id), Tag.deleted_at.is_(None), Tag.is_active == True]
                existing_tags, _ = await tag_repository.get_all_tag(session=session, where_conditions=condition, skip=0, limit=1000)

                if len(existing_tags) != len(product_data.tags_id):
                    existing_tag_ids = {t.id for t in existing_tags}
                    missing_tag_ids = set(product_data.tags_id) - existing_tag_ids
                    TagException.tags_not_found(list(missing_tag_ids))

            color_ids = []
            for variant in product_data.product_variant:
                if variant.color_id:
                    color_ids.append(variant.color_id)
            
            if color_ids:
                condition = [Color.id.in_(color_ids), Color.deleted_at.is_(None)]
                existing_colors, _ = await color_repository.get_all_color(session=session, where_conditions=condition, skip=0, limit=1000)
                
                if len(existing_colors) != len(set(color_ids)):
                    existing_color_ids = {str(c.id) for c in existing_colors}
                    missing_color_ids = set(color_ids) - existing_color_ids
                    ColorException.colors_not_found(list(missing_color_ids))

            new_product = await product_repository.create_product(product_data, session)

            base_slug = generate_slug(product_data.name)
            unique_slug = await self.generate_unique_slug(base_slug, session)
            new_product.slug = unique_slug

            await cate_product_repository.create_cate_product(existing_categories, new_product.id, session)

            await product_variant_repository.create_product_variant(product_data.product_variant, new_product.id,
                                                                    session)

            if product_data.materials:
                await product_material_repository.create_product_material(product_data.materials, new_product.id,
                                                                          session)

            if product_data.tags_id:
                await product_tag_repository.create_product_tag(product_data.tags_id, new_product.id, session)

            await session.commit()
            await session.refresh(new_product)

            product_dict = {
                "id": str(new_product.id),
                "name": new_product.name,
                "slug": new_product.slug,
                "images": new_product.images,
                "description": new_product.description,
                "short_description": new_product.short_description,
                "created_at": new_product.created_at.isoformat() if new_product.created_at else None,
                "status": new_product.status,
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                        "parent_id": str(category.parent_id) if category.parent_id else None
                    } for category in existing_categories
                ],
                "brand": {
                    "id": str(existing_brand.id),
                    "name": existing_brand.name,
                    "slug": existing_brand.slug,
                    "logo": existing_brand.logo
                } if existing_brand else None,
                "materials": [
                    {
                        "id": str(material.id),
                        "name": material.name,
                        "slug": material.slug,
                        "percentage": next(m.percentage for m in product_data.materials if m.material_id == material.id)
                    } for material in existing_materials
                ],
                "tags": [
                    {
                        "id": str(tag.id),
                        "name": tag.name,
                        "slug": tag.slug
                    } for tag in existing_tags
                ],
                "product_variant": [variant.dict() for variant in product_data.product_variant]
            }

            return product_dict
        except Exception as e:
            await session.rollback()
            logger.error("Error create new product: ", e)
            ProductException.invalid_create_product()


    async def generate_unique_slug(self, base_slug: str, session: AsyncSession):
        original_slug = base_slug
        counter = 1

        while True:
            condition = [
                Product.slug == base_slug, Product.deleted_at.is_(None), Product.status == "active"
            ]
            existing = await product_repository.get_product(session=session, where_conditions=condition)

            if not existing:
                return base_slug

            base_slug = f"{original_slug}-{counter}"
            counter += 1
