from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, delete
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

    async def get_product_tags(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Product_Tag).options(
            *joins if joins else []
        ).where(*conditions)
        result = await session.exec(statement)

        return result.all()

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
            Product.deleted_at.is_(None),
            Product.status == "active"
        )
        result = await session.exec(query)
        return result.one_or_none()


    async def assign_tags_to_product(self, product_id: str, tag_ids: List[str], session: AsyncSession):
        condition = and_(Product_Tag.product_id == product_id, Product_Tag.deleted_at.is_(None))
        current_tags = await self.get_product_tags(condition, session)
        current_tag_ids = [str(tag.id) for tag in current_tags]

        removed_tags = set(current_tag_ids) - set(tag_ids)
        added_tags = set(tag_ids) - set(current_tag_ids)

        delete_stmt = delete(Product_Tag).where(and_(Product_Tag.product_id == product_id))
        await session.exec(delete_stmt)

        for tag_id in tag_ids:
            product_tag = Product_Tag(
                product_id=product_id,
                tag_id=tag_id,
                created_at=datetime.now()
            )
            session.add(product_tag)

        if removed_tags:
            condition_increment = and_(Tag.id.in_(tag_ids))
            await self.update_tag(condition_increment, {"products_count": Tag.products_count + 1}, session)
        if added_tags:
            condition_decrement = and_(Tag.id.in_(tag_ids))
            await self.update_tag(condition_decrement, {"products_count": func.greatest(Tag.products_count - 1, 0)}, session)

        await session.commit()
        return True


    async def delete_tag(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        tag_delete = await self.get_tag(condition, session)

        if tag_delete is None:
            TagException.tag_not_found()

        tag_delete.deleted_at = datetime.now()
        await session.commit()

        return str(tag_delete.id)
    
    async def delete_multiple_tags(self, data: DeleteMultipleTagsModel, session: AsyncSession):
        conditions = [Tag.id.in_(data.tag_ids), Tag.deleted_at.is_(None)]
        tags, _ = await self.get_all_tag(conditions, session)
        existing_ids = {str(row.id) for row in tags}
        missing_ids = set(data.tag_ids) - existing_ids
        if missing_ids:
            TagException.some_tags_not_found()

        condition_delete = and_(Tag.id.in_(data.tag_ids), Tag.deleted_at.is_(None))
        stmt = update(Tag).where(condition_delete).values(deleted_at=datetime.now())

        await session.exec(stmt)
        await session.commit()

        return data.tag_ids
