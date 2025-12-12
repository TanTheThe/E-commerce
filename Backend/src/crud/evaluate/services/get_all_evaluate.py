from typing import Optional
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.evaluate.repositories import EvaluateRepository
from src.crud.product.repositories import ProductRepository
from src.database.models import Evaluate, Order_Detail, User, Order, Product, Product_Variant, Color
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import func, or_, asc, desc
from sqlalchemy.orm import joinedload
from src.schemas.evaluate import EvaluateFilterModel
from src.errors.evaluate import EvaluateException
import logging

logger = logging.getLogger(__name__)

evaluate_repository = EvaluateRepository()
order_detail_repository = OrderDetailRepository()
product_repository = ProductRepository()


class GetAllEvaluateService:
    async def get_all_evaluate_admin(self, filter_data: EvaluateFilterModel, session: AsyncSession, skip: int = 0,
                                     limit: int = 10):
        if skip < 0:
            EvaluateException.skip_cant_be_negative()

        if limit < 1 or limit > 100:
            EvaluateException.limit_must_be_1_to_100()

        conditions = [Evaluate.deleted_at.is_(None)]
        joins = []

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

            joins = [
                (Product, {"on": Evaluate.product_id == Product.id}),
                (User, {"on": Evaluate.user_id == User.id}),
                (Order_Detail, {"on": Evaluate.order_detail_id == Order_Detail.id}),
                (Order, {"on": Order_Detail.order_id == Order.id}),
            ]

        if filter_data.rate:
            conditions.append(Evaluate.rate == filter_data.rate)

        if filter_data.product_id:
            conditions.append(Evaluate.product_id == filter_data.product_id)

        if filter_data.user_id:
            conditions.append(Evaluate.user_id == filter_data.user_id)

        order_by = None
        if filter_data.sort_by_rate:
            if filter_data.sort_by_rate == "highest":
                order_by = desc(Evaluate.rate)
            else:
                order_by = asc(Evaluate.rate)

        if filter_data.sort_by_created_at:
            if filter_data.sort_by_created_at == "newest":
                order_by = desc(Evaluate.created_at)
            else:
                order_by = asc(Evaluate.created_at)

        if not order_by:
            order_by = desc(Evaluate.created_at)

        options = [
            joinedload(Evaluate.order_detail).options(
                joinedload(Order_Detail.order).load_only(Order.code)
            ),
            joinedload(Evaluate.user).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.email
            ),
            joinedload(Evaluate.product).load_only(
                Product.id,
                Product.name,
                Product.slug
            ),
            joinedload(Evaluate.product_variant).options(
                joinedload(Product_Variant.color).load_only(Color.name)
            ).load_only(
                Product_Variant.id,
                Product_Variant.color_name,
                Product_Variant.size
            )
        ]

        evaluates, total = await evaluate_repository.get_all_evaluate(session=session, where_conditions=conditions,
                                                                      order_by=order_by, options=options, skip=skip,
                                                                      limit=limit, joins=joins)

        if not evaluates:
            return {
                "data": [],
                "total": 0,
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "limit": limit,
                "total_pages": 0
            }

        response = []
        for ev in evaluates:
            evaluate_data = {
                "id": str(ev.id),
                "comment": ev.comment,
                "rate": ev.rate,
                "image": ev.image,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "product": {
                    "id": str(ev.product.id) if ev.product else None,
                    "name": ev.product.name if ev.product else None,
                    "slug": ev.product.slug if ev.product else None,
                    "variant": {
                        "id": str(ev.product_variant.id) if ev.product_variant else None,
                        "size": ev.product_variant.size if ev.product_variant else None,
                        "color_name": (
                            ev.product_variant.color.name
                            if ev.product_variant and ev.product_variant.color
                            else ev.product_variant.color_name if ev.product_variant
                            else None
                        )
                    } if ev.product_variant else None
                },
                "customer": {
                    "id": str(ev.user.id) if ev.user else None,
                    "first_name": ev.user.first_name if ev.user else None,
                    "last_name": ev.user.last_name if ev.user else None,
                    "email": ev.user.email if ev.user else None,
                    "full_name": f"{ev.user.first_name} {ev.user.last_name}".strip() if ev.user else None
                },
                "order_code": ev.order_detail.order.code if ev.order_detail and ev.order_detail.order else None,
                "order_detail_id": str(ev.order_detail_id) if ev.order_detail_id else None
            }
            response.append(evaluate_data)

        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "data": response,
            "total": total,
            "page": current_page,
            "limit": limit,
            "total_pages": total_pages
        }

    async def get_all_evaluate_customer(self, filter_data: Optional[EvaluateFilterModel], session: AsyncSession,
                                        skip: int = 0, limit: int = 10):
        if skip < 0:
            EvaluateException.skip_cant_be_negative()

        if limit < 1 or limit > 100:
            EvaluateException.limit_must_be_1_to_100()

        conditions = [Evaluate.deleted_at.is_(None)]

        if filter_data:
            if filter_data.rate:
                conditions.append(Evaluate.rate == filter_data.rate)

            if filter_data.product_id:
                conditions.append(Evaluate.product_id == filter_data.product_id)

        order_by = [desc(Evaluate.created_at)]

        if filter_data and filter_data.sort_by_rate:
            if filter_data.sort_by_rate == "highest":
                order_by.insert(0, desc(Evaluate.rate))
            else:
                order_by.insert(0, asc(Evaluate.rate))

        options = [
            joinedload(Evaluate.user).load_only(
                User.id,
                User.first_name,
                User.last_name
            ),
            joinedload(Evaluate.product).load_only(
                Product.id,
                Product.name,
                Product.slug
            ),
            joinedload(Evaluate.product_variant).options(
                joinedload(Product_Variant.color).load_only(Color.name)
            ).load_only(
                Product_Variant.id,
                Product_Variant.color_name,
                Product_Variant.size
            )
        ]

        evaluates, total = await evaluate_repository.get_all_evaluate(session=session, where_conditions=conditions,
                                                                      order_by=order_by, options=options, skip=skip,
                                                                      limit=limit)

        if not evaluates:
            return {
                "data": [],
                "total": 0,
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "limit": limit,
                "total_pages": 0
            }

        response = []
        for ev in evaluates:
            evaluate_data = {
                "id": str(ev.id),
                "comment": ev.comment,
                "rate": ev.rate,
                "image": ev.image,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "product": {
                    "id": str(ev.product.id) if ev.product else None,
                    "name": ev.product.name if ev.product else None,
                    "slug": ev.product.slug if ev.product else None,
                    "variant": {
                        "id": str(ev.product_variant.id) if ev.product_variant else None,
                        "size": ev.product_variant.size if ev.product_variant else None,
                        "color_name": (
                            ev.product_variant.color.name
                            if ev.product_variant and ev.product_variant.color
                            else ev.product_variant.color_name if ev.product_variant
                            else None
                        )
                    } if ev.product_variant else None
                },
                "customer": {
                    "id": str(ev.user.id) if ev.user else None,
                    "first_name": ev.user.first_name if ev.user else None,
                    "last_name": ev.user.last_name if ev.user else None,
                    "full_name": f"{ev.user.first_name} {ev.user.last_name}".strip() if ev.user else None
                }
            }
            response.append(evaluate_data)

        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "data": response,
            "total": total,
            "page": current_page,
            "limit": limit,
            "total_pages": total_pages
        }


