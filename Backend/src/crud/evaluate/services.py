from sqlalchemy.orm import selectinload
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.evaluate.repositories import EvaluateRepository
from src.database.models import Evaluate, Order_Detail
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.schemas.evaluate import EvaluateCreateModel, EvaluateInputModel, SupplementEvaluateModel, GetEvaluateByProduct
from src.errors.evaluate import EvaluateException

evaluate_repository = EvaluateRepository()
order_detail_repository = OrderDetailRepository()

class EvaluateService:
    async def create_evaluate_service(self, customer_id, evaluate_data: EvaluateInputModel, session: AsyncSession):
        condition = and_(Order_Detail.id == evaluate_data.order_detail_id)
        joins = [selectinload(Order_Detail.order)]
        order_detail = await order_detail_repository.get_order_detail(condition, session, joins)

        if not order_detail:
            EvaluateException.order_detail_not_found()

        if str(customer_id) != str(order_detail.order.user_id):
            EvaluateException.user_not_allowed_to_review()

        existing_eval = await evaluate_repository.get_by_order_detail_id(evaluate_data.order_detail_id, session)
        if existing_eval:
            EvaluateException.already_reviewed()

        evaluate_create_data = EvaluateCreateModel(
            **evaluate_data.model_dump(),
            user_id=str(customer_id),
            product_id=str(order_detail.product_id),
            product_variant_id=str(order_detail.product_variant_id)
        )

        new_evaluate = await evaluate_repository.create_evaluate(evaluate_create_data, session)

        new_evaluate_dict = {
            "id": str(new_evaluate.id),
            "comment": new_evaluate.comment,
            "rate": new_evaluate.rate,
            "image": new_evaluate.image
        }

        await session.commit()

        return new_evaluate_dict

    async def get_evaluates_by_customer(self, customer_id: str, session: AsyncSession, skip: int = 0, limit: int = 10):
        condition = and_(Evaluate.user_id == customer_id)
        joins = [
            selectinload(Evaluate.user), selectinload(Evaluate.product), selectinload(Evaluate.product_variant)
        ]
        evaluates = await evaluate_repository.get_all_evaluate(condition, session, joins, skip, limit)

        if not evaluates:
            return []

        response = []
        for ev in evaluates:
            response.append({
                "id": str(ev.id),
                "rate": ev.rate,
                "comment": ev.comment,
                "image": ev.image,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "product": {
                    "name": ev.product.name if ev.product else None,
                    "size": ev.product_variant.size if ev.product_variant else None,
                    "color": ev.product_variant.color if ev.product_variant else None
                },
                "customer": {
                    "first_name": ev.user.first_name if ev.user else None,
                    "last_name": ev.user.last_name if ev.user else None
                }
            })

        return response


    async def get_all_evaluate_admin(self, session: AsyncSession, skip: int = 0, limit: int = 10):
        joins = [
            selectinload(Evaluate.order_detail).selectinload(Order_Detail.order), selectinload(Evaluate.user),
            selectinload(Evaluate.product), selectinload(Evaluate.product_variant)
        ]
        evaluates = await evaluate_repository.get_all_evaluate(None, session, joins, skip, limit)

        if not evaluates:
            return []

        response = []
        for ev in evaluates:
            response.append({
                "id": str(ev.id),
                "rate": ev.rate,
                "comment": ev.comment,
                "image": ev.image,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "product": {
                    "name": ev.product.name if ev.product else None,
                    "size": ev.product_variant.size if ev.product_variant else None,
                    "color": ev.product_variant.color if ev.product_variant else None
                },
                "customer": {
                    "first_name": ev.user.first_name if ev.user else None,
                    "last_name": ev.user.last_name if ev.user else None
                },
                "code": ev.order_detail.order.code if ev.order_detail else None,
            })

        return response


    async def get_all_evaluate_customer(self, session: AsyncSession, skip: int = 0, limit: int = 10):
        joins = [
            selectinload(Evaluate.user), selectinload(Evaluate.product), selectinload(Evaluate.product_variant)
        ]
        evaluates = await evaluate_repository.get_all_evaluate(None, session, joins, skip, limit)

        if not evaluates:
            return []

        response = []
        for ev in evaluates:
            response.append({
                "id": str(ev.id),
                "rate": ev.rate,
                "comment": ev.comment,
                "image": ev.image,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "product": {
                    "name": ev.product.name if ev.product else None,
                    "size": ev.product_variant.size if ev.product_variant else None,
                    "color": ev.product_variant.color if ev.product_variant else None
                },
                "customer": {
                    "first_name": ev.user.first_name if ev.user else None,
                    "last_name": ev.user.last_name if ev.user else None
                }
            })

        return response


    async def get_evaluate_by_product(self, product_id: str, data: GetEvaluateByProduct, session: AsyncSession, skip: int = 0, limit: int = 10):
        conditions = [Evaluate.product_id == product_id]
        if data.variant_id:
            conditions.append(Evaluate.product_variant_id == data.variant_id)

        if data.rate:
            conditions.append(Evaluate.rate == data.rate)

        condition = and_(*conditions)

        joins = [selectinload(Evaluate.user), selectinload(Evaluate.product_variant)]
        evaluates = await evaluate_repository.get_all_evaluate(condition, session, joins, skip, limit)

        if not evaluates:
            return []

        response = []
        for ev in evaluates:
            response.append({
                "id": str(ev.id),
                "rate": ev.rate,
                "comment": ev.comment,
                "image": ev.image,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "customer": {
                    "first_name": ev.user.first_name if ev.user else None,
                    "last_name": ev.user.last_name if ev.user else None
                },
                "variant": {
                    "size": ev.product_variant.size if ev.product_variant else None,
                    "color": ev.product_variant.color if ev.product_variant else None
                },
                "additional_comment": ev.additional_comment,
                "additional_image": ev.additional_image,
                "additional_created_at": ev.additional_created_at.isoformat() if ev.additional_created_at else None
            })

        return response


    async def get_average_rate(self, product_id: str, session: AsyncSession):
        conditions = and_(Evaluate.product_id == product_id)
        average = await evaluate_repository.get_average_rate(conditions, session)
        return round(average, 1) if average else 0.0


    async def supplement_evaluate(self, evaluate_id: str, customer_id: str,
                                  data: SupplementEvaluateModel, session: AsyncSession):
        condition = and_(
            Evaluate.id == evaluate_id,
            Evaluate.user_id == customer_id
        )
        await evaluate_repository.supplement_evaluate(data, condition, session)
        await session.commit()


    async def delete_evaluate(self, evaluate_id: str, session: AsyncSession):
        condition = and_(Evaluate.id == evaluate_id)
        return await evaluate_repository.delete_evaluate(condition, session)