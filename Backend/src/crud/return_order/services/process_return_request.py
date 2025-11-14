from sqlalchemy.orm import selectinload
from datetime import datetime
from starlette.requests import Request

from src.celery_tasks.auto_complete_return import auto_complete_return_order_task
from src.crud.notification.services.services import NotificationService
from src.crud.order.repositories import OrderRepository
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.payment_refund.services import PaymentRefundService
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.order_detail.repositories import OrderDetailRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.database.models import ReturnOrder
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from src.errors.return_order import ReturnOrderException
from src.schemas.return_order import ReturnOrderActionType, ReturnOrderStatusType
import logging

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
notification_service = NotificationService()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()

logger = logging.getLogger(__name__)

class ProcessReturnOrderService:
    async def process_return_request(self, return_order_id: str, action: str, admin_data: dict,
                                     request: Request, session: AsyncSession):
        conditions = [ReturnOrder.id == return_order_id]
        joins = [
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.return_items),
            selectinload(ReturnOrder.user)
        ]

        return_order = await return_order_repository.get_return_order(conditions, session, joins)
        if not return_order:
            ReturnOrderException.return_doesnt_exist()

        message = ""
        # try:
        #
        #
        # except Exception as e:
        #     await session.rollback()
        #     ReturnOrderException.error_return_order()

        if action == ReturnOrderActionType.APPROVE:
            await self.approve_return_request(return_order, admin_data, session)
            message = f"Đã chấp nhận yêu cầu hoàn trả đơn hàng #{return_order.order.code}"

            auto_complete_return_order_task.apply_async(
                args=[str(return_order_id)],
                countdown=259200  # 3 days = 3 * 24 * 60 * 60
            )
            logger.info(f"Scheduled auto-complete for return order {return_order_id} in 3 days")

        elif action == ReturnOrderActionType.REJECT:
            reject_reason = admin_data.get('reject_reason')
            if not reject_reason:
                ReturnOrderException.reason_must_be_provided()

            await self.reject_return_request(return_order, reject_reason, session)
            message = f"Đã từ chối yêu cầu hoàn trả đơn hàng #{return_order.order.code}"

        else:
            ReturnOrderException.invalid_action()

        await session.commit()

        return message, {
            "return_order_id": return_order_id,
            "action": action
        }

    async def approve_return_request(self, return_order: ReturnOrder, admin_data: dict, session: AsyncSession):
        await return_order_repository.update_return_order(
            and_(ReturnOrder.id == return_order.id),
            {
                "status": ReturnOrderStatusType.APPROVED,
                "approved_at": datetime.now(),
                "note": admin_data.get('admin_note')
            },
            session
        )

        await notification_service.create_return_approved_notification(
            session=session,
            return_order_id=str(return_order.id),
            customer_id=str(return_order.user_id),
            order_code=return_order.order.code,
            order_id=str(return_order.order_id),
        )

    async def reject_return_request(self, return_order: ReturnOrder, reject_reason: str, session: AsyncSession):
        current_note = return_order.note or ""
        new_note = f"{current_note} | Admin từ chối: {reject_reason}"

        await return_order_repository.update_return_order(
            and_(ReturnOrder.id == return_order.id),
            {
                "status": ReturnOrderStatusType.REJECTED,
                "rejected_at": datetime.now(),
                "note": new_note
            },
            session
        )

        await notification_service.create_return_rejected_notification(
            session=session,
            return_order_id=str(return_order.id),
            customer_id=str(return_order.user_id),
            order_code=return_order.order.code,
            reject_reason=reject_reason,
            order_id=str(return_order.order_id),
        )





