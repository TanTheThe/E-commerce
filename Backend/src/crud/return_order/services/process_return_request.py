from typing import Optional
from sqlalchemy.orm import selectinload
from datetime import datetime
from src.celery_tasks.auto_complete_return import auto_complete_return_order_task
from src.crud.notification.services.create_notification import CreateNotificationService
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
from src.schemas.return_order import ReturnOrderActionType, ReturnOrderStatus
import logging

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
order_detail_repository = OrderDetailRepository()
vnpay_repository = VNPayRepository()
payment_refund_service = PaymentRefundService()
payment_refund_repository = PaymentRefundRepository()
product_variant_repository = ProductVariantRepository()

logger = logging.getLogger(__name__)

create_notification_service = CreateNotificationService()

class ProcessReturnOrderService:
    async def process_return_request(self, return_order_id: str, action: ReturnOrderActionType, admin_note: Optional[str],
                                     reject_reason: Optional[str], attempt_count: int, admin_id: str, admin_email: str,
                                     session: AsyncSession):
        conditions = [ReturnOrder.id == return_order_id, ReturnOrder.deleted_at.is_(None)]
        options = [
            selectinload(ReturnOrder.order),
            selectinload(ReturnOrder.return_items),
            selectinload(ReturnOrder.user)
        ]

        return_order = await return_order_repository.get_return_order(session=session, where_conditions=conditions,
                                                                      options=options, for_update=True)
        if not return_order:
            ReturnOrderException.return_doesnt_exist()

        current_status = return_order.status

        if current_status in [ReturnOrderStatus.APPROVED, ReturnOrderStatus.REJECTED,
                              ReturnOrderStatus.REFUNDED, ReturnOrderStatus.COMPLETED]:
            ReturnOrderException.action_cant_be_performed(action, current_status)

        if current_status != ReturnOrderStatus.PENDING:
            ReturnOrderException.invalid_status_to_return(action)

        message = ""
        try:
            if action == ReturnOrderActionType.APPROVE:
                message = await self.handle_approve(
                    return_order, admin_note, attempt_count, admin_id, session
                )

            elif action == ReturnOrderActionType.REJECT:
                message = await self.handle_reject(
                    return_order, reject_reason, admin_id, session
                )

            else:
                ReturnOrderException.invalid_action()

            await session.commit()

            return message, {
                "return_order_id": return_order_id,
                "action": action.value,
                "processed_at": datetime.now().isoformat()
            }
        except Exception as e:
            await session.rollback()
            logger.error("Error process return request: ", e)
            ReturnOrderException.error_return_order()


    async def handle_approve(self, return_order: ReturnOrder, admin_note: Optional[str], attempt_count: int,
                             admin_id: str, session: AsyncSession) -> str:
        now = datetime.now()

        update_data = {
            "status": ReturnOrderStatus.APPROVED,
            "approved_at": now,
            "approved_by": admin_id,
            "updated_at": now
        }

        if admin_note:
            current_note = return_order.note or ""
            update_data["note"] = f"{current_note}\nAdmin note: {admin_note}".strip()

        await return_order_repository.update_return_order(
            and_(ReturnOrder.id == return_order.id),
            update_data,
            session
        )

        await create_notification_service.create_return_approved_notification(
            session=session,
            return_order_id=str(return_order.id),
            customer_id=str(return_order.user_id),
            order_code=return_order.order.code,
            order_id=str(return_order.order_id),
        )

        try:
            auto_complete_return_order_task.apply_async(
                args=[str(return_order.id)],
                countdown=259200  # 3 days
            )
            logger.info(f"Scheduled auto-complete for return order {return_order.id} in 3 days")
        except Exception as e:
            logger.error(f"Failed to schedule auto-complete task: {str(e)}")

        return f"Đã chấp nhận yêu cầu hoàn trả đơn hàng #{return_order.order.code}"


    async def handle_reject(self, return_order: ReturnOrder, reject_reason: str, admin_id: str, session: AsyncSession):
        now = datetime.now()

        current_note = return_order.note or ""
        new_note = f"{current_note}\nAdmin từ chối ({now.strftime('%Y-%m-%d %H:%M')}): {reject_reason}".strip()

        await return_order_repository.update_return_order(
            and_(ReturnOrder.id == return_order.id),
            {
                "status": ReturnOrderStatus.REJECTED,
                "rejected_at": now,
                "rejected_by": admin_id,
                "note": new_note,
                "updated_at": now
            },
            session
        )

        await create_notification_service.create_return_rejected_notification(
            session=session,
            return_order_id=str(return_order.id),
            customer_id=str(return_order.user_id),
            order_code=return_order.order.code,
            reject_reason=reject_reason,
            order_id=str(return_order.order_id),
        )

        return f"Đã từ chối yêu cầu hoàn trả đơn hàng #{return_order.order.code}"






