from venv import logger
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from src.config import Config
from src.crud.vnpay.services.create_payment_url import CreatePaymentURLService
from src.crud.vnpay.services.get_payment_by_order_code import GetPaymentByOrderCodeService
from src.crud.vnpay.services.handle_ipn.handle_ipn import HandleIPNService
from src.crud.vnpay.services.handle_return import HandleReturnService
from src.crud.vnpay.utils import get_client_ip
from src.dependencies import AccessTokenBearer
from src.schemas.vnpay import PaymentRequest
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from src.dependencies import customer_role_middleware
import random
import urllib.parse
import json
import base64

vnpay_admin_router = APIRouter(prefix="/vnpay")
vnpay_customer_router = APIRouter(prefix="/vnpay")
vnpay_staff_router = APIRouter(prefix="/vnpay")

create_payment_url_service = CreatePaymentURLService()
handle_ipn_service = HandleIPNService()
handle_return_service = HandleReturnService()
get_payment_by_order_code_service = GetPaymentByOrderCodeService()
access_token_bearer = AccessTokenBearer()

n = random.randint(10 ** 11, 10 ** 12 - 1)
n_str = str(n).zfill(12)


@vnpay_customer_router.post("/payment", dependencies=[Depends(customer_role_middleware)])
async def create_payment(request: Request, payment_data: PaymentRequest,
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    try:
        payment_url = await create_payment_url_service.create_payment_url(
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
        result = await handle_ipn_service.handle_ipn(dict(request.query_params), session)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"VNPay IPN error: {str(e)}", exc_info=True)
        return JSONResponse({"RspCode": "99", "Message": "Internal error"})


@vnpay_customer_router.get("/payment_return", response_class=HTMLResponse)
async def payment_return(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        payment_result = await handle_return_service.handle_return(dict(request.query_params), session)

        payment_data = json.dumps(payment_result)
        encoded_data = base64.urlsafe_b64encode(payment_data.encode()).decode()

        frontend_url = f"http://{Config.CUSTOMER_DOMAIN_CLIENT}/payment-return?data={encoded_data}"
        return RedirectResponse(url=frontend_url, status_code=302)

    except ValueError as e:
        error_url = f"http://{Config.CUSTOMER_DOMAIN_CLIENT}/payment-return?error={urllib.parse.quote(str(e))}"
        return RedirectResponse(url=error_url, status_code=302)

    except Exception as e:
        logger.error(f"Payment return error: {str(e)}", exc_info=True)
        error_url = f"http://{Config.CUSTOMER_DOMAIN_CLIENT}/payment-return?error={urllib.parse.quote('Lỗi xử lý kết quả thanh toán')}"
        return RedirectResponse(url=error_url, status_code=302)


@vnpay_customer_router.get("/payment_result/{order_code}")
async def get_payment_result(order_code: str, session: AsyncSession = Depends(get_session)):
    try:
        payment_result = await get_payment_by_order_code_service.get_payment_result_by_order_code(order_code, session)

        if not payment_result:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "Không tìm thấy thông tin thanh toán",
                }
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thông tin thanh toán",
                "content": {
                    "payment": payment_result
                }
            }
        )

    except Exception as e:
        logger.error(f"Error fetching payment result: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Lỗi hệ thống",
            }
        )
