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
from src.schemas.tag import TagCreateModel, ProductTagAssignmentModel, TagUpdateModel, DeleteMultipleTagsModel, \
    TagDeleteStrategy

tag_repository = TagRepository()
product_repository = ProductRepository()


class DeleteTagService:
    async def delete_tag(self, tag_id: str, strategy: TagDeleteStrategy, session: AsyncSession):
        conditions = [Tag.id == tag_id, Tag.deleted_at.is_(None)]
        tag = await tag_repository.get_tag(session=session, where_conditions=conditions)

        if not tag:
            TagException.tag_not_found()

        if tag.products_count > 0:
            if strategy == TagDeleteStrategy.REJECT:
                TagException.tag_currently_use(tag)

            elif strategy == TagDeleteStrategy.FORCE_DELETE:
                await tag_repository.delete_tag_relationships(tag_id, session)

        await tag_repository.soft_delete_tag(tag_id, session)
        await session.commit()

        return {
            "id": str(tag.id),
            "name": tag.name,
            "slug": tag.slug,
            "products_count": tag.products_count,
            "deleted_at": datetime.utcnow().isoformat()
        }


    async def delete_multiple_tags(self, data: DeleteMultipleTagsModel, session: AsyncSession):
        results = []
        deleted_count = 0
        skipped_count = 0
        failed_count = 0

        conditions = [
            Tag.id.in_(data.tag_ids),
            Tag.deleted_at.is_(None)
        ]
        tags = await tag_repository.get_all_tag(session=session, where_conditions=conditions)
        tags_dict = {str(tag.id): tag for tag in tags}

        for tag_id in data.tag_ids:
            if tag_id not in tags_dict:
                results.append({
                    "id": tag_id,
                    "name": "Unknown",
                    "products_count": 0,
                    "status": "skipped",
                    "reason": "Tag không tồn tại hoặc đã bị xóa"
                })
                skipped_count += 1
                continue

            tag = tags_dict[tag_id]

            if tag.products_count > 0:
                if data.strategy == TagDeleteStrategy.REJECT:
                    results.append({
                        "id": str(tag.id),
                        "name": tag.name,
                        "products_count": tag.products_count,
                        "status": "skipped",
                        "reason": f"Tag đang được sử dụng bởi {tag.products_count} sản phẩm"
                    })
                    skipped_count += 1
                    continue
                elif data.strategy == TagDeleteStrategy.FORCE_DELETE:
                    await tag_repository.delete_tag_relationships(tag_id, session)

            await tag_repository.soft_delete_tag(tag_id, session)

            results.append({
                "id": str(tag.id),
                "name": tag.name,
                "products_count": tag.products_count,
                "status": "deleted",
                "reason": None
            })
            deleted_count += 1

        await session.commit()

        return {
            "total_requested": len(data.tag_ids),
            "deleted": deleted_count,
            "skipped": skipped_count,
            "failed": failed_count,
            "details": results
        }