from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, status, Depends
from src.crud.purchase_return.services.approve_purchase_return import PurchaseReturnApprovalService
from src.crud.purchase_return.services.complete_purchase_return import CompletePurchaseReturnService
from src.crud.purchase_return.services.create_purchase_return import CreatePurchaseReturnService
from src.crud.purchase_return.services.get_purchase_returns import GetPurchaseReturnsService
from src.crud.purchase_return.services.send_purchase_return import SendPurchaseReturnService
from src.dependencies import AccessTokenBearer, admin_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.user import UserException
from src.schemas.purchase_order import CreatePurchaseOrderRequest
from src.schemas.purchase_return import CompletePurchaseReturnRequest, CreatePurchaseReturnRequest, SortBy

return_purchase_admin_router = APIRouter(prefix="/return-purchase")
return_purchase_customer_router = APIRouter(prefix="/return-purchase")
return_purchase_staff_router = APIRouter(prefix="/return-purchase")

create_purchase_return_service = CreatePurchaseReturnService()
approve_purchase_return_service = PurchaseReturnApprovalService()
send_purchase_return_service = SendPurchaseReturnService()
complete_purchase_return_service = CompletePurchaseReturnService()
get_purchase_returns_service = GetPurchaseReturnsService()
access_token_bearer = AccessTokenBearer()


@return_purchase_admin_router.post("/")
async def create_purchase_return(request: CreatePurchaseReturnRequest,
                                 token_details: dict = Depends(
                                     access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    user_id = token_details['user']['id']

    return_items = [item.model_dump() for item in request.return_items]

    purchase_return = await create_purchase_return_service.create_return_from_goods_receipt(
        session=session,
        goods_receipt_id=request.goods_receipt_id,
        return_items=return_items,
        return_reason=request.return_reason,
        return_type=request.return_type,
        created_by=user_id,
        notes=request.notes
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tạo đơn hoàn trả hàng thành công",
            "content": purchase_return
        }
    )


@return_purchase_admin_router.post("/{purchase_return_id}/approve", dependencies=[Depends(admin_role_middleware)])
async def approve_purchase_return(purchase_return_id: str,
                                  token_details: dict = Depends(
                                      access_token_bearer),
                                  session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']

    purchase_return = await approve_purchase_return_service.approve_purchase_return(
        session=session,
        purchase_return_id=purchase_return_id,
        approved_by=user_id
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Duyệt phiếu hoàn trả thành công. Có thể gửi hàng về NCC",
            "content": purchase_return
        }
    )


@return_purchase_admin_router.post("/{purchase_return_id}/send-email", dependencies=[Depends(admin_role_middleware)])
async def send_return_email_to_supplier(purchase_return_id: str,
                                        supplier_email: Optional[str] = None,
                                        token_details: dict = Depends(
                                            access_token_bearer),
                                        session: AsyncSession = Depends(get_session)):

    purchase_return = await send_purchase_return_service.send_return_email_to_supplier(
        session=session,
        purchase_return_id=purchase_return_id,
        supplier_email=supplier_email
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Đã gửi email thông báo hoàn trả đến nhà cung cấp",
            "content": purchase_return
        }
    )


@return_purchase_admin_router.post("/{purchase_return_id}/send-email", dependencies=[Depends(admin_role_middleware)])
async def send_return_email_to_supplier(purchase_return_id: str,
                                        supplier_email: Optional[str] = None,
                                        token_details: dict = Depends(
                                            access_token_bearer),
                                        session: AsyncSession = Depends(get_session)):

    purchase_return = await send_purchase_return_service.send_return_email_to_supplier(
        session=session,
        purchase_return_id=purchase_return_id,
        supplier_email=supplier_email
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Đã gửi email thông báo hoàn trả đến nhà cung cấp",
            "content": purchase_return
        }
    )


@return_purchase_admin_router.post("/{purchase_return_id}/complete", dependencies=[Depends(admin_role_middleware)])
async def complete_purchase_return(purchase_return_id: str,
                                   request: CompletePurchaseReturnRequest,
                                   token_details: dict = Depends(
                                       access_token_bearer),
                                   session: AsyncSession = Depends(get_session)):

    purchase_return = await complete_purchase_return_service.complete_purchase_return(session=session,
                                                                                      purchase_return_id=purchase_return_id,
                                                                                      shipped_date=request.shipped_date,
                                                                                      refund_amount=request.refund_amount,
                                                                                      notes=request.notes)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Hoàn tất phiếu hoàn trả thành công",
            "content": purchase_return
        }
    )
    
    
@return_purchase_admin_router.get("/")
async def get_all_purchase_returns(warehouse_id: str,
                                   status_pr: Optional[str] = Query(None, description="Trạng thái phiếu"),
                                   purchase_order_id: Optional[str] = Query(None, description="ID đơn hàng"),
                                   goods_receipt_id: Optional[str] = Query(None, description="ID phiếu nhập kho"),
                                   supplier_id: Optional[str] = Query(None, description="ID nhà cung cấp"),
                                   from_date: Optional[datetime] = Query(None, description="Từ ngày"),
                                   to_date: Optional[datetime] = Query(None, description="Đến ngày"),
                                   search: Optional[str] = Query(None, description="Tìm kiếm theo return_number"),
                                   sort_by: Optional[SortBy] = None,
                                   skip: int = 0, limit: int = 10,
                                   token_details: dict = Depends(access_token_bearer),
                                   session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()
    
    purchase_returns = await get_purchase_returns_service.get_purchase_returns(session=session, status_pr=status_pr,
                                                                              purchase_order_id=purchase_order_id,
                                                                              goods_receipt_id=goods_receipt_id,
                                                                              supplier_id=supplier_id, from_date=from_date,
                                                                              to_date=to_date, search=search, 
                                                                              sort_by=sort_by, skip=skip, limit=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các phiếu hoàn trả tại kho",
            "content": purchase_returns
        }
    )
    
    
@return_purchase_admin_router.get("/{purchase_return_id}")
async def get_detail_purchase_return(purchase_return_id: str,
                                      token_details: dict = Depends(access_token_bearer),
                                      session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()
        
    purchase_returns = await get_purchase_returns_service.get_purchase_returns(session=session, status_pr=status_pr,
                                                                              purchase_order_id=purchase_order_id,
                                                                              goods_receipt_id=goods_receipt_id,
                                                                              supplier_id=supplier_id, from_date=from_date,
                                                                              to_date=to_date, search=search, 
                                                                              sort_by=sort_by, skip=skip, limit=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các phiếu hoàn trả tại kho",
            "content": purchase_returns
        }
    )
