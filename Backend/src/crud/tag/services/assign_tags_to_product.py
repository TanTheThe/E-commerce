from datetime import datetime

from sqlalchemy import delete, func
from src.crud.product.repositories import ProductRepository
from src.crud.tag.repositories import TagRepository
from src.database.models import Product, Product_Tag, Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, asc, desc
from src.errors.product import ProductException
from src.crud.tag.utils import generate_slug
from typing import List, Optional
from src.errors.tag import TagException
from src.schemas.tag import TagCreateModel, ProductTagAssignmentModel, TagUpdateModel, DeleteMultipleTagsModel

tag_repository = TagRepository()
product_repository = ProductRepository()


class AssignTagsToProductService:
    async def assign_tags_to_product(self, assignment_data: ProductTagAssignmentModel, session: AsyncSession):
        condition_tag_ids = [
            Product.id == assignment_data.product_id, 
            Product.deleted_at.is_(None),
            Product.status == "active"
        ]
        product = await product_repository.get_product(session=session, where_conditions=condition_tag_ids)
        if not product:
            ProductException.not_found()
            
        if assignment_data.tag_ids:
            conditions = [
                Tag.id.in_(assignment_data.tag_ids),
                Tag.deleted_at.is_(None)
            ]
            tags, _ = await tag_repository.get_all_tag(session=session, where_conditions=conditions)
            existing_tag_ids = {str(row.id) for row in tags}

            missing_tags = set(assignment_data.tag_ids) - existing_tag_ids

            if missing_tags:
                TagException.some_tags_not_found()

        added_count, removed_count = await self.process_assign_tags_to_product(assignment_data.product_id, assignment_data.tag_ids, session)

        return {
            "product_id": str(assignment_data.product_id),
            "assigned_tags": len(assignment_data.tag_ids),
            "tags_added": added_count,
            "tags_removed": removed_count
        }
        
        
    async def process_assign_tags_to_product(self, product_id: str, tag_ids: List[str], session: AsyncSession):
        conditions_product_tag = [
            Product_Tag.product_id == product_id,
            Product_Tag.deleted_at.is_(None)
        ]

        current_tags = await tag_repository.get_product_tags(session=session, where_conditions=conditions_product_tag)
        
        current_tag_ids = [str(tag.id) for tag in current_tags]
        
        new_tag_ids_set = set(tag_ids)
        current_tag_ids_set = set(current_tag_ids)
        
        added_tags = new_tag_ids_set - current_tag_ids_set
        removed_tags = current_tag_ids_set - new_tag_ids_set
        
        delete_stmt = delete(Product_Tag).where(
            Product_Tag.product_id == product_id
        )
        await session.execute(delete_stmt)
        
        if tag_ids:
            product_tags_data = [
                {
                    "product_id": product_id,
                    "tag_id": tag_id,
                    "created_at": datetime.now()
                }
                for tag_id in tag_ids
            ]
            await tag_repository.bulk_insert_product_tags(product_tags_data, session)
            
        if added_tags:
            await tag_repository.update_tag_counts(added_tags, increment=1, session=session)
        
        if removed_tags:
            await tag_repository.update_tag_counts(removed_tags, increment=-1, session=session)

        await session.commit()
        
        return len(added_tags), len(removed_tags)
        
        
        