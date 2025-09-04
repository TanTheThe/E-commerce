from fastapi import APIRouter, status, Depends
from src.crud.vnpay.services import VNPayService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import customer_role_middleware

vnpay_admin_router = APIRouter(prefix="/vnpay")
vnpay_customer_router = APIRouter(prefix="/vnpay")
vnpay_common_router = APIRouter(prefix="/vnpay")

vnpay_service = VNPayService()
access_token_bearer = AccessTokenBearer()

@vnpay_customer_router.get("/", dependencies=[Depends(customer_role_middleware)])
async def create_new_address(token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    pass
