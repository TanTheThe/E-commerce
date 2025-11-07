from fastapi import APIRouter, status, Depends
from src.crud.cash.services.create_manual_refund_transaction import ManualRefundCashService
from src.crud.cash.services.update_shipping_status import WebhookShippingService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.schemas.cash import CreateManualRefundRequest
from src.schemas.webhook import ShippingWebhookRequest

webhook_admin_router = APIRouter(prefix="/cash")
webhook_customer_router = APIRouter(prefix="/cash")
webhook_staff_router = APIRouter(prefix="/cash")

webhook_shipping_service = WebhookShippingService()
manual_refund_cash_service = ManualRefundCashService()
access_token_bearer = AccessTokenBearer()

@webhook_admin_router.post("/webhook-shipping", status_code=status.HTTP_200_OK)
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


@webhook_admin_router.post("/manual-refund-transaction", status_code=status.HTTP_200_OK)
async def create_manual_refund_transaction(request_data: CreateManualRefundRequest,
                                  token_details: dict = Depends(access_token_bearer),
                                  session: AsyncSession = Depends(get_session)):

    cash_transaction = await manual_refund_cash_service.create_manual_refund_transaction(
        return_order_id=request_data.return_order_id,
        amount=request_data.amount,
        payment_method=request_data.payment_method,
        notes=request_data.notes,
        transaction_date=request_data.transaction_date,
        session=session
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Đã tạo giao dịch hoàn tiền thủ công",
            "content": cash_transaction
        }
    )














