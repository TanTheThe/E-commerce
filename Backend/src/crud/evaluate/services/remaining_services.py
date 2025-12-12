from datetime import datetime, timedelta
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.evaluate.repositories import EvaluateRepository
from src.crud.product.repositories import ProductRepository
from src.database.models import Evaluate
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.schemas.evaluate import SupplementEvaluateModel, ReplyEvaluateModel
from src.errors.evaluate import EvaluateException
import logging

logger = logging.getLogger(__name__)

evaluate_repository = EvaluateRepository()
order_detail_repository = OrderDetailRepository()
product_repository = ProductRepository()


class RemainingEvaluateService:
    async def supplement_evaluate(self, evaluate_id: str, customer_id: str,
                                  data: SupplementEvaluateModel, session: AsyncSession):
        condition = [
            Evaluate.id == evaluate_id,
            Evaluate.user_id == customer_id,
            Evaluate.deleted_at.is_(None)
        ]
        evaluate = await evaluate_repository.get_evaluate(session=session, where_conditions=condition)
        if not evaluate:
            EvaluateException.review_not_found()

        if evaluate.additional_comment or evaluate.additional_image:
            EvaluateException.already_supplemented()

        if evaluate.created_at < datetime.now() - timedelta(days=7):
            EvaluateException.supplement_time_expired()

        updated_evaluate = await evaluate_repository.update_evaluate_some_field(and_(*condition),
                                                             {"additional_comment": data.additional_comment,
                                                              "additional_created_at": datetime.now(),
                                                              "additional_image": data.additional_image},
                                                             session)

        return {
            "id": str(updated_evaluate.id),
            "additional_comment": updated_evaluate.additional_comment,
            "additional_created_at": updated_evaluate.additional_created_at.isoformat()
        }

    async def reply_evaluate(self, evaluate_id: str, data: ReplyEvaluateModel, session: AsyncSession):
        condition = [
            Evaluate.id == evaluate_id,
            Evaluate.deleted_at.is_(None)
        ]
        evaluate = await evaluate_repository.get_evaluate(session=session, where_conditions=condition)
        if not evaluate:
            EvaluateException.review_not_found()

        if evaluate.seller_reply:
            EvaluateException.already_reply()

        updated_evaluate = await evaluate_repository.update_evaluate_some_field(and_(*condition),
                                                             {"seller_reply": data.seller_reply,
                                                              "seller_reply_at": datetime.now()},
                                                             session)

        return {
            "id": str(updated_evaluate.id),
            "seller_reply": updated_evaluate.seller_reply,
            "seller_reply_at": updated_evaluate.seller_reply_at.isoformat() if updated_evaluate.seller_reply_at else None
        }

    async def delete_evaluate_service(self, evaluate_id: str, session: AsyncSession):
        condition = [Evaluate.id == evaluate_id, Evaluate.deleted_at.is_(None)]
        return await evaluate_repository.delete_evaluate(condition, session)
