from sqlalchemy.orm import selectinload
from src.celery_app import celery_app
from src.crud.return_order.repositories import ReturnOrderRepository
from src.crud.return_order.services.complete_return_order import CompleteReturnOrderService
from src.database.main import async_session_maker
import asyncio
import logging
from src.database.models import ReturnOrder
from src.schemas.return_order import ReturnOrderStatus

logger = logging.getLogger(__name__)

return_order_repository = ReturnOrderRepository()
complete_return_order_service = CompleteReturnOrderService()


@celery_app.task(name='auto_complete_return_order')
def auto_complete_return_order_task(return_order_id: str):
    asyncio.run(process_auto_complete_return_order(return_order_id))

async def process_auto_complete_return_order(return_order_id: str):
    async with async_session_maker() as session:
        try:
            conditions = [
                ReturnOrder.id == return_order_id,
                ReturnOrder.status == ReturnOrderStatus.APPROVED,
                ReturnOrder.deleted_at.is_(None)
            ]
            options = [
                selectinload(ReturnOrder.return_items),
                selectinload(ReturnOrder.order),
                selectinload(ReturnOrder.user)
            ]

            return_order = await return_order_repository.get_return_order(
                where_conditions=conditions,
                session=session,
                options=options,
                for_update=True
            )

            if not return_order:
                logger.info(f"Return order {return_order_id} not found or not in approved status")
                return

            logger.info(f"Auto-completing return order {return_order_id}")

            message, result = await complete_return_order_service.complete_return(
                return_order_id=return_order_id,
                restore_stock=True,
                request=None,
                session=session
            )

            await session.commit()
            logger.info(f"Auto-completed return order {return_order_id}: {message}")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error auto-completing return order {return_order_id}: {str(e)}")
            raise