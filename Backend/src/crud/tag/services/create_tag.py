from datetime import datetime
from sqlalchemy import func
from src.crud.product.repositories import ProductRepository
from src.crud.tag.repositories import TagRepository
from src.database.models import Product, Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, asc, desc
from src.errors.product import ProductException
from src.crud.tag.utils import generate_slug
from typing import Optional
from src.errors.tag import TagException
from src.schemas.tag import TagCreateModel, ProductTagAssignmentModel, TagUpdateModel, DeleteMultipleTagsModel
import re
import logging

logger = logging.getLogger(__name__)

tag_repository = TagRepository()
product_repository = ProductRepository()


class CreateTagService:
    async def create_tag_service(self, tag_data: TagCreateModel, session: AsyncSession):
        try:
            normalized_name = tag_data.name.strip()
        
            condition = [
                func.lower(Tag.name) == normalized_name.lower(),
                Tag.deleted_at.is_(None)
            ]
            existing_tag = await tag_repository.get_tag(session=session, where_conditions=condition)

            if existing_tag:
                TagException.tag_name_exists()

            base_slug = generate_slug(normalized_name)
            slug = await self.generate_unique_slug(base_slug, session)
            
            new_tag_dict = {
                "name": normalized_name,
                "slug": slug,
                "is_active": tag_data.is_active
            }
            
            tag = await tag_repository.create_tag(new_tag_dict, session)

            await session.commit()
            await session.refresh(tag)

            return {
                "id": str(tag.id),
                "name": tag.name,
                "slug": tag.slug,
                "is_active": tag.is_active,
                "created_at": tag.created_at.isoformat() if tag.created_at else None
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in auto-complete return task: {str(e)}")
            raise
        
        
    async def generate_unique_slug(self, base_slug: str, session: AsyncSession, max_attempts: int = 100) -> str:
        condition = [Tag.slug == base_slug, Tag.deleted_at.is_(None)]
        existing = await tag_repository.get_tag(session=session, where_conditions=condition)
        
        if not existing:
            return base_slug
        
        tags, _ = await tag_repository.get_all_tag(
            session=session, where_conditions=[Tag.slug.ilike(f"{base_slug}%"), Tag.deleted_at.is_(None)]
        )

        similar_slugs = {tag.slug for tag in tags}
        
        used_numbers = set()
        pattern = re.compile(rf"^{re.escape(base_slug)}-(\d+)$")
        
        for slug in similar_slugs:
            if slug == base_slug:
                used_numbers.add(0)
            else:
                match = pattern.match(slug)
                if match:
                    used_numbers.add(int(match.group(1)))
                    
        counter = 1
        while counter in used_numbers and counter < max_attempts:
            counter += 1
            
        if counter >= max_attempts:
            TagException.cant_create_unique_slug()
        
        return f"{base_slug}-{counter}"