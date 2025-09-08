from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from src.crud.vnpay.services import VNPayService
from src.crud.vnpay.utils import get_client_ip
from src.dependencies import AccessTokenBearer
from src.schemas.vnpay import PaymentRequest
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from src.dependencies import customer_role_middleware
from datetime import datetime
import random

vnpay_admin_router = APIRouter(prefix="/vnpay")
vnpay_customer_router = APIRouter(prefix="/vnpay")
vnpay_common_router = APIRouter(prefix="/vnpay")

vnpay_service = VNPayService()
access_token_bearer = AccessTokenBearer()

templates = Jinja2Templates(directory="src/templates")

n = random.randint(10**11, 10**12 - 1)
n_str = str(n).zfill(12)

@vnpay_customer_router.post("/payment", dependencies=[Depends(customer_role_middleware)])
async def create_payment(
    request: Request,
    payment_data: PaymentRequest,
    token_details: dict = Depends(access_token_bearer),
    session: AsyncSession = Depends(get_session)
):
    if not payment_data.order_code or not payment_data.amount:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Không tìm thấy thông tin thanh toán",
                "content": None
            }
        )
        
    if payment_data.amount < 5000 or payment_data.amount > 1000000000: 
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Số tiền thanh toán phải nằm trong khoảng 5,000 and 1,000,000,000 VND",
                "content": None
            }
        )
    
    try:
        payment_url = await vnpay_service.create_payment_url(
            request=request,
            order_type=payment_data.order_type,
            order_code=payment_data.order_code,
            amount=payment_data.amount,
            order_desc=payment_data.order_desc,
            bank_code=payment_data.bank_code,
            language=payment_data.language,
            ipaddr=get_client_ip(request),
            session=session
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Đang chuyển hướng trang",
                "content": {
                    "payment_url": payment_url,
                    "order_code": payment_data.order_code,
                    "amount": payment_data.amount
                }
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Lỗi tạo đường dẫn thanh toán",
                "content": None
            }
        )
        


@vnpay_customer_router.get("/payment_ipn")
async def payment_ipn(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        result = await vnpay_service.handle_ipn(dict(request.query_params), session)
        return result
    except Exception as e:
        return JSONResponse({"RspCode": "99", "Message": "Internal error"})


@vnpay_customer_router.get("/payment_return", dependencies=[Depends(customer_role_middleware)])
async def payment_return(request: Request,
                         token_details: dict = Depends(access_token_bearer), 
                         session: AsyncSession = Depends(get_session)):
    try:
        payment = await vnpay_service.handle_return(dict(request.query_params), request, session)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin thanh toán",
                "content": {
                    "payment": payment
                }
            }
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": str(e),
                "content": None
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Lỗi xử lý kết quả thanh toán",
                "content": None
            }
        )


@vnpay_customer_router.get("/query", response_class=HTMLResponse)
async def query_form(request: Request):
    return templates.TemplateResponse("payment/query.html", {
        "request": request, 
        "title": "Kiểm tra kết quả giao dịch",
        "current_year": datetime.now().year
    })


@vnpay_customer_router.post("/query", response_class=HTMLResponse)
async def query(
    request: Request,
    order_id: str = Form(...),
    trans_date: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    # dependencies=[Depends(customer_role_middleware)]
    # token_details: dict = Depends(access_token_bearer),
    response_json = await vnpay_service.query_transaction(order_id, trans_date, get_client_ip(request))
    return templates.TemplateResponse("payment/query.html", {
        "request": request,
        "title": "Kiểm tra kết quả giao dịch",
        "response_json": response_json,
        "current_year": datetime.now().year
    })


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
    # dependencies=[Depends(customer_role_middleware)]
    # token_details: dict = Depends(access_token_bearer),
    response_json = await vnpay_service.refund_transaction(
        TransactionType, order_id, amount, order_desc, trans_date, get_client_ip(request)
    )
    return templates.TemplateResponse("payment/refund.html", {
        "request": request,
        "title": "Kết quả hoàn tiền giao dịch",
        "response_json": response_json,
        "current_year": datetime.now().year
    })

