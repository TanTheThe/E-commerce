from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime

from src.crud.notification.services.services import NotificationService
from src.crud.order.repositories import OrderRepository
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import ReturnOrder, Order, Order_Detail, ReturnItem
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.order import OrderException
from src.errors.return_order import ReturnOrderException
from src.schemas.return_order import ReturnOrderType

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
notification_service = NotificationService()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()


class CreateReturnOrderService:
    async def validate_return_eligibility(self, order_id: str, user_id: str, session: AsyncSession):
        conditions = and_(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.deleted_at.is_(None)
        )

        joins = [
            selectinload(Order.order_detail),
            selectinload(Order.payments)
        ]

        order = await order_repository.get_order(conditions, session, joins)

        if not order:
            OrderException.not_found()

        if order.status not in ("delivered", "received"):
            OrderException.only_delivered_can_return()

        if order.payment_status != "success":
            OrderException.only_payment_success_can_return()

        if not order.delivered_at:
            OrderException.not_found_delivered_at()

        days_since_delivery = (datetime.now() - order.delivered_at).days
        if days_since_delivery > 7:
            OrderException.overdue_return_order()

        condition = [ReturnOrder.order_id == order_id]
        existing_return = await return_order_repository.get_return_order(condition, session)

        if existing_return:
            ReturnOrderException.already_exists()

        return True, "Đơn hàng hợp lệ để hoàn trả", order

    async def validate_return_items(self, return_items: List[dict], order_details: List[Order_Detail]):
        if not return_items:
            ReturnOrderException.at_least_one_product_to_return()

        order_detail_dict = {str(detail.id): detail for detail in order_details}

        for item in return_items:
            order_detail_id = item.get('order_detail_id')
            return_quantity = item.get('quantity', 0)
            images = item.get('images', [])

            if not order_detail_id or return_quantity <= 0:
                ReturnOrderException.refund_amount_greater_than_0()

            if not images or len(images) < 5:
                ReturnOrderException.at_least_5_products_image()

            if order_detail_id not in order_detail_dict:
                OrderException.product_not_include_order()

            original_quantity = order_detail_dict[order_detail_id].quantity
            if return_quantity > original_quantity:
                ReturnOrderException.refund_amount_exceed_purchase()

        return True, "Danh sách sản phẩm hợp lệ"

    async def calculate_refund_amount(self, return_items: List[dict], order: Order, session: AsyncSession) -> int:
        total_refund = 0
        discount_percent = order.discount_percent or 0

        for item in return_items:
            condition = and_(Order_Detail.id == item['order_detail_id'], Order_Detail.deleted_at.is_(None))
            order_detail = await order_detail_repository.get_order_detail(condition, session)

            if order_detail:
                item_refund = order_detail.price * item['quantity']
                item_refund = int(item_refund * (1 - discount_percent / 100))
                total_refund += item_refund

        return total_refund

    async def create_return_request(self, order_id: str, user_id: str, request_data: dict, session: AsyncSession):
        is_valid, message, order = await self.validate_return_eligibility(order_id, user_id, session)
        if not is_valid:
            ReturnOrderException.order_not_valid_for_return()

        return_items = request_data.get('return_items', [])
        items_valid, items_message = await self.validate_return_items(return_items, order.order_detail)
        if not items_valid:
            ReturnOrderException.order_not_valid_for_return()

        # try:
        #
        #
        # except Exception as e:
        #     await session.rollback()
        #     ReturnOrderException.error_return_order()

        refund_amount = await self.calculate_refund_amount(return_items, order, session)

        return_order = ReturnOrder(
            order_id=order_id,
            user_id=user_id,
            reason=request_data.get('reason', ''),
            status=ReturnOrderType.PENDING,
            note=request_data.get('note'),
            created_at=datetime.now()
        )

        session.add(return_order)
        await session.flush()

        for item_data in return_items:
            condition = and_(Order_Detail.id == item_data['order_detail_id'], Order_Detail.deleted_at.is_(None))
            order_detail = await order_detail_repository.get_order_detail(condition, session)

            item_refund = order_detail.price * item_data['quantity']
            item_refund = int(item_refund * (1 - (order.discount_percent or 0) / 100))

            return_item = ReturnItem(
                return_order_id=return_order.id,
                order_detail_id=item_data['order_detail_id'],
                quantity=item_data['quantity'],
                refund_amount=item_refund,
                images=item_data.get('images', []),
                created_at=datetime.now()
            )
            session.add(return_item)

        await notification_service.create_return_request_notification(
            session=session,
            return_order_id=str(return_order.id),
            customer_id=user_id,
            order_code=order.code,
            order_id=str(order.id),
        )

        await session.commit()

        message = f"Yêu cầu hoàn trả đơn hàng #{order.code} đã được gửi thành công"
        return message, {
            "return_order_id": str(return_order.id),
            "total_refund": refund_amount
        }




