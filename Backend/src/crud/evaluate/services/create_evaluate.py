from datetime import datetime
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.evaluate.repositories import EvaluateRepository
from src.crud.product.repositories import ProductRepository
from src.database.models import Evaluate, Order_Detail, Order, Product, Product_Variant
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from sqlalchemy.orm import selectinload
from src.schemas.evaluate import EvaluateCreateModel, EvaluateInputModel
from src.errors.evaluate import EvaluateException
import logging

logger = logging.getLogger(__name__)

evaluate_repository = EvaluateRepository()
order_detail_repository = OrderDetailRepository()
product_repository = ProductRepository()


class CreateEvaluateService:
    async def create_evaluate(self, customer_id, evaluate_data: EvaluateInputModel, session: AsyncSession):
        try:
            condition = [Order_Detail.id == evaluate_data.order_detail_id, Order_Detail.deleted_at.is_(None)]
            options = [
                selectinload(Order_Detail.order).load_only(Order.user_id, Order.status, Order.delivered_at),
                selectinload(Order_Detail.product).load_only(Product.id, Product.name),
                selectinload(Order_Detail.product_variant).load_only(Product_Variant.id)
            ]
            order_detail = await order_detail_repository.get_order_detail(session=session, where_conditions=condition,
                                                                          options=options)

            if not order_detail:
                EvaluateException.order_detail_not_found()

            if str(customer_id) != str(order_detail.order.user_id):
                EvaluateException.user_not_allowed_to_review()

            valid_statuses = ["delivered", "received"]
            if order_detail.order.status not in valid_statuses:
                EvaluateException.order_not_delivered()

            condition_od = [Evaluate.order_detail_id == evaluate_data.order_detail_id, Evaluate.deleted_at.is_(None)]
            existing_eval = await evaluate_repository.get_evaluate(session=session, where_conditions=condition_od)
            if existing_eval:
                EvaluateException.already_reviewed()

            if not order_detail.product or order_detail.product.deleted_at is not None:
                EvaluateException.product_may_deleted()

            if hasattr(order_detail.order, 'delivered_at'):
                days_since_delivery = (datetime.now() - order_detail.order.delivered_at).days
                if days_since_delivery > 30:
                    EvaluateException.evaluate_period_has_expired()

            evaluate_create_data = EvaluateCreateModel(
                **evaluate_data.model_dump(),
                user_id=str(customer_id),
                product_id=str(order_detail.product_id),
                product_variant_id=str(order_detail.product_variant_id) if order_detail.product_variant_id else None
            )

            new_evaluate = await evaluate_repository.create_evaluate(evaluate_create_data, session)

            avg_rating = await evaluate_repository.get_average_rate(
                and_(Evaluate.product_id == order_detail.product_id, Evaluate.deleted_at.is_(None)),
                session
            )
            avg_rating = round(avg_rating, 2) if avg_rating else 0.0

            await product_repository.update_product_some_field(
                Product.id == order_detail.product_id,
                {"avg_rating": avg_rating, "updated_at": datetime.now(), "review_count": Product.review_count + 1},
                session
            )

            await session.commit()
            await session.refresh(new_evaluate)

            new_evaluate_dict = {
                "id": str(new_evaluate.id),
                "comment": new_evaluate.comment,
                "rate": new_evaluate.rate,
                "image": new_evaluate.image,
                "created_at": new_evaluate.created_at.isoformat(),
                "product_id": str(new_evaluate.product_id),
                "product_name": order_detail.product.name if order_detail.product else None,
                "order_detail_id": str(new_evaluate.order_detail_id),
                "user_id": str(new_evaluate.user_id)
            }

            return new_evaluate_dict

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create evaluate")
            raise
