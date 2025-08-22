from typing import Optional, List
from sqlalchemy import ColumnElement
from sqlalchemy.orm import noload

from src.database.models import Evaluate, Order_Detail
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_, func, distinct
from datetime import datetime
from src.errors.evaluate import EvaluateException
from src.schemas.evaluate import SupplementEvaluateModel


class EvaluateRepository:
    async def create_evaluate(self, evaluate_data, session: AsyncSession):
        evaluate_data_dict = evaluate_data.model_dump()

        new_evaluate = Evaluate(
            **evaluate_data_dict,
            created_at=datetime.now()
        )
        session.add(new_evaluate)

        return new_evaluate

    async def get_all_evaluate(self, conditions: List[Optional[ColumnElement[bool]]], session: AsyncSession,
                               order_by: list = None, joins: list = None,
                               skip: int = 0, limit: int = 10, need_join: bool = False):
        count_stmt = select(func.count(distinct(Evaluate.id))).select_from(Evaluate).where(*conditions)
        if need_join:
            count_stmt = (count_stmt
                          .join(Evaluate.product)
                          .join(Evaluate.user)
                          .join(Evaluate.order_detail)
                          .join(Order_Detail.order))

        total_result = await session.exec(count_stmt)
        total = total_result.one()

        statement = select(Evaluate).distinct(Evaluate.id).options(
            *joins if joins else []
        ).where(*conditions)

        if order_by:
            statement = statement.order_by(Evaluate.id, *order_by)
        else:
            statement = statement.order_by(Evaluate.id)

        statement = statement.offset(skip).limit(limit)
        result = await session.exec(statement)
        evaluates = result.all()
        return evaluates, total


    async def get_evaluate(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        statement = select(Evaluate).options(
            *joins if joins else []
        ).where(conditions)

        result = await session.exec(statement)

        return result.one_or_none()

    async def get_by_order_detail_id(self, order_detail_id: str, session: AsyncSession, joins: list = None):
        statement = select(Evaluate).options(
            *joins if joins else []
        ).where(Evaluate.order_detail_id == order_detail_id)
        result = await session.exec(statement)
        return result.one_or_none()

    async def supplement_evaluate(self, data: SupplementEvaluateModel, condition: Optional[ColumnElement[bool]],
                                  session: AsyncSession):
        evaluate = await self.get_evaluate(condition, session)
        if not evaluate:
            EvaluateException.review_not_found()

        if evaluate.additional_comment:
            EvaluateException.already_supplemented()

        evaluate.additional_comment = data.additional_comment
        evaluate.additional_image = data.additional_image
        evaluate.additional_created_at = datetime.now()

    async def get_average_rate(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        statement = select(func.avg(Evaluate.rate)).where(condition)
        result = await session.exec(statement)
        average = result.one_or_none()

        return average

    async def delete_evaluate(self, condition: Optional[ColumnElement[bool]], session: AsyncSession):
        evaluate_delete = await self.get_evaluate(condition, session)

        if evaluate_delete is None:
            EvaluateException.review_not_found_to_delete()

        evaluate_delete.deleted_at = datetime.now()
        await session.commit()

        return str(evaluate_delete.id)
