from datetime import datetime
from sqlalchemy import func
from src.crud.product.repositories import ProductRepository
from src.crud.tag.repositories import TagRepository
from src.database.models import Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.crud.tag.utils import generate_slug
from src.errors.tag import TagException
from src.schemas.tag import TagUpdateModel
import re

tag_repository = TagRepository()
product_repository = ProductRepository()


class UpdateTagService:
    async def update_tag(self, tag_id: str, tag_data: TagUpdateModel, session: AsyncSession):
        condition = [Tag.id == tag_id, Tag.deleted_at.is_(None)]
        existing_tag = await tag_repository.get_tag(session=session, where_conditions=condition)
        if not existing_tag:
            TagException.tag_not_found()

        update_data = {}
        has_changes = False

        if tag_data.name is not None:
            normalized_name = tag_data.name.strip()

            if normalized_name.lower() != existing_tag.name.lower():
                conditions = [
                    func.lower(Tag.name) == normalized_name.lower(),
                    Tag.id != tag_id,
                    Tag.deleted_at.is_(None)
                ]
                duplicate_tag = await tag_repository.get_tag(session=session, where_conditions=conditions)

                if duplicate_tag:
                    TagException.tag_name_exists()

                new_slug = await self.generate_unique_slug_for_update(normalized_name, tag_id, session)

                update_data["name"] = normalized_name
                update_data["slug"] = new_slug
                has_changes = True

        if tag_data.is_active is not None and tag_data.is_active != existing_tag.is_active:
            update_data["is_active"] = tag_data.is_active
            has_changes = True

        if not has_changes:
            return {
                "id": str(existing_tag.id),
                "name": existing_tag.name,
                "slug": existing_tag.slug,
                "is_active": existing_tag.is_active,
                "products_count": existing_tag.products_count or 0,
                "created_at": existing_tag.created_at.isoformat() if existing_tag.created_at else None,
                "updated_at": existing_tag.updated_at.isoformat() if existing_tag.updated_at else None
            }

        update_data["updated_at"] = datetime.utcnow()

        await tag_repository.update_tag(
            and_(Tag.id == tag_id),
            update_data,
            session
        )

        await session.commit()

        conditions = [Tag.id == tag_id, Tag.deleted_at.is_(None)]
        tag = await tag_repository.get_tag(session=session, where_conditions=conditions)

        if not tag:
            TagException.tag_not_found()

        return {
            "id": str(tag.id),
            "name": tag.name,
            "slug": tag.slug,
            "is_active": tag.is_active,
            "products_count": tag.products_count or 0,
            "created_at": tag.created_at.isoformat() if tag.created_at else None,
            "updated_at": tag.updated_at.isoformat() if tag.updated_at else None
        }


    async def generate_unique_slug_for_update(self, name: str, current_tag_id: str, session: AsyncSession, max_attempts: int = 100):
        base_slug = generate_slug(name)

        conditions = [
            Tag.slug == base_slug,
            Tag.id != current_tag_id,
            Tag.deleted_at.is_(None)
        ]

        existing = await tag_repository.get_tag(session=session, where_conditions=conditions)

        if not existing:
            return base_slug

        conditions_pattern_exclude_id = [
            Tag.slug.like(f"{base_slug}%"),
            Tag.id != current_tag_id,
            Tag.deleted_at.is_(None)
        ]

        slugs = await tag_repository.get_all_tag(session=session, where_conditions=conditions_pattern_exclude_id)
        similar_slugs = [row.slug for row in slugs]

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


