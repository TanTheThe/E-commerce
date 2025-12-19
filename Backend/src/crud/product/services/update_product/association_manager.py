from datetime import datetime
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.brand.repositories import BrandRepository
from src.crud.categories.repositories import CategoriesRepository
from src.crud.categories_product.services import CategoriesProductService
from src.crud.material.repositories import MaterialRepository
from src.crud.product_material.repositories import ProductMaterialRepository
from src.crud.product_tag.repositories import ProductTagRepository
from src.crud.tag.repositories import TagRepository
from src.database.models import Categories, Product, Brand, Material, Product_Material, Tag, Product_Tag
from src.errors.brand import BrandException
from src.errors.categories import CategoriesException
from src.errors.material import MaterialException
from src.errors.product import ProductException
from src.errors.tag import TagException

tag_repository = TagRepository()
product_material_repository = ProductMaterialRepository()
categories_repository = CategoriesRepository()
categories_product_service = CategoriesProductService()
brand_repository = BrandRepository()
material_repository = MaterialRepository()
product_tag_repository = ProductTagRepository()

class ProductAssociationManager:
    async def update_categories(self, product_id: str, category_ids: List[str], session: AsyncSession):
        if not category_ids or len(category_ids) == 0:
            raise ProductException.categories_required()

        for cat_id in category_ids:
            conditions = [
                Categories.id == cat_id,
                Categories.deleted_at.is_(None),
                Categories.is_active == True
            ]
            exists = await categories_repository.get_category(session=session, where_conditions=conditions)
            if not exists:
                raise CategoriesException.category_not_found(cat_id)

        await categories_product_service.update_categories_product(product_id, category_ids, session)


    async def update_brand(self, product: Product, brand_id: str, session: AsyncSession):
        if brand_id:
            conditions = [
                Brand.id == brand_id,
                Brand.deleted_at.is_(None),
                Brand.is_active == True
            ]
            exists = await brand_repository.get_brand(session=session, where_conditions=conditions)
            if not exists:
                BrandException.brand_not_found()

        product.brand_id = brand_id


    async def update_materials(self, product_id: str, materials: List[dict], session: AsyncSession):
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

        conditions = [
            Material.id.in_(material_ids),
            Material.deleted_at.is_(None),
            Material.is_active == True
        ]
        exists, _ = await material_repository.get_all_material(session=session, where_conditions=conditions)
        existing_material_ids = {str(row.id) for row in exists}
        missing_ids = set(material_ids) - existing_material_ids
        if missing_ids:
            raise MaterialException.material_not_found()

        await product_material_repository.delete_product_material(product_id, session)

        current_time = datetime.now()
        product_materials = [
            Product_Material(
                product_id=product_id,
                material_id=material_data["material_id"],
                percentage=material_data["percentage"],
                created_at=current_time,
                updated_at=current_time,
            )
            for material_data in materials
        ]
        session.add_all(product_materials)


    async def update_tags(self, product_id: str, tags_id: List[str], session: AsyncSession):
        if tags_id is None:
            return

        if len(tags_id) == 0:
            await product_tag_repository.delete_product_tag(product_id, session)
            return

        conditions = [
            Tag.id.in_(tags_id),
            Tag.deleted_at.is_(None),
            Tag.is_active == True
        ]

        exists, _ = await tag_repository.get_all_tag(session=session, where_conditions=conditions)
        existing_tag_ids = {str(row.id) for row in exists}
        missing_ids = set(tags_id) - existing_tag_ids
        if missing_ids:
            raise TagException.tag_not_found()

        await product_tag_repository.delete_product_tag(product_id, session)

        current_time = datetime.now()
        product_tags = [
            Product_Tag(
                product_id=product_id,
                tag_id=tag_id,
                created_at=current_time,
                updated_at=current_time,
            )
            for tag_id in tags_id
        ]
        session.add_all(product_tags)