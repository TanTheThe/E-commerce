from typing import Optional
from sqlalchemy import ColumnElement
from src.database.models import Evaluate
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, and_, func
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


    async def get_all_evaluate(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None,
                               skip: int = 0, limit: int = 10):
        base_condition = Evaluate.deleted_at.is_(None)
        if conditions is not None:
            combined_condition = and_(base_condition, conditions)
        else:
            combined_condition = base_condition

        statement = select(Evaluate).where(combined_condition).offset(skip).limit(limit).order_by(desc(Evaluate.created_at))

        if joins:
            statement = statement.options(*joins)

        result = await session.exec(statement)
        return result.all()


    async def get_evaluate(self, conditions: Optional[ColumnElement[bool]], session: AsyncSession, joins: list = None):
        base_condition = Evaluate.deleted_at.is_(None)
        if conditions is not None:
            combined_condition = and_(base_condition, conditions)
        else:
            combined_condition = base_condition

        statement = select(Evaluate).where(combined_condition)
        if joins:
            statement = statement.options(*joins)

        result = await session.exec(statement)

        return result.one_or_none()


    async def get_by_order_detail_id(self, order_detail_id: str, session: AsyncSession):
        statement = select(Evaluate).where(Evaluate.order_detail_id == order_detail_id)
        result = await session.exec(statement)
        return result.one_or_none()


    async def supplement_evaluate(self, data: SupplementEvaluateModel,  condition: Optional[ColumnElement[bool]], session: AsyncSession):
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
