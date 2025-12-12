from sqlalchemy.orm import selectinload
from datetime import datetime
from src.crud.order.repositories import OrderRepository
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.return_order.services.complete_return_order import CompleteReturnOrderService
from src.database.models import ReturnOrder, Order
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
import logging

order_repository = OrderRepository()
return_order_repository = ReturnOrderRepository()
complete_return_order_service = CompleteReturnOrderService()

logger = logging.getLogger(__name__)

class AutoCompleteReturnService:
    async def auto_complete_return(self, return_order_id: str, session: AsyncSession):
        try:
            conditions = [
                ReturnOrder.id == return_order_id,
                ReturnOrder.status == "approved"
            ]
            joins = [
                selectinload(ReturnOrder.return_items),
                selectinload(ReturnOrder.order),
                selectinload(ReturnOrder.user)
            ]

            return_order = await return_order_repository.get_return_order(conditions, session, joins)

            if not return_order:
                logger.info(f"Return order {return_order_id} not found or not in 'approved' status")

            if return_order.order.cancellation_status in ['REQUESTED', 'APPROVED']:
                logger.info(f"Return order {return_order_id} - Order has cancellation status")

            await return_order_repository.update_return_order(
                and_(ReturnOrder.id == return_order_id),
                {
                    "status": "completed",
                    "refunded_at": datetime.now()
                },
                session
            )

            await complete_return_order_service.restore_product_stock(
                return_order.return_items,
                session
            )

            refund_result = None
            if return_order.order.payment_method == "vnpay":
                try:
                    refund_result = await complete_return_order_service.process_refund_single_attempt(
                        return_order,
                        session,
                        ipaddr=None
                    )
                except Exception as e:
                    logger.warning(f"Refund failed for return order {return_order_id}: {str(e)}")

            await order_repository.update_order_some_field(
                and_(Order.id == return_order.order_id),
                {"status": "returned"},
                session
            )

            await notification_service.create_return_completed_notification(
                session=session,
                return_order_id=return_order_id,
                customer_id=str(return_order.user_id),
                order_code=return_order.order.code,
                stock_restored=True,
                order_id=str(return_order.order_id),
            )

            await session.commit()

            logger.info(f"Auto-completed return order {return_order_id}")

            return {
                'return_order_id': return_order_id,
                'stock_restored': True,
                'refund_result': refund_result,
            }

        except Exception as e:
            logger.error(f"Error auto-completing return order {return_order_id}: {str(e)}")
            await session.rollback()
            raise



