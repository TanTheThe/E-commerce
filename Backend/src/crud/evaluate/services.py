from datetime import datetime
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.evaluate.repositories import EvaluateRepository
from src.crud.product.repositories import ProductRepository
from src.database.models import Evaluate, Order_Detail, User, Order, Product, Product_Variant, Color
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, func, or_, asc, desc
from sqlalchemy.orm import selectinload, joinedload, noload, load_only
from src.schemas.evaluate import EvaluateCreateModel, EvaluateInputModel, SupplementEvaluateModel, GetEvaluateByProduct, \
    EvaluateFilterModel, EvaluateAdditionalModel, ReplyEvaluateModel
from src.errors.evaluate import EvaluateException

evaluate_repository = EvaluateRepository()
order_detail_repository = OrderDetailRepository()
product_repository = ProductRepository()


class EvaluateService:
    async def create_evaluate_service(self, customer_id, evaluate_data: EvaluateInputModel, session: AsyncSession):
        condition = and_(Order_Detail.id == evaluate_data.order_detail_id, Order_Detail.deleted_at.is_(None))
        joins = [
            selectinload(Order_Detail.order).load_only(Order.user_id, Order.status),
        ]
        order_detail = await order_detail_repository.get_order_detail(condition, session, joins)

        if not order_detail:
            EvaluateException.order_detail_not_found()

        if str(customer_id) != str(order_detail.order.user_id):
            EvaluateException.user_not_allowed_to_review()

        if order_detail.order.status not in ("delivered", "received"):
            EvaluateException.order_not_delivered()

        existing_eval = await evaluate_repository.get_by_order_detail_id(evaluate_data.order_detail_id, session)
        if existing_eval and existing_eval.deleted_at is None:
            EvaluateException.already_reviewed()

        evaluate_create_data = EvaluateCreateModel(
            **evaluate_data.model_dump(),
            user_id=str(customer_id),
            product_id=str(order_detail.product_id),
            product_variant_id=str(order_detail.product_variant_id)
        )

        new_evaluate = await evaluate_repository.create_evaluate(evaluate_create_data, session)

        avg_rating = await evaluate_repository.get_average_rate(
            and_(Evaluate.product_id == order_detail.product_id, Evaluate.deleted_at.is_(None)),
            session
        )
        avg_rating = avg_rating if avg_rating else 0.0

        await product_repository.update_product_some_field(
            Product.id == order_detail.product_id,
            {"avg_rating": avg_rating, "updated_at": datetime.now(), "review_count": Product.review_count + 1},
            session
        )

        new_evaluate_dict = {
            "id": str(new_evaluate.id),
            "comment": new_evaluate.comment,
            "rate": new_evaluate.rate,
            "image": new_evaluate.image,
            "created_at": str(new_evaluate.created_at),
            "product_id": str(new_evaluate.product_id),
            "order_detail_id": str(new_evaluate.order_detail_id)
        }

        await session.commit()

        return new_evaluate_dict

    async def get_evaluates_by_customer(self, customer_id: str, session: AsyncSession, skip: int = 0, limit: int = 10):
        condition = [and_(Evaluate.user_id == customer_id)]
        joins = [
            selectinload(Evaluate.user),
            selectinload(Evaluate.product).options(
                selectinload(Product.product_variant),
            ),
            selectinload(Evaluate.product_variant),
        ]
        evaluates = await evaluate_repository.get_all_evaluate(condition, session, None, joins, skip, limit)

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

    async def get_all_evaluate_admin(self, filter_data: EvaluateFilterModel, session: AsyncSession, skip: int = 0,
                                     limit: int = 10):
        conditions = [Evaluate.deleted_at.is_(None)]
        need_join = False

        if filter_data.search and filter_data.search.strip():
            search_term = f"%{filter_data.search.strip()}%"
            full_name_search = func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            conditions.append(or_(
                Order.code.ilike(search_term),
                Product.name.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                full_name_search
            ))
            need_join = True

        if filter_data.rate:
            conditions.append(Evaluate.rate == filter_data.rate)

        order_by = []
        if filter_data.sort_by_rate:
            if filter_data.sort_by_rate == "highest":
                order_by.append(desc(Evaluate.rate))
            else:
                order_by.append(asc(Evaluate.rate))

        if filter_data.sort_by_created_at:
            if filter_data.sort_by_created_at == "newest":
                order_by.append(desc(Evaluate.created_at))
            else:
                order_by.append(asc(Evaluate.created_at))

        if not order_by:
            order_by = [desc(Evaluate.created_at)]

        joins = [
            joinedload(Evaluate.order_detail).options(
                joinedload(Order_Detail.order).load_only(
                    Order.code
                ),
            ),
            joinedload(Evaluate.user).load_only(
                User.first_name,
                User.last_name,
            ),
            joinedload(Evaluate.product).load_only(
                Product.name
            ),
            joinedload(Evaluate.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.name
                )
            ).load_only(
                Product_Variant.color_name,
                Product_Variant.size
            )
        ]

        evaluates, total = await evaluate_repository.get_all_evaluate(conditions, session, order_by, joins, skip, limit,
                                                                      need_join)

        if not evaluates:
            return []

        response = []
        for ev in evaluates:
            response.append({
                "id": str(ev.id),
                "rate": ev.rate,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "product": {
                    "name": ev.product.name if ev.product else None,
                    "size": ev.product_variant.size if ev.product_variant else None,
                    "color_name": (
                        ev.product_variant.color.name
                        if ev.product_variant and ev.product_variant.color
                        else ev.product_variant.color_name if ev.product_variant else None
                    )
                },
                "customer": {
                    "first_name": ev.user.first_name if ev.user else None,
                    "last_name": ev.user.last_name if ev.user else None
                },
                "code": ev.order_detail.order.code if ev.order_detail else None,
            })

        return {
            "data": response,
            "total": total,
        }

    async def get_all_evaluate_customer(self, session: AsyncSession, skip: int = 0, limit: int = 10):
        conditions = [Evaluate.deleted_at.is_(None)]

        joins = [
            joinedload(Evaluate.user).load_only(
                User.first_name,
                User.last_name,
            ),
            joinedload(Evaluate.product).load_only(
                Product.name
            ),
            joinedload(Evaluate.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.name
                )
            ).load_only(
                Product_Variant.color_name,
                Product_Variant.size
            )
        ]

        evaluates, total = await evaluate_repository.get_all_evaluate(conditions, session, None, joins, skip, limit,
                                                                      False)

        if not evaluates:
            return []

        response = []
        for ev in evaluates:
            response.append({
                "id": str(ev.id),
                "rate": ev.rate,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "product": {
                    "name": ev.product.name if ev.product else None,
                    "size": ev.product_variant.size if ev.product_variant else None,
                    "color_name": (
                        ev.product_variant.color.name
                        if ev.product_variant and ev.product_variant.color
                        else ev.product_variant.color_name if ev.product_variant else None
                    )
                },
                "customer": {
                    "first_name": ev.user.first_name if ev.user else None,
                    "last_name": ev.user.last_name if ev.user else None
                },
            })

        return {
            "data": response,
            "total": total,
        }

    async def get_detail_evaluate_admin(self, id: str, session: AsyncSession):
        joins = [
            joinedload(Evaluate.order_detail).options(
                joinedload(Order_Detail.order).load_only(
                    Order.code
                ),
            ),
            joinedload(Evaluate.user).load_only(
                User.first_name,
                User.last_name,
            ),
            joinedload(Evaluate.product).load_only(
                Product.name
            ),
            joinedload(Evaluate.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.name
                )
            ).load_only(
                Product_Variant.color_name,
                Product_Variant.size
            )
        ]

        condition = and_(Evaluate.id == id, Evaluate.deleted_at.is_(None))
        evaluate = await evaluate_repository.get_evaluate(condition, session, joins)

        if not evaluate:
            EvaluateException.review_not_found()

        return {
            "id": str(evaluate.id),
            "rate": evaluate.rate,
            "comment": evaluate.comment,
            "image": evaluate.image,
            "created_at": evaluate.created_at.isoformat() if evaluate.created_at else None,
            "product": {
                "name": evaluate.product.name if evaluate.product else None,
                "size": evaluate.product_variant.size if evaluate.product_variant else None,
                "color_name": (
                    evaluate.product_variant.color.name
                    if evaluate.product_variant and evaluate.product_variant.color
                    else evaluate.product_variant.color_name if evaluate.product_variant else None
                )
            },
            "customer": {
                "first_name": evaluate.user.first_name if evaluate.user else None,
                "last_name": evaluate.user.last_name if evaluate.user else None
            },
            "code": evaluate.order_detail.order.code if evaluate.order_detail else None,
            "additional_comment": evaluate.additional_comment,
            "additional_image": evaluate.additional_image,
            "additional_created_at": evaluate.additional_created_at.isoformat() if evaluate.additional_created_at else None
        }

    async def get_detail_evaluate_customer(self, id: str, customer_id: str, session: AsyncSession):
        joins = [
            joinedload(Evaluate.user).load_only(
                User.first_name,
                User.last_name,
            ),
            joinedload(Evaluate.product).load_only(
                Product.name
            ),
            joinedload(Evaluate.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.name
                )
            ).load_only(
                Product_Variant.color_name,
                Product_Variant.size,
                Product_Variant.image
            ),
            joinedload(Evaluate.order_detail).options(
                joinedload(Order_Detail.order).load_only(
                    Order.code,
                    Order.created_at
                )
            ).load_only(
                Order_Detail.quantity
            )
        ]

        condition = and_(Evaluate.id == id, Evaluate.deleted_at.is_(None), Evaluate.user_id == customer_id)
        evaluate = await evaluate_repository.get_evaluate(condition, session, joins)

        if not evaluate:
            EvaluateException.review_not_found()

        has_additional_evaluation = (
                evaluate.additional_comment is not None or
                evaluate.additional_image is not None
        )

        return {
            "id": str(evaluate.id),
            "rate": evaluate.rate,
            "comment": evaluate.comment,
            "image": evaluate.image,
            "created_at": evaluate.created_at.isoformat() if evaluate.created_at else None,
            "product": {
                "name": evaluate.product.name if evaluate.product else None,
                "variant_image": evaluate.product_variant.image if evaluate.product_variant else None,
                "size": evaluate.product_variant.size if evaluate.product_variant else None,
                "color_name": (
                    evaluate.product_variant.color.name
                    if evaluate.product_variant and evaluate.product_variant.color
                    else evaluate.product_variant.color_name if evaluate.product_variant else None
                ),
                "quantity": evaluate.order_detail.quantity if evaluate.order_detail else None
            },
            "order": {
                "code": evaluate.order_detail.order.code if evaluate.order_detail and evaluate.order_detail.order else None,
                "created_at": (
                    evaluate.order_detail.order.created_at.isoformat()
                    if evaluate.order_detail and evaluate.order_detail.order and evaluate.order_detail.order.created_at
                    else None
                )
            },
            "customer": {
                "first_name": evaluate.user.first_name if evaluate.user else None,
                "last_name": evaluate.user.last_name if evaluate.user else None
            },
            "additional_evaluation": {
                "has_additional": has_additional_evaluation,
                "comment": evaluate.additional_comment,
                "image": evaluate.additional_image,
                "created_at": evaluate.additional_created_at.isoformat() if evaluate.additional_created_at else None,
            },
            "seller_reply": {
                "content": evaluate.seller_reply,
                "replied_at": evaluate.seller_reply_at.isoformat() if evaluate.seller_reply_at else None,
                "has_reply": evaluate.seller_reply is not None
            },
            "meta": {
                "can_add_additional": not has_additional_evaluation,
                "order_detail_id": str(evaluate.order_detail_id),
                "product_id": str(evaluate.product_id),
                "evaluation_status": "complete" if has_additional_evaluation else "basic_only"
            }
        }

    async def get_evaluate_by_product(self, product_id: str, session: AsyncSession,
                                      skip: int = 0, limit: int = 10):
        conditions = [Evaluate.product_id == product_id, Evaluate.deleted_at.is_(None)]
        joins = [
            joinedload(Evaluate.user).load_only(
                User.first_name,
                User.last_name,
            ),
            joinedload(Evaluate.product).load_only(
                Product.name
            ),
            joinedload(Evaluate.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.name
                )
            ).load_only(
                Product_Variant.color_name,
                Product_Variant.size
            )
        ]

        evaluates, total = await evaluate_repository.get_all_evaluate(conditions, session, None, joins, skip, limit,
                                                                      False)

        if not evaluates:
            return []

        response = []
        for ev in evaluates:
            response.append({
                "id": str(ev.id),
                "rate": ev.rate,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "product": {
                    "name": ev.product.name if ev.product else None,
                    "size": ev.product_variant.size if ev.product_variant else None,
                    "color_name": (
                        ev.product_variant.color.name
                        if ev.product_variant and ev.product_variant.color
                        else ev.product_variant.color_name if ev.product_variant else None
                    )
                },
                "customer": {
                    "first_name": ev.user.first_name if ev.user else None,
                    "last_name": ev.user.last_name if ev.user else None
                }
            })

        return {
            "data": response,
            "total": total,
        }

    async def get_average_rate(self, product_id: str, session: AsyncSession):
        conditions = and_(Evaluate.product_id == product_id)
        average = await evaluate_repository.get_average_rate(conditions, session)
        return round(average, 1) if average else 0.0

    async def supplement_evaluate(self, evaluate_id: str, customer_id: str,
                                  data: SupplementEvaluateModel, session: AsyncSession):
        condition = and_(
            Evaluate.id == evaluate_id,
            Evaluate.user_id == customer_id,
            Evaluate.deleted_at.is_(None)
        )
        evaluate = await evaluate_repository.get_evaluate(condition, session)
        if not evaluate:
            EvaluateException.review_not_found()

        if evaluate.additional_comment or evaluate.additional_image:
            EvaluateException.already_supplemented()

        await evaluate_repository.update_evaluate_some_field(condition,
                                                             {"additional_comment": data.additional_comment,
                                                              "additional_created_at": datetime.now(),
                                                              "additional_image": data.additional_image},
                                                             session)

    async def reply_evaluate(self, evaluate_id: str, data: ReplyEvaluateModel, session: AsyncSession):
        condition = and_(
            Evaluate.id == evaluate_id
        )
        evaluate = await evaluate_repository.get_evaluate(condition, session)
        if not evaluate:
            EvaluateException.review_not_found()

        if evaluate.seller_reply:
            EvaluateException.already_reply()

        await evaluate_repository.update_evaluate_some_field(condition,
                                                             {"seller_reply": data.seller_reply,
                                                              "seller_reply_at": datetime.now()},
                                                             session)

    async def delete_evaluate(self, evaluate_id: str, session: AsyncSession):
        condition = and_(Evaluate.id == evaluate_id)
        return await evaluate_repository.delete_evaluate(condition, session)
