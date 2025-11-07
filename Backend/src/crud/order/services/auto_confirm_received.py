from datetime import datetime
from sqlalchemy.orm import selectinload
from src.crud.notification.services import NotificationService
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import Special_Offer, User, Address, Order_Detail, Product_Variant, Product, Color, Order
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
from sqlalchemy import update
from src.errors.address import AddressException
from src.errors.order import OrderException
from src.errors.product import ProductException
from src.errors.special_offer import SpecialOfferException
from src.schemas.order import OrderCreateModel, PaymentStatusOrderType, CancellationStatusType
import time
import uuid
from src.errors.authentication import AuthException

order_repository = OrderRepository()

class AutoConfirmReceivedService:
    async def auto_confirm_received(self, order_id: str, session: AsyncSession):
        condition = and_(Order.id == order_id, Order.deleted_at.is_(None))
        options = [selectinload(Order.order_detail).load_only(Order_Detail.product_id)]

        order = await order_repository.get_order(condition, session, options)

        if not order:
            print(f"Order {order_id} not found")
            return None

        if order.status != "delivered":
            print(f"Order {order_id} is no longer in 'delivered' status. Current: {order.status}")
            return None

        if order.cancellation_status in [CancellationStatusType.REQUESTED, CancellationStatusType.APPROVED]:
            print(f"Order {order_id} has cancellation status: {order.cancellation_status}")
            return None

        update_data = {
            "status": "received",
            "received_at": datetime.now(),
        }

        await order_repository.update_order_some_field(condition, update_data, session)

        history_dict = {
            "order_id": order_id,
            "status": "received",
            "created_at": datetime.now(),
        }

        history_entry = await order_repository.create_order_status_history(history_dict, session)

        await session.commit()

        print(f"Order {order_id} auto-confirmed as received")

        return {
            "order_id": order_id,
            "status": "received",
            "received_at": datetime.now(),
        }






