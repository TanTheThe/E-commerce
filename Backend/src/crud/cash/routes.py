from fastapi import APIRouter, status, Depends
from src.crud.webhook.services.update_shipping_status import WebhookShippingService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.schemas.webhook import ShippingWebhookRequest

webhook_admin_router = APIRouter(prefix="/webhook")
webhook_customer_router = APIRouter(prefix="/webhook")
webhook_staff_router = APIRouter(prefix="/webhook")

webhook_shipping_service = WebhookShippingService()
access_token_bearer = AccessTokenBearer()

@webhook_admin_router.post("/shipping", status_code=status.HTTP_200_OK)
async def handle_shipping_webhook(webhook_data: ShippingWebhookRequest,
                           token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)):
    result = await webhook_shipping_service.update_shipping_status(webhook_data, session)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Cập nhật trạng thái đơn hàng thành công",
            "content": result
        }
    )















