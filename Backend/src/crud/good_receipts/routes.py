from fastapi import APIRouter, status, Depends
from src.crud.good_receipts.services.create_goods_receipt import CreateGoodsReceiptService
from src.crud.good_receipts.services.get_approval_review import ApprovalPreviewService
from src.dependencies import AccessTokenBearer, admin_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.user import UserException
from src.schemas.goods_receipt import CreateGoodsReceiptRequest

good_receipts_admin_router = APIRouter(prefix="/good-receipts")
good_receipts_customer_router = APIRouter(prefix="/good-receipts")
good_receipts_staff_router = APIRouter(prefix="/good-receipts")

approval_preview_service = ApprovalPreviewService()
create_goods_receipt_service = CreateGoodsReceiptService()
access_token_bearer = AccessTokenBearer()


@good_receipts_admin_router.post("/")
async def create_goods_receipt(request: CreateGoodsReceiptRequest,
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    user_id = token_details['user']['id']
        
    goods_receipt = await create_goods_receipt_service.create_goods_receipt(request, user_id, session)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tạo đơn nhập kho thành công",
            "content": goods_receipt
        }
    )


@good_receipts_admin_router.get("/{goods_receipt_id}/approval-preview")
async def get_approval_preview(goods_receipt_id: str,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    preview = await approval_preview_service.get_approval_preview(goods_receipt_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Nội dung chi tiết của phiếu",
            "content": preview
        }
    )


@good_receipts_admin_router.post("/{goods_receipt_id}/approve")
async def approve_goods_receipt(goods_receipt_id: str,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    user_id = token_details['user']['id']

    goods_receipt = await create_goods_receipt_service.create_goods_receipt(request, user_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tạo đơn nhập kho thành công",
            "content": goods_receipt
        }
    )














