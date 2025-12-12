from sqlalchemy.orm import selectinload
from src.database.models import User, Order, Order_Detail, ReturnOrder
from src.crud.order.repositories import OrderRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import func, or_, asc, desc

from src.errors.order import OrderException
from src.schemas.order import OrderFilterModel, CancellationStatusType

order_repository = OrderRepository()


class GetAllOrdersService:
    async def get_all_order_customer(self, user_id: str, status_order: str, session: AsyncSession, skip: int = 0,
                                     limit: int = 10):
        valid_statuses = ["pending", "confirmed", "shipping", "delivered",
                          "received", "cancelled", "returned", "all"]

        if status_order not in valid_statuses:
            OrderException.invalid_status(valid_statuses)

        conditions = [
            Order.user_id == user_id,
            Order.deleted_at.is_(None)
        ]

        if status_order == "delivered":
            conditions.append(Order.status.in_(["delivered", "received"]))
        elif status_order != "all":
            conditions.append(Order.status == status_order)

        if status_order in ["delivered", "received"]:
            options = [
                selectinload(Order.order_detail).selectinload(Order_Detail.evaluate),
                selectinload(Order.return_orders)
            ]
        else:
            options = [selectinload(Order.order_detail)]

        order_by = desc(Order.created_at)

        orders, total = await order_repository.get_all_order(session=session, where_conditions=conditions, skip=skip,
                                                             limit=limit, options=options, order_by=order_by)

        order_response = []
        for order in orders:
            product_map = {}

            for od in order.order_detail:
                pid = str(od.product_id)
                product = od.product_snapshot

                if pid not in product_map:
                    product_map[pid] = {
                        "product_id": pid,
                        "name": product.get("name"),
                        "variant_image": product.get("variant_image"),
                        "price_after_discount": product.get("price_after_discount"),
                        "price_before_discount": product.get("price_before_discount"),
                        "variants": []
                    }

                variant_info = {
                    "size": product.get("size"),
                    "color_name": product.get("color_name"),
                    "quantity": od.quantity,
                    "order_detail_id": str(od.id)
                }

                if status_order in ["delivered", "received", "all"]:
                    has_evaluation = od.evaluate is not None and od.evaluate.deleted_at is None
                    variant_info["has_evaluation"] = has_evaluation

                    if has_evaluation:
                        variant_info["evaluation_id"] = str(od.evaluate.id)
                        has_additional_evaluation = (
                                od.evaluate.additional_comment is not None or
                                od.evaluate.additional_image is not None
                        )
                        variant_info["has_additional_evaluation"] = has_additional_evaluation

                product_map[pid]["variants"].append(variant_info)

            can_show_cancel = self.can_show_cancel_button(order)
            has_pending_cancellation = order.cancellation_status == CancellationStatusType.REQUESTED

            active_return_orders = [ro for ro in order.return_orders if
                                    ro.deleted_at is None] if order.return_orders else []
            has_return_orders = len(active_return_orders) > 0

            return_orders_info = []
            if has_return_orders:
                for return_order in active_return_orders:
                    return_orders_info.append({
                        "return_order_id": str(return_order.id),
                        "status": return_order.status,
                        "reason": return_order.reason,
                        "created_at": str(return_order.created_at)
                    })

            order_info = {
                "order_id": str(order.id),
                "code": order.code,
                "status": order.status,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "created_at": str(order.created_at),
                "discount": order.discount,
                "sub_total": order.sub_total,
                "total_price": order.total_price,
                "can_show_cancel_button": can_show_cancel,
                "has_pending_cancellation": has_pending_cancellation,
                "cancellation_status": order.cancellation_status,
                "cancellation_reason": order.cancellation_reason if has_pending_cancellation else None,
                "has_return_orders": has_return_orders,
                "return_orders": return_orders_info
            }

            if order.payment_method == "vnpay":
                if order.payment_status == "success":
                    order_info["paid_amount"] = order.total_price
                elif order.payment_status == "pending":
                    order_info["paid_amount"] = 0

            order_response.append({
                "order": order_info,
                "order_detail": list(product_map.values())
            })

        return {"total": total, "data": order_response}

    def can_show_cancel_button(self, order: Order) -> bool:
        if order.status in ["cancelled", "delivered", "shipping", "received"]:
            return False

        if order.cancellation_status == CancellationStatusType.REQUESTED:
            return False

        if order.status in ["pending", "confirmed"]:
            return True

        return False

    async def get_all_order_admin(self, session: AsyncSession, filter_data: OrderFilterModel, skip: int = 0,
                                  limit: int = 10):
        conditions = [
            Order.deleted_at.is_(None),
            User.deleted_at.is_(None)
        ]

        joins = []
        if filter_data.search:
            search_term = f"%{filter_data.search}%"
            full_name_search = func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            conditions.append(or_(
                Order.code.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                full_name_search
            ))
            joins.append(
                (User, {"on": Order.user_id == User.id})
            )

        if filter_data.status:
            conditions.append(Order.status == filter_data.status.value)

        order_by = None
        if filter_data.sort_by_total_price:
            if filter_data.sort_by_total_price == "cheapest":
                order_by = asc(Order.total_price)
            else:
                order_by = desc(Order.total_price)

        if filter_data.sort_by_created_at:
            if filter_data.sort_by_created_at == "newest":
                order_by = desc(Order.created_at)
            else:
                order_by = asc(Order.created_at)

        if order_by is None:
            order_by = desc(Order.created_at)

        options = [
            selectinload(Order.user).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.deleted_at,
            ),
            selectinload(Order.return_orders).load_only(
                ReturnOrder.id,
                ReturnOrder.status,
                ReturnOrder.created_at,
            ),
        ]
        orders, total = await order_repository.get_all_order(session=session, where_conditions=conditions, order_by=order_by,
                                                             skip=skip, limit=limit, options=options, joins=joins)

        response = []
        for order in orders:
            user = order.user
            customer_name = f"{user.first_name} {user.last_name}" if user else None

            active_returns = [ro for ro in order.return_orders if ro.deleted_at is None] if order.return_orders else []
            has_return = len(active_returns) > 0
            return_status = None

            if has_return:
                latest_return = max(active_returns, key=lambda x: x.created_at)
                return_status = latest_return.status

            order_dict = {
                "id": str(order.id),
                "code": order.code,
                "status": order.status,
                "created_at": str(order.created_at),
                "total_price": order.total_price,
                "sub_total": order.sub_total,
                "discount": order.discount,
                "discount_percent": order.discount_percent if hasattr(order, 'discount_percent') else 0,
                "customer_name": customer_name,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "has_return": has_return,
                "return_status": return_status,
                "cancellation_status": order.cancellation_status,
            }
            response.append(order_dict)

        return {
            "data": response,
            "total": total,
        }
