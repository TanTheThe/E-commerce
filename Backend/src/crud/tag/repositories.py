from typing import Optional, List, Dict, Any, Set, Tuple
from sqlalchemy import ColumnElement, delete, insert
from src.database.models import Product, Tag, Product_Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func, update
from datetime import datetime
from src.errors.tag import TagException
from src.schemas.tag import DeleteMultipleTagsModel


class TagRepository:
    async def create_tag(self, tag_data_dict, session: AsyncSession):
        new_tag = Tag(
            **tag_data_dict,
            created_at=datetime.now()
        )
        session.add(new_tag)

        return new_tag
    
    
    async def bulk_insert_product_tags(self, product_tags_data: List[Dict[str, Any]], session: AsyncSession):
        insert_stmt = insert(Product_Tag).values(product_tags_data)
        await session.execute(insert_stmt)

    
    async def get_all_tag(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):
        if select_columns is None:
            query = select(Tag)
        else:
            query = select(*select_columns).select_from(Tag)

        if joins:
            for table, config in joins:
                if config.get('type') == 'outer':
                    query = query.outerjoin(table, config['on'])
                else:
                    query = query.join(table, config['on'])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.exec(count_query)
        total = count_result.one() or 0

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        tags = result.all()

        return tags, total


    async def get_tag(self, session: AsyncSession,
                        select_columns: Optional[List[Any]] = None,
                        joins: Optional[List[Tuple[Any, dict]]] = None,
                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                        group_by_columns: Optional[List[Any]] = None,
                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                        order_by: Optional[Any] = None,
                        options: Optional[List[Any]] = None):

        if select_columns is None:
            query = select(Tag)
        else:
            query = select(*select_columns).select_from(Tag)

        if joins:
            for table, config in joins:
                if config.get("type") == "outer":
                    query = query.outerjoin(table, config["on"])
                else:
                    query = query.join(table, config["on"])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        result = await session.exec(query)

        tag = result.one_or_none()

        return tag
    
    
    async def get_product_tags(self, session: AsyncSession,
                             select_columns: Optional[List[Any]] = None,
                             joins: Optional[List[Tuple[Any, dict]]] = None,
                             where_conditions: Optional[List[ColumnElement[bool]]] = None,
                             group_by_columns: Optional[List[Any]] = None,
                             having_conditions: Optional[List[ColumnElement[bool]]] = None,
                             order_by: Optional[Any] = None,
                             skip: int = 0, limit: int = 10,
                             options: Optional[list] = None):
        if select_columns is None:
            query = select(Product_Tag)
        else:
            query = select(*select_columns).select_from(Product_Tag)

        if joins:
            for table, config in joins:
                if config.get('type') == 'outer':
                    query = query.outerjoin(table, config['on'])
                else:
                    query = query.join(table, config['on'])

        if where_conditions:
            query = query.where(and_(*where_conditions))

        if group_by_columns:
            query = query.group_by(*group_by_columns)

        if having_conditions:
            query = query.having(and_(*having_conditions))

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.exec(count_query)
        total = count_result.one() or 0

        if options:
            query = query.options(*options)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        prod_tags = result.all()

        return prod_tags, total


    async def update_tag(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Tag)
            .where(condition)
            .values(**values)
        )

        await session.exec(stmt)


    async def count_products_by_tag(self, tag_id: str, session: AsyncSession):
        query = select(func.count(Product_Tag.product_id)).where(
            Product_Tag.tag_id == tag_id
        ).join(
            Product, and_(Product_Tag.product_id == Product.id)
        ).where(
            and_(
                Product.deleted_at.is_(None),
                Product.status == "active"
            )
        )
        result = await session.exec(query)
        return result.one_or_none()

    
    async def update_tag_counts(self, tag_ids: Set[str], increment: int, session: AsyncSession):
        if increment > 0:
            update_stmt = (
                update(Tag)
                .where(Tag.id.in_(tag_ids))
                .values(products_count=Tag.products_count + increment)
            )
        else:
            update_stmt = (
                update(Tag)
                .where(Tag.id.in_(tag_ids))
                .values(products_count=func.greatest(Tag.products_count + increment, 0))
            )
        
        await session.execute(update_stmt)


    async def delete_tag_relationships(self, tag_id: str, session: AsyncSession):
        delete_stmt = delete(Product_Tag).where(
            and_(Product_Tag.tag_id == tag_id)
        )
        await session.execute(delete_stmt)

        update_count_stmt = (
            update(Tag)
            .where(and_(Tag.id == tag_id))
            .values(products_count=0)
        )
        await session.execute(update_count_stmt)
    

    async def soft_delete_tag(self, tag_id: str, session: AsyncSession):
        stmt = (
            update(Tag)
            .where(and_(Tag.id == tag_id))
            .values(
                deleted_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        await session.execute(stmt)
    
    async def delete_multiple_tags(self, data: DeleteMultipleTagsModel, session: AsyncSession):
        conditions = [Tag.id.in_(data.tag_ids), Tag.deleted_at.is_(None)]
        tags, _ = await self.get_all_tag(session=session, where_conditions=conditions)
        existing_ids = {str(row.id) for row in tags}
        missing_ids = set(data.tag_ids) - existing_ids
        if missing_ids:
            TagException.some_tags_not_found()

        condition_delete = and_(Tag.id.in_(data.tag_ids), Tag.deleted_at.is_(None))
        stmt = update(Tag).where(condition_delete).values(deleted_at=datetime.now())

        await session.exec(stmt)
        await session.commit()

        return data.tag_ids
