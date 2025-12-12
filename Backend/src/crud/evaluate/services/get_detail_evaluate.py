from datetime import datetime
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.evaluate.repositories import EvaluateRepository
from src.crud.product.repositories import ProductRepository
from src.database.models import Evaluate, Order_Detail, User, Order, Product, Product_Variant, Color
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload
from src.errors.evaluate import EvaluateException
import logging

logger = logging.getLogger(__name__)

evaluate_repository = EvaluateRepository()
order_detail_repository = OrderDetailRepository()
product_repository = ProductRepository()


class GetDetailEvaluateService:
    async def get_detail_evaluate_admin(self, id: str, session: AsyncSession):
        options = [
            joinedload(Evaluate.order_detail).options(
                joinedload(Order_Detail.order).load_only(
                    Order.id,
                    Order.code,
                    Order.status,
                    Order.created_at
                )
            ).load_only(
                Order_Detail.id,
                Order_Detail.quantity,
                Order_Detail.price
            ),
            joinedload(Evaluate.user).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.email,
                User.phone
            ),
            joinedload(Evaluate.product).load_only(
                Product.id,
                Product.name,
                Product.slug,
                Product.avg_rating,
                Product.review_count
            ),
            joinedload(Evaluate.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.id,
                    Color.name
                )
            ).load_only(
                Product_Variant.id,
                Product_Variant.color_name,
                Product_Variant.size,
                Product_Variant.image
            )
        ]

        condition = [Evaluate.id == id, Evaluate.deleted_at.is_(None)]
        evaluate = await evaluate_repository.get_evaluate(session=session, where_conditions=condition, options=options)

        if not evaluate:
            EvaluateException.review_not_found()

        has_additional_evaluation = (
            evaluate.additional_comment is not None or
            evaluate.additional_image is not None
        )

        has_seller_reply = evaluate.seller_reply is not None

        return {
            "id": str(evaluate.id),
            "rate": evaluate.rate,
            "comment": evaluate.comment,
            "image": evaluate.image,
            "created_at": evaluate.created_at.isoformat() if evaluate.created_at else None,
            "product": {
                "id": str(evaluate.product.id) if evaluate.product else None,
                "name": evaluate.product.name if evaluate.product else None,
                "slug": evaluate.product.slug if evaluate.product else None,
                "avg_rating": float(evaluate.product.avg_rating) if evaluate.product and evaluate.product.avg_rating else 0.0,
                "review_count": evaluate.product.review_count if evaluate.product else 0,
                "variant": {
                    "id": str(evaluate.product_variant.id) if evaluate.product_variant else None,
                    "image": evaluate.product_variant.image if evaluate.product_variant else None,
                    "size": evaluate.product_variant.size if evaluate.product_variant else None,
                    "color_name": (
                        evaluate.product_variant.color.name
                        if evaluate.product_variant and evaluate.product_variant.color
                        else evaluate.product_variant.color_name if evaluate.product_variant
                        else None
                    )
                } if evaluate.product_variant else None
            },
            "customer": {
                "id": str(evaluate.user.id) if evaluate.user else None,
                "first_name": evaluate.user.first_name if evaluate.user else None,
                "last_name": evaluate.user.last_name if evaluate.user else None,
                "full_name": f"{evaluate.user.first_name} {evaluate.user.last_name}".strip() if evaluate.user else None,
                "email": evaluate.user.email if evaluate.user else None,
                "phone": evaluate.user.phone if evaluate.user else None
            },
            "order": {
                "id": str(evaluate.order_detail.order.id) if evaluate.order_detail and evaluate.order_detail.order else None,
                "code": evaluate.order_detail.order.code if evaluate.order_detail and evaluate.order_detail.order else None,
                "status": evaluate.order_detail.order.status if evaluate.order_detail and evaluate.order_detail.order else None,
                "created_at": (
                    evaluate.order_detail.order.created_at.isoformat()
                    if evaluate.order_detail and evaluate.order_detail.order and evaluate.order_detail.order.created_at
                    else None
                ),
                "order_detail_id": str(evaluate.order_detail.id) if evaluate.order_detail else None,
                "quantity": evaluate.order_detail.quantity if evaluate.order_detail else None,
                "price": float(evaluate.order_detail.price) if evaluate.order_detail and evaluate.order_detail.price else None
            },
            "additional_evaluation": {
                "has_additional": has_additional_evaluation,
                "comment": evaluate.additional_comment,
                "image": evaluate.additional_image,
                "created_at": evaluate.additional_created_at.isoformat() if evaluate.additional_created_at else None
            },
            "seller_reply": {
                "has_reply": has_seller_reply,
                "content": evaluate.seller_reply,
                "replied_at": evaluate.seller_reply_at.isoformat() if evaluate.seller_reply_at else None
            },
            "meta": {
                "evaluation_status": "complete" if has_additional_evaluation else "basic_only",
                "can_reply": not has_seller_reply,  # Admin có thể reply nếu chưa reply
                "product_id": str(evaluate.product_id),
                "user_id": str(evaluate.user_id)
            }
        }

    async def get_detail_evaluate_customer(self, id: str, customer_id: str, session: AsyncSession):
        options = [
            joinedload(Evaluate.user).load_only(
                User.id,
                User.first_name,
                User.last_name
            ),
            joinedload(Evaluate.product).load_only(
                Product.id,
                Product.name,
                Product.slug,
                Product.avg_rating,
                Product.review_count
            ),
            joinedload(Evaluate.product_variant).options(
                joinedload(Product_Variant.color).load_only(
                    Color.id,
                    Color.name
                )
            ).load_only(
                Product_Variant.id,
                Product_Variant.color_name,
                Product_Variant.size,
                Product_Variant.image
            ),
            joinedload(Evaluate.order_detail).options(
                joinedload(Order_Detail.order).load_only(
                    Order.id,
                    Order.code,
                    Order.status,
                    Order.created_at
                )
            ).load_only(
                Order_Detail.id,
                Order_Detail.quantity,
                Order_Detail.price
            )
        ]

        condition = [Evaluate.id == id, Evaluate.deleted_at.is_(None), Evaluate.user_id == customer_id]
        evaluate = await evaluate_repository.get_evaluate(session=session, where_conditions=condition, options=options)

        if not evaluate:
            EvaluateException.review_not_found()

        has_additional_evaluation = (
            evaluate.additional_comment is not None or
            evaluate.additional_image is not None
        )

        has_seller_reply = evaluate.seller_reply is not None

        can_add_additional = not has_additional_evaluation
        if can_add_additional and evaluate.created_at:
            days_since_review = (datetime.now() - evaluate.created_at).days
            if days_since_review > 7:
                can_add_additional = False

        return {
            "id": str(evaluate.id),
            "rate": evaluate.rate,
            "comment": evaluate.comment,
            "image": evaluate.image,
            "created_at": evaluate.created_at.isoformat() if evaluate.created_at else None,
            "product": {
                "id": str(evaluate.product.id) if evaluate.product else None,
                "name": evaluate.product.name if evaluate.product else None,
                "slug": evaluate.product.slug if evaluate.product else None,
                "avg_rating": float(
                    evaluate.product.avg_rating) if evaluate.product and evaluate.product.avg_rating else 0.0,
                "review_count": evaluate.product.review_count if evaluate.product else 0,
                "variant": {
                    "id": str(evaluate.product_variant.id) if evaluate.product_variant else None,
                    "image": evaluate.product_variant.image if evaluate.product_variant else None,
                    "size": evaluate.product_variant.size if evaluate.product_variant else None,
                    "color_name": (
                        evaluate.product_variant.color.name
                        if evaluate.product_variant and evaluate.product_variant.color
                        else evaluate.product_variant.color_name if evaluate.product_variant
                        else None
                    )
                } if evaluate.product_variant else None
            },
            "order": {
                "id": str(
                    evaluate.order_detail.order.id) if evaluate.order_detail and evaluate.order_detail.order else None,
                "code": evaluate.order_detail.order.code if evaluate.order_detail and evaluate.order_detail.order else None,
                "status": evaluate.order_detail.order.status if evaluate.order_detail and evaluate.order_detail.order else None,
                "created_at": (
                    evaluate.order_detail.order.created_at.isoformat()
                    if evaluate.order_detail and evaluate.order_detail.order and evaluate.order_detail.order.created_at
                    else None
                ),
                "order_detail_id": str(evaluate.order_detail.id) if evaluate.order_detail else None,
                "quantity": evaluate.order_detail.quantity if evaluate.order_detail else None,
                "price": float(
                    evaluate.order_detail.price) if evaluate.order_detail and evaluate.order_detail.price else None
            },
            "customer": {
                "id": str(evaluate.user.id) if evaluate.user else None,
                "first_name": evaluate.user.first_name if evaluate.user else None,
                "last_name": evaluate.user.last_name if evaluate.user else None,
                "full_name": f"{evaluate.user.first_name} {evaluate.user.last_name}".strip() if evaluate.user else None
            },
            "additional_evaluation": {
                "has_additional": has_additional_evaluation,
                "comment": evaluate.additional_comment,
                "image": evaluate.additional_image,
                "created_at": evaluate.additional_created_at.isoformat() if evaluate.additional_created_at else None
            },
            "seller_reply": {
                "has_reply": has_seller_reply,
                "content": evaluate.seller_reply,
                "replied_at": evaluate.seller_reply_at.isoformat() if evaluate.seller_reply_at else None
            },
            "meta": {
                "can_add_additional": can_add_additional,
                "can_add_additional_reason": None if can_add_additional else (
                    "Đã thêm đánh giá bổ sung" if has_additional_evaluation else "Đã quá thời hạn (7 ngày)"
                ),
                "order_detail_id": str(evaluate.order_detail_id),
                "product_id": str(evaluate.product_id),
                "evaluation_status": "complete" if has_additional_evaluation else "basic_only",
                "days_since_review": (datetime.now() - evaluate.created_at).days if evaluate.created_at else None
            }
        }

