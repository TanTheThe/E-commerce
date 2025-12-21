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
from src.schemas.tag import TagAdminQueryParams, TagCreateModel, ProductTagAssignmentModel, TagQueryParams, TagSortEnum, TagUpdateModel, DeleteMultipleTagsModel

tag_repository = TagRepository()
product_repository = ProductRepository()


class GetAllTagsService:
    async def get_all_tags_admin(self, params: TagAdminQueryParams, skip: int, limit: int, session: AsyncSession):
        conditions = [Tag.deleted_at.is_(None)]
        
        if params.search:
            conditions.append(Tag.name.ilike(f"%{params.search}%"))
        
        if params.is_active is not None:
            conditions.append(Tag.is_active == params.is_active)

        order_by_clause = self.get_order_by_clause(params.sort_by)

        tags, total = await tag_repository.get_all_tag(
            conditions=conditions,
            session=session,
            skip=skip,
            limit=limit,
            order_by_clause=order_by_clause
        )

        tags_list = [
            {
                "id": str(tag.id),
                "name": tag.name,
                "slug": tag.slug,
                "is_active": tag.is_active,
                "product_count": tag.products_count,
                "created_at": str(tag.created_at) if tag.created_at else None
            }
            for tag in tags
        ]

        return {
            "data": tags_list,
            "total": total
        }


    async def get_all_tags_customer(self, params: TagQueryParams, skip: int, limit: int, session: AsyncSession):
        conditions = [
            Tag.deleted_at.is_(None),
            Tag.is_active == True
        ]
        
        if params.search:
            conditions.append(Tag.name.ilike(f"%{params.search}%"))
        
        order_by_clause = desc(Tag.created_at)

        tags, total = await tag_repository.get_all_tag(
            conditions=conditions,
            session=session,
            skip=skip,
            limit=limit,
            order_by_clause=order_by_clause
        )

        tags_list = [
            {
                "id": str(tag.id),
                "name": tag.name,
                "slug": tag.slug,
                "is_active": tag.is_active,
                "product_count": tag.products_count,
            }
            for tag in tags
        ]

        return {
            "data": tags_list,
            "total": total
        }

    
    def get_order_by_clause(self, sort_by: TagSortEnum):
        sort_mapping = {
            TagSortEnum.NAME_ASC: asc(Tag.name),
            TagSortEnum.NAME_DESC: desc(Tag.name),
            TagSortEnum.CREATED_ASC: asc(Tag.created_at),
            TagSortEnum.CREATED_DESC: desc(Tag.created_at),
        }
        return sort_mapping.get(sort_by, desc(Tag.created_at))