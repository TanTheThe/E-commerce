from sqlalchemy.orm import selectinload
from src.crud.notification.services import NotificationService
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import User, Order, Order_Detail, OrderStatusHistory, ReturnOrder, ReturnItem
from src.crud.address.repositories import AddressRepository
from src.crud.order.repositories import OrderRepository
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.user.repositories import UserRepository
from src.crud.product.repositories import ProductRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.color.repositories import ColorRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.order import OrderException

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


class GetDetailOrderService:
    async def get_detail_order_admin(self, order_id: str, session: AsyncSession):
        joins = [
            selectinload(Order.order_detail).load_only(
                Order_Detail.id,
                Order_Detail.quantity,
                Order_Detail.product_snapshot
            ),
            selectinload(Order.user).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.email,
                User.phone,
            ),
            selectinload(Order.return_orders).selectinload(ReturnOrder.return_items).load_only(
                ReturnItem.id,
                ReturnItem.order_detail_id,
                ReturnItem.quantity,
                ReturnItem.refund_amount
            ),
        ]

        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        order = await order_repository.get_order(condition, session, joins)

        if not order:
            OrderException.not_found()

        user = order.user
        user_response = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
        } if user else None

        address = order.address_snapshot
        address_response = {
            "line": address.get("line"),
            "street": address.get("street"),
            "ward": address.get("ward"),
            "city": address.get("city"),
            "district": address.get("district"),
            "country": address.get("country"),
        } if address else None

        returned_items_map = {}
        total_refunded = 0

        for return_order in order.return_orders:
            if return_order.status in ["approved", "completed"]:
                for return_item in return_order.return_items:
                    order_detail_id = str(return_item.order_detail_id)
                    if order_detail_id not in returned_items_map:
                        returned_items_map[order_detail_id] = {
                            "quantity": 0,
                            "refund_amount": 0
                        }
                    returned_items_map[order_detail_id]["quantity"] += return_item.quantity
                    returned_items_map[order_detail_id]["refund_amount"] += return_item.refund_amount
                    total_refunded += return_item.refund_amount

        order_detail_response = []
        for od in order.order_detail:
            product_snapshot = od.product_snapshot
            order_detail_id = str(od.id)

            returned_info = returned_items_map.get(order_detail_id)
            is_returned = returned_info is not None
            returned_quantity = returned_info["quantity"] if is_returned else 0
            refund_amount = returned_info["refund_amount"] if is_returned else 0

            product_dict = {
                "id": order_detail_id,
                "name": product_snapshot.get("name"),
                "variant_image": product_snapshot.get("variant_image"),
                "price": product_snapshot.get("price_after_discount"),
                "quantity": od.quantity,
                "size": product_snapshot.get("size"),
                "color": product_snapshot.get("color_name"),
                "is_returned": is_returned,
                "returned_quantity": returned_quantity,
                "refund_amount": refund_amount,
            }

            order_detail_response.append(product_dict)

        final_total = order.total_price - total_refunded

        response = {
            "order": {
                "id": str(order.id),
                "code": order.code,
                "note": order.note,
                "status": order.status,
                "created_at": str(order.created_at),
                "sub_total": order.sub_total,
                "discount": order.discount,
                "total_price": order.total_price,
                "total_refunded": total_refunded,
                "final_total": final_total,
            },
            "customer": user_response,
            "address": address_response,
            "order_detail": order_detail_response
        }

        return response

    async def get_detail_order_customer(self, order_id: str, customer_id: str, session: AsyncSession):
        joins = [
            selectinload(Order.order_detail), selectinload(Order.user),
        ]

        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        order = await order_repository.get_order(condition, session, joins)

        if not order:
            OrderException.not_found()

        if str(order.user_id) != str(customer_id):
            OrderException.unauthorized_order()

        user = order.user
        user_response = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
        } if user else None

        address = order.address_snapshot
        address_response = {
            "line": address["line"],
            "street": address["street"],
            "ward": address["ward"],
            "city": address["city"],
            "district": address["district"],
            "country": address["country"],
        } if address else None

        condition_status = and_(OrderStatusHistory.order_id == order_id)
        latest_status = await order_repository.get_new_status_order(condition_status, session)
        latest_status_response = None
        if latest_status:
            latest_status_response = {
                "status": latest_status.status,
                "changed_at": str(latest_status.created_at),
            }

        order_detail_response = []
        for od in order.order_detail:
            product_dict = {
                "name": od.product_snapshot["name"],
                "size": od.product_snapshot["size"],
                "color_name": od.product_snapshot["color_name"],
                "product_image": od.product_snapshot["product_image"],
                "variant_image": od.product_snapshot["variant_image"],
                "price_after_discount": od.product_snapshot["price_after_discount"],
                "price_before_discount": od.product_snapshot["price_before_discount"],
                "quantity": od.quantity
            }

            order_detail_response.append(product_dict)

        response = {
            "order": {
                "code": order.code,
                "note": order.note,
                "status": order.status,
                "created_at": str(order.created_at),
                "last_status_change": latest_status_response,
                "sub_total": order.sub_total,
                "discount": order.discount,
                "total_price": order.total_price,
            },
            "customer": user_response,
            "address": address_response,
            "order_detail": order_detail_response
        }

        return response
