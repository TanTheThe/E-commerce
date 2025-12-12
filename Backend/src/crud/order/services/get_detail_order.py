from sqlalchemy.orm import selectinload
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


class GetDetailOrderService:
    async def get_detail_order_admin(self, order_id: str, session: AsyncSession):
        options = [
            selectinload(Order.order_detail).load_only(
                Order_Detail.id,
                Order_Detail.quantity,
                Order_Detail.price,
                Order_Detail.product_snapshot
            ),
            selectinload(Order.user).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.email,
                User.phone,
                User.deleted_at,
            ),
            selectinload(Order.return_orders).options(
                selectinload(ReturnOrder.return_items).load_only(
                    ReturnItem.id,
                    ReturnItem.order_detail_id,
                    ReturnItem.quantity,
                    ReturnItem.refund_amount
                )
            ).load_only(
                ReturnOrder.id,
                ReturnOrder.status,
                ReturnOrder.reason,
                ReturnOrder.created_at,
                ReturnOrder.deleted_at,
            ),
        ]

        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        order = await order_repository.get_order(session=session, where_conditions=condition, options=options)

        if not order:
            OrderException.not_found()

        if order.user and order.user.deleted_at is not None:
            pass

        returned_items_map, total_refunded = self.calculate_returned_items(order.return_orders)

        user = order.user
        user_response = None
        if user:
            user_response = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "is_deleted": user.deleted_at is not None
            }

        address_snapshot = order.address_snapshot
        if not address_snapshot:
            return None

        address_response = None
        if "ward" in address_snapshot and isinstance(address_snapshot["ward"], dict):
            address_response = {
                "line": address_snapshot.get("line"),
                "ward": address_snapshot.get("ward"),
                "province": address_snapshot.get("province"),
                "district": address_snapshot.get("district"),
                "country": address_snapshot.get("country", "Việt Nam"),
            }

        special_offer_response = None
        if order.special_offer_snapshot:
            special_offer_response = {
                "id": order.special_offer_snapshot.get("id"),
                "code": order.special_offer_snapshot.get("code"),
                "name": order.special_offer_snapshot.get("name"),
                "discount": order.special_offer_snapshot.get("discount"),
                "type": order.special_offer_snapshot.get("type"),
                "condition": order.special_offer_snapshot.get("condition"),
            }

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
                "product_image": product_snapshot.get("product_image"),
                "price": product_snapshot.get("price_after_discount"),
                "price_before_discount": product_snapshot.get("price_before_discount"),
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
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "created_at": str(order.created_at),
                "updated_at": str(order.updated_at) if order.updated_at else None,
                "estimated_delivery_date": str(order.estimated_delivery_date) if order.estimated_delivery_date else None,
                "sub_total": order.sub_total,
                "discount": order.discount,
                "discount_percent": order.discount_percent if hasattr(order, 'discount_percent') else 0,
                "total_price": order.total_price,
                "total_refunded": total_refunded,
                "final_total": final_total,
                "cancellation_status": order.cancellation_status,
                "cancellation_reason": order.cancellation_reason,
            },
            "customer": user_response,
            "address": address_response,
            "special_offer": special_offer_response,
            "order_detail": order_detail_response
        }

        return response


    def calculate_returned_items(self, return_orders):
        returned_items_map = {}
        total_refunded = 0

        if not return_orders:
            return returned_items_map, total_refunded

        for return_order in return_orders:
            if return_order.deleted_at is not None:
                continue

            if return_order.status not in ["approved", "completed"]:
                continue

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

        return returned_items_map, total_refunded


    async def get_detail_order_customer(self, order_id: str, customer_id: str, session: AsyncSession):
        options = [
            selectinload(Order.order_detail).load_only(
                Order_Detail.id,
                Order_Detail.quantity,
                Order_Detail.price,
                Order_Detail.product_snapshot
            ),
            selectinload(Order.user).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.email,
                User.phone,
            ),
        ]

        condition = [
            Order.id == order_id, Order.deleted_at.is_(None)
        ]
        order = await order_repository.get_order(session=session, where_conditions=condition, options=options)

        if not order:
            OrderException.not_found()

        if str(order.user_id) != str(customer_id):
            OrderException.unauthorized_order()

        condition_status = and_(OrderStatusHistory.order_id == order_id)
        latest_status = await order_repository.get_new_status_order(condition_status, session)
        latest_status_response = None
        if latest_status:
            latest_status_response = {
                "status": latest_status.status,
                "changed_at": str(latest_status.created_at),
            }

        user = order.user
        user_response = None
        if user:
            user_response = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
            }

        address_snapshot = order.address_snapshot
        if not address_snapshot:
            return None

        address_response = None
        if "ward" in address_snapshot and isinstance(address_snapshot["ward"], dict):
            address_response = {
                "line": address_snapshot.get("line"),
                "ward": address_snapshot.get("ward"),
                "province": address_snapshot.get("province"),
                "district": address_snapshot.get("district"),
                "country": address_snapshot.get("country", "Việt Nam"),
            }

        special_offer_response = None
        if order.special_offer_snapshot:
            special_offer_response = {
                "code": order.special_offer_snapshot.get("code"),
                "name": order.special_offer_snapshot.get("name"),
                "discount": order.special_offer_snapshot.get("discount"),
                "type": order.special_offer_snapshot.get("type"),
            }

        order_detail_response = []
        for od in order.order_detail:
            product_snapshot = od.product_snapshot

            product_dict = {
                "name": product_snapshot.get("name"),
                "size": product_snapshot.get("size"),
                "color_name": product_snapshot.get("color_name"),
                "product_image": product_snapshot.get("product_image"),
                "variant_image": product_snapshot.get("variant_image"),
                "price_after_discount": product_snapshot.get("price_after_discount"),
                "price_before_discount": product_snapshot.get("price_before_discount"),
                "quantity": od.quantity
            }

            order_detail_response.append(product_dict)

        order_info = {
            "code": order.code,
            "note": order.note,
            "status": order.status,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "created_at": str(order.created_at),
            "estimated_delivery_date": str(order.estimated_delivery_date) if order.estimated_delivery_date else None,
            "last_status_change": latest_status_response,
            "sub_total": order.sub_total,
            "discount": order.discount,
            "discount_percent": order.discount_percent if hasattr(order, 'discount_percent') else 0,
            "total_price": order.total_price,
        }

        if order.payment_method == "vnpay":
            if order.payment_status == "success":
                order_info["paid_amount"] = order.total_price
            elif order.payment_status == "pending":
                order_info["paid_amount"] = 0

        return {
            "order": order_info,
            "customer": user_response,
            "address": address_response,
            "special_offer": special_offer_response,
            "order_detail": order_detail_response
        }
