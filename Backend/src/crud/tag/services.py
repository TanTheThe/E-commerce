from datetime import datetime
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

tag_repository = TagRepository()
product_repository = ProductRepository()


class TagService:
    async def create_tag_service(self, tag_data: TagCreateModel, session: AsyncSession):
        condition = and_(Tag.name == tag_data.name, Tag.deleted_at.is_(None))
        existing_tag = await tag_repository.get_tag(condition, session)

        if existing_tag:
            TagException.tag_name_exists()

        slug = generate_slug(tag_data.name)

        condition_slug = and_(Tag.slug == slug, Tag.deleted_at.is_(None))
        existing_slug = await tag_repository.get_tag(condition_slug, session)
        if existing_slug:
            counter = 1
            new_slug = ""
            while existing_slug:
                new_slug = f"{slug}-{counter}"
                condition_slug = and_(Tag.slug == new_slug, Tag.deleted_at.is_(None))
                existing_slug = await tag_repository.get_tag(condition_slug, session)
                counter += 1
            slug = new_slug

        new_tag_dict = {
            "name": tag_data.name,
            "slug": slug,
            "is_active": tag_data.is_active
        }

        tag = await tag_repository.create_tag(new_tag_dict, session)

        await session.commit()

        return {
            "id": str(tag.id),
            "name": tag.name,
            "slug": tag.slug,
            "is_active": tag.is_active,
            "created_at": str(tag.created_at) if tag.created_at else None
        }

    async def get_all_tags_admin(self, search: Optional[str], is_active: Optional[bool],
                                 sort_by: Optional[str], skip: int, limit: int, session: AsyncSession):
        conditions = [Tag.deleted_at.is_(None)]

        if search:
            conditions.append(Tag.name.ilike(f"%{search}%"))

        if is_active is not None:
            conditions.append(Tag.is_active == is_active)

        order_by_clause = None

        if sort_by == "name_asc":
            order_by_clause = asc(Tag.name)
        elif sort_by == "name_desc":
            order_by_clause = desc(Tag.name)
        elif sort_by == "created_asc":
            order_by_clause = asc(Tag.created_at)
        else:
            order_by_clause = desc(Tag.created_at)

        tags, total = await tag_repository.get_all_tag(conditions, session, skip, limit,
                                                       order_by_clause=order_by_clause)

        tags_list = []
        for tag in tags:
            tag_dict = {
                "id": str(tag.id),
                "name": tag.name,
                "slug": tag.slug,
                "is_active": tag.is_active,
                "product_count": tag.products_count,
                "created_at": str(tag.created_at) if tag.created_at else None
            }
            tags_list.append(tag_dict)

        return {
            "data": tags_list,
            "total": total
        }

    async def get_all_tags_customer(self, search: Optional[str], skip: int, limit: int, session: AsyncSession):
        conditions = [Tag.deleted_at.is_(None)]

        if search:
            conditions.append(Tag.name.ilike(f"%{search}%"))

        tags, total = await tag_repository.get_all_tag(conditions, session, skip, limit)

        tags_list = []
        for tag in tags:
            tag_dict = {
                "id": str(tag.id),
                "name": tag.name,
                "slug": tag.slug,
                "is_active": tag.is_active,
                "product_count": tag.products_count,
            }
            tags_list.append(tag_dict)

        return {
            "data": tags_list,
            "total": total
        }

    async def assign_tags_to_product(self, assignment_data: ProductTagAssignmentModel, session: AsyncSession):
        condition = and_(Product.id == assignment_data.product_id, Product.deleted_at.is_(None),
                         Product.status == "active")
        product = await product_repository.get_product(condition, session)
        if not product:
            ProductException.not_found()

        tag_ids = assignment_data.tag_ids
        condition_tag_ids = [Tag.id.in_(tag_ids), Tag.deleted_at.is_(None)]
        existing_tags = await tag_repository.get_all_tag(condition_tag_ids, session)

        if len(existing_tags) != len(tag_ids):
            TagException.some_tags_not_found()

        await tag_repository.assign_tags_to_product(assignment_data.product_id, assignment_data.tag_ids, session)

        return {
            "product_id": str(assignment_data.product_id),
            "assigned_tags": len(assignment_data.tag_ids)
        }

    async def update_tag_service(self, tag_id: str, tag_data: TagUpdateModel, session: AsyncSession):
        condition = and_(Tag.id == tag_id, Tag.deleted_at.is_(None))
        existing_tag = await tag_repository.get_tag(condition, session)
        if not existing_tag:
            TagException.tag_not_found()

        if tag_data.name and tag_data.name != existing_tag.name:
            condition_check_name = and_(Tag.name == tag_data.name, Tag.deleted_at.is_(None))
            duplicate_tag = await tag_repository.get_tag(condition_check_name, session)
            if duplicate_tag:
                TagException.tag_name_exists()

        new_slug = None
        if tag_data.name and tag_data.name != existing_tag.name:
            new_slug = generate_slug(tag_data.name)

            condition_slug = and_(Tag.slug == new_slug, Tag.deleted_at.is_(None))
            existing_slug = await tag_repository.get_tag(condition_slug, session)
            if existing_slug and str(existing_slug.id) != tag_id:
                counter = 1
                temp_slug = ""
                while existing_slug:
                    temp_slug = f"{new_slug}-{counter}"
                    condition_slug_loop = and_(Tag.slug == temp_slug, Tag.deleted_at.is_(None))
                    existing_slug = await tag_repository.get_tag(condition_slug_loop, session)
                    if not existing_slug or str(existing_slug.id) == tag_id:
                        break
                    counter += 1
                new_slug = temp_slug

        update_data = {}
        if tag_data.name is not None:
            update_data["name"] = tag_data.name
        if new_slug:
            update_data["slug"] = new_slug
        if tag_data.is_active is not None:
            update_data["is_active"] = tag_data.is_active
        update_data["updated_at"] = datetime.now()

        condition = and_(Tag.id == tag_id)
        await tag_repository.update_tag(condition, update_data, session)
        await session.commit()

        return {
            "id": tag_id,
            "name": update_data["name"],
            "slug": update_data["slug"],
            "is_active": update_data["is_active"],
            "updated_at": str(update_data["updated_at"])
        }

    async def delete_tag(self, tag_id: str, session: AsyncSession):
        condition = and_(Tag.id == tag_id, Tag.deleted_at.is_(None))
        return await tag_repository.delete_tag(condition, session)

    async def delete_multiple_tags(self, data: DeleteMultipleTagsModel, session: AsyncSession):
        tag_ids = await tag_repository.delete_multiple_tags(data, session)
        return tag_ids