from sqlalchemy.orm import selectinload

from src.crud.notification.services.services import NotificationService
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import User, Order, Order_Detail, ReturnOrder
from src.crud.address.repositories import AddressRepository
from src.crud.order.repositories import OrderRepository
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.user.repositories import UserRepository
from src.crud.product.repositories import ProductRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.color.repositories import ColorRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_, func, or_, asc, desc
from src.schemas.order import OrderFilterModel, CancellationStatusType

order_repository = OrderRepository()
special_offer_repository = SpecialOfferRepository()
user_repository = UserRepository()
address_repository = AddressRepository()
product_repository = ProductRepository()
order_detail_repository = OrderDetailRepository()
product_variant_repository = ProductVariantRepository()
color_repository = ColorRepository()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
notification_service = NotificationService()


class GetAllOrdersService:
    async def get_all_order_customer(self, user_id: str, status_order: str, session: AsyncSession, skip: int = 0,
                                     limit: int = 10):
        if status_order == "delivered":
            condition = [
                Order.user_id == user_id,
                Order.status.in_(["delivered", "received"]),
                Order.deleted_at.is_(None)
            ]
            joins = [
                selectinload(Order.order_detail).selectinload(Order_Detail.evaluate),
                selectinload(Order.return_orders)
            ]
        else:
            condition = [Order.user_id == user_id, Order.status == status_order, Order.deleted_at.is_(None)]
            if status_order in ["received"]:
                joins = [
                    selectinload(Order.order_detail).selectinload(Order_Detail.evaluate),
                    selectinload(Order.return_orders)
                ]
            else:
                joins = [selectinload(Order.order_detail)]

        orders, total = await order_repository.get_all_order(condition, session, skip=skip, limit=limit, joins=joins)

        order_response = []
        for order in orders:
            product_map = {}

            for od in order.order_detail:
                pid = str(od.product_id)
                product = od.product_snapshot

                if pid not in product_map:
                    product_map[pid] = {
                        "product_id": pid,
                        "name": product["name"],
                        "variant_image": product["variant_image"],
                        "price_after_discount": product["price_after_discount"],
                        "price_before_discount": product["price_before_discount"],
                        "variants": []
                    }

                variant_info = {
                    "size": product["size"],
                    "color_name": product["color_name"],
                    "quantity": od.quantity,
                    "order_detail_id": str(od.id)
                }

                if status_order in ["delivered", "received"]:
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

            can_show_cancel_button = self.can_show_cancel_button(order)
            has_pending_cancellation = order.cancellation_status == CancellationStatusType.REQUESTED

            active_return_orders = [ro for ro in order.return_orders] if order.return_orders else []
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
                "created_at": str(order.created_at),
                "discount": order.discount,
                "total_price": order.total_price,
                "can_show_cancel_button": can_show_cancel_button,
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
        conditions = [Order.deleted_at.is_(None), User.deleted_at.is_(None)]

        if filter_data.search:
            search_term = f"%{filter_data.search}%"
            full_name_search = func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            conditions.append(or_(
                Order.code.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                full_name_search
            ))
            need_user_join = True
        else:
            need_user_join = False

        if filter_data.status:
            conditions.append(Order.status == filter_data.status)

        order_by = []
        if filter_data.sort_by_total_price:
            if filter_data.sort_by_total_price == "cheapest":
                order_by.append(asc(Order.total_price))
            else:
                order_by.append(desc(Order.total_price))

        if filter_data.sort_by_created_at:
            if filter_data.sort_by_created_at == "newest":
                order_by.append(desc(Order.created_at))
            else:
                order_by.append(asc(Order.created_at))

        joins = [
            selectinload(Order.user).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.deleted_at,
            ),
            selectinload(Order.return_orders).load_only(
                ReturnOrder.id,
                ReturnOrder.status,
            ),
        ]
        orders, total = await order_repository.get_all_order(conditions, session, order_by, skip=skip, limit=limit,
                                                             joins=joins, join_user=need_user_join)

        response = []
        for order in orders:
            user = order.user
            customer_name = f"{user.first_name} {user.last_name}" if user else None

            has_return = len(order.return_orders) > 0
            return_status = None
            if has_return:
                latest_return = order.return_orders[-1]
                return_status = latest_return.status

            order_dict = {
                "id": str(order.id),
                "code": order.code,
                "status": order.status,
                "created_at": str(order.created_at),
                "total_price": order.total_price,
                "sub_total": order.sub_total,
                "discount": order.discount,
                "customer_name": customer_name,
                "payment_method": order.payment_method,
                "has_return": has_return,
                "return_status": return_status,
            }
            response.append(order_dict)

        return {
            "data": response,
            "total": total,
        }
