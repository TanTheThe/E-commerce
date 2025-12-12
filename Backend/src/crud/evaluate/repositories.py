from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import ColumnElement, update
from src.crud.product.repositories import ProductRepository
from src.database.models import Evaluate, Product
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, func
from datetime import datetime
from src.errors.evaluate import EvaluateException

product_repository = ProductRepository()


class EvaluateRepository:
    async def create_evaluate(self, evaluate_data, session: AsyncSession):
        evaluate_data_dict = evaluate_data.model_dump()

        new_evaluate = Evaluate(
            **evaluate_data_dict,
            created_at=datetime.now()
        )
        session.add(new_evaluate)

        return new_evaluate


    async def get_all_evaluate(self, session: AsyncSession,
                            select_columns: Optional[List[Any]] = None,
                            joins: Optional[List[Tuple[Any, dict]]] = None,
                            where_conditions: Optional[List[ColumnElement[bool]]] = None,
                            group_by_columns: Optional[List[Any]] = None,
                            having_conditions: Optional[List[ColumnElement[bool]]] = None,
                            order_by: Optional[Any] = None,
                            skip: int = 0, limit: int = 10,
                            options: Optional[list] = None):
        if select_columns is None:
            query = select(Evaluate)
        else:
            query = select(*select_columns).select_from(Evaluate)

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
        evaluates = result.all()

        return evaluates, total


    async def get_evaluate(self, session: AsyncSession,
                        select_columns: Optional[List[Any]] = None,
                        joins: Optional[List[Tuple[Any, dict]]] = None,
                        where_conditions: Optional[List[ColumnElement[bool]]] = None,
                        group_by_columns: Optional[List[Any]] = None,
                        having_conditions: Optional[List[ColumnElement[bool]]] = None,
                        order_by: Optional[Any] = None,
                        options: Optional[List[Any]] = None):

        if select_columns is None:
            query = select(Evaluate)
        else:
            query = select(*select_columns).select_from(Evaluate)

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

        evaluate = result.one_or_none()

        return evaluate

    async def update_evaluate_some_field(self, condition: Optional[ColumnElement[bool]], values: Dict[str, Any], session: AsyncSession):
        stmt = (
            update(Evaluate)
            .where(condition)
            .values(**values)
            .returning(Evaluate)
        )
        result = await session.exec(stmt)
        await session.flush()
        await session.commit()

        return result.one_or_none()

    async def get_average_rate(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(func.avg(Evaluate.rate)).where(condition)
        result = await session.exec(statement)
        average = result.one_or_none()

        return average

    async def delete_evaluate(self, condition: Optional[List[ColumnElement[bool]]], session: AsyncSession):
        evaluate_delete = await self.get_evaluate(session=session, where_conditions=condition)

        if evaluate_delete is None:
            EvaluateException.review_not_found_to_delete()

        evaluate_delete.deleted_at = datetime.now()

        await product_repository.update_product_some_field(
            Product.id == evaluate_delete.product_id,
            {"review_count": Product.review_count - 1},
            session
        )
        await session.commit()

        return str(evaluate_delete.id)
