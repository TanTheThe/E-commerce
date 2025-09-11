from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.crud.payment_refund.services import PaymentRefundService
from src.crud.vnpay.services import VNPayService
from src.crud.vnpay.utils import get_client_ip
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from datetime import datetime

vnpay_admin_router = APIRouter(prefix="/vnpay")
vnpay_customer_router = APIRouter(prefix="/vnpay")
vnpay_common_router = APIRouter(prefix="/vnpay")

payment_refund_service = PaymentRefundService()
access_token_bearer = AccessTokenBearer()

templates = Jinja2Templates(directory="src/templates")


@vnpay_customer_router.get("/refund", response_class=HTMLResponse)
async def refund_form(request: Request):
    return templates.TemplateResponse("payment/refund.html", {
        "request": request,
        "title": "Hoàn tiền giao dịch",
        "current_year": datetime.now().year
    })


@vnpay_customer_router.post("/refund", response_class=HTMLResponse)
async def refund(
        request: Request,
        TransactionType: str = Form(...),
        order_id: str = Form(...),
        amount: str = Form(...),
        order_desc: str = Form(...),
        trans_date: str = Form(...),
        session: AsyncSession = Depends(get_session)
):
    response_json = await payment_refund_service.refund_transaction(
        TransactionType, order_id, amount, order_desc, trans_date, get_client_ip(request)
    )
    return templates.TemplateResponse("payment/refund.html", {
        "request": request,
        "title": "Kết quả hoàn tiền giao dịch",
        "response_json": response_json,
        "current_year": datetime.now().year
    })