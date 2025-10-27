from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, status, Depends
from src.crud.good_receipts.services.approve_goods_receipt import ApproveGoodsReceiptService
from src.crud.good_receipts.services.create_goods_receipt import CreateGoodsReceiptService
from src.crud.good_receipts.services.delete_goods_receipt import DeleteGoodsReceiptService
from src.crud.good_receipts.services.get_all_goods_receipt import GetAllGoodsReceiptService
from src.crud.good_receipts.services.get_approval_review import ApprovalPreviewService
from src.crud.good_receipts.services.get_detail_goods_receipt import GetDetailGoodsReceiptService
from src.crud.good_receipts.services.get_gr_for_create import GetGRForCreateService
from src.crud.good_receipts.services.update_goods_receipt import UpdateGoodsReceiptService
from src.dependencies import AccessTokenBearer, admin_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.user import UserException
from src.schemas.goods_receipt import CreateGoodsReceiptRequest
from src.schemas.goods_receipt import SortBy, UpdateGoodsReceiptRequest

goods_receipt_admin_router = APIRouter(prefix="/goods-receipt")
goods_receipt_customer_router = APIRouter(prefix="/goods-receipt")
goods_receipt_staff_router = APIRouter(prefix="/goods-receipt")

approval_preview_service = ApprovalPreviewService()
create_goods_receipt_service = CreateGoodsReceiptService()
approve_goods_receipt_service = ApproveGoodsReceiptService()
get_all_goods_receipts_service = GetAllGoodsReceiptService()
get_detail_goods_receipt_service = GetDetailGoodsReceiptService()
update_goods_receipt_service = UpdateGoodsReceiptService()
delete_goods_receipt_service = DeleteGoodsReceiptService()
get_gr_for_create_service = GetGRForCreateService()
access_token_bearer = AccessTokenBearer()


@goods_receipt_admin_router.post("/")
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


@goods_receipt_admin_router.get("/{goods_receipt_id}/approval-preview")
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


@goods_receipt_admin_router.get("/")
async def get_all_goods_receipts(warehouse_id: str,
                                 status_gr: Optional[str] = Query(None, description="Trạng thái phiếu"),
                                 purchase_order_id: Optional[str] = Query(None, description="ID đơn hàng"),
                                 supplier_id: Optional[str] = Query(None, description="ID nhà cung cấp"),
                                 from_date: Optional[datetime] = Query(None, description="Từ ngày"),
                                 to_date: Optional[datetime] = Query(None, description="Đến ngày"),
                                 search: Optional[str] = Query(None, description="Tìm kiếm theo receipt_number"),
                                 sort_by: Optional[SortBy] = None,
                                 skip: int = 0, limit: int = 10,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    goods_receipt = await get_all_goods_receipts_service.get_all_goods_receipts(
        session=session,
        warehouse_id=warehouse_id,
        status_gr=status_gr,
        purchase_order_id=purchase_order_id,
        supplier_id=supplier_id,
        from_date=from_date,
        to_date=to_date,
        search=search,
        sort_by=sort_by,
        skip=skip,
        limit=limit
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin toàn bộ các phiếu nhập hàng tại kho",
            "content": goods_receipt
        }
    )


@goods_receipt_admin_router.get("/{goods_receipt_id}")
async def get_goods_receipt_detail(goods_receipt_id: str,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    goods_receipt = await get_detail_goods_receipt_service.get_goods_receipt(
        session=session,
        gr_id=goods_receipt_id
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết phiếu nhập hàng",
            "content": goods_receipt
        }
    )
    
    
@goods_receipt_admin_router.get("/create-info/{parent_goods_receipt_id}")
async def get_goods_receipt_for_create(parent_goods_receipt_id: str,
                                       token_details: dict = Depends(access_token_bearer),
                                       session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    goods_receipt = await get_gr_for_create_service.get_goods_receipt_for_create(
        session=session,
        parent_gr_id=parent_goods_receipt_id
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin để tạo phiếu nhập hàng con",
            "content": goods_receipt
        }
    )


@goods_receipt_admin_router.post("/{goods_receipt_id}/approve", dependencies=[Depends(admin_role_middleware)])
async def approve_goods_receipt(goods_receipt_id: str,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']

    goods_receipt = await approve_goods_receipt_service.approve_goods_receipt(session, goods_receipt_id, user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": goods_receipt["message"],
            "content": goods_receipt["data"]
        }
    )
    
    
@goods_receipt_admin_router.put("/{goods_receipt_id}")
async def update_goods_receipt(goods_receipt_id: str, request: UpdateGoodsReceiptRequest,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()
        
    update_data = request.model_dump(exclude_none=True)
    
    goods_receipt = await update_goods_receipt_service.update_goods_receipt(session, goods_receipt_id, update_data)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật phiếu nhập hàng thành công",
            "content": goods_receipt
        }
    )
    

@goods_receipt_admin_router.delete("/{goods_receipt_id}")
async def delete_goods_receipt(goods_receipt_id: str,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()
        
    await delete_goods_receipt_service.delete_goods_receipt(session, goods_receipt_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa phiếu nhập hàng thành công"
        }
    )