from datetime import datetime
from sqlalchemy.orm import selectinload
from src.crud.notification.services import NotificationService
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import Order, Order_Detail, OrderStatusHistory
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
from src.schemas.order import CancellationStatusType

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


class ConfirmOrderReceivedService:
    async def confirm_order_received_service(self, order_id: str, session: AsyncSession):
        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        joins = [
            selectinload(Order.order_detail).load_only(Order_Detail.product_id),
        ]

        order_to_update = await order_repository.get_order(condition, session, joins)
        if order_to_update is None:
            OrderException.not_found()

        if order_to_update.cancellation_status == CancellationStatusType.REQUESTED:
            OrderException.cant_update_cancel_order()
        if order_to_update.cancellation_status == CancellationStatusType.APPROVED:
            OrderException.cant_reverse_cancel_order()

        if order_to_update.status != "delivered":
            OrderException.current_status_cant_pick_up(order_to_update.status)

        if order_to_update.status == "received":
            OrderException.already_received()

        update_data = {
            "status": "received",
            "received_at": datetime.now()
        }

        order_after_update = await order_repository.update_order(order_to_update, update_data, session)

        history_entry = OrderStatusHistory(
            order_id=order_id,
            status=order_after_update.status,
            created_at=datetime.now(),
        )
        session.add(history_entry)
        await session.commit()

        return order_after_update

