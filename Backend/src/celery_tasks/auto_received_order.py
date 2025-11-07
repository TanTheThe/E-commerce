from src.celery_app import celery_app

from src.crud.order.services.auto_confirm_received import AutoConfirmReceivedService
from src.database.main import async_session_maker
import asyncio

auto_confirm_received_service = AutoConfirmReceivedService()

@celery_app.task(name='auto_confirm_order_received')
def auto_confirm_order_received_task(order_id: str):
    asyncio.run(process_auto_confirm(order_id))

async def process_auto_confirm(order_id: str):
    async with async_session_maker() as session:
        try:
            await auto_confirm_received_service.auto_confirm_received(order_id, session)
        except Exception as e:
            print(f"Error auto-confirming order {order_id}: {str(e)}")