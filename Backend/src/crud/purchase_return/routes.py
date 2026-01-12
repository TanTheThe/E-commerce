from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, status, Depends
from src.crud.purchase_return.services.approve_purchase_return import PurchaseReturnApprovalService
from src.crud.purchase_return.services.complete_purchase_return import CompletePurchaseReturnService
from src.crud.purchase_return.services.confirmed_purchase_return import PurchaseReturnConfirmedService
from src.crud.purchase_return.services.create_purchase_return import CreatePurchaseReturnService
from src.crud.purchase_return.services.delete_purchase_return import DeletePurchaseReturnService
from src.crud.purchase_return.services.get_detail_purchase_return import GetDetailPurchaseReturnService
from src.crud.purchase_return.services.get_purchase_returns import GetPurchaseReturnsService
from src.crud.purchase_return.services.send_purchase_return import SendPurchaseReturnService
from src.crud.purchase_return.services.update_purchase_return import UpdatePurchaseReturnService
from src.dependencies import AccessTokenBearer, admin_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.purchase_return import PurchaseReturnException
from src.errors.user import UserException
from src.schemas.purchase_return import CreatePurchaseReturnRequest, GetPurchaseReturnsQuery, PurchaseReturnStatus, ReturnType, SendEmailRequest, SortBy, UpdatePurchaseReturnRequest

return_purchase_admin_router = APIRouter(prefix="/return-purchase")
return_purchase_customer_router = APIRouter(prefix="/return-purchase")
return_purchase_staff_router = APIRouter(prefix="/return-purchase")

create_purchase_return_service = CreatePurchaseReturnService()
approve_purchase_return_service = PurchaseReturnApprovalService()
send_purchase_return_service = SendPurchaseReturnService()
complete_purchase_return_service = CompletePurchaseReturnService()
get_purchase_returns_service = GetPurchaseReturnsService()
get_detail_purchase_return_service = GetDetailPurchaseReturnService()
update_purchase_return_service = UpdatePurchaseReturnService()
delete_purchase_return_service = DeletePurchaseReturnService()
confirmed_purchase_return_service = PurchaseReturnConfirmedService()
access_token_bearer = AccessTokenBearer()


@return_purchase_admin_router.post("/")
async def create_purchase_return(request: CreatePurchaseReturnRequest,
                                 token_details: dict = Depends(access_token_bearer),
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
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Tạo đơn hoàn trả hàng thành công",
            "content": purchase_return
        }
    )


@return_purchase_admin_router.post("/{purchase_return_id}/approve", dependencies=[Depends(admin_role_middleware)])
async def approve_purchase_return(purchase_return_id: str,
                                  token_details: dict = Depends(access_token_bearer),
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


@return_purchase_admin_router.post("/{purchase_return_id}/confirmed", dependencies=[Depends(admin_role_middleware)])
async def confirmed_purchase_return(purchase_return_id: str,
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']

    purchase_return = await confirmed_purchase_return_service.confirmed_purchase_return(
        session=session,
        purchase_return_id=purchase_return_id,
        confirmed_by=user_id
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xác nhận nhận hàng hoàn trả thành công",
            "content": purchase_return
        }
    )


@return_purchase_admin_router.post("/{purchase_return_id}/send-email", dependencies=[Depends(admin_role_middleware)])
async def send_return_email_to_supplier(purchase_return_id: str,
                                        request: SendEmailRequest,
                                        token_details: dict = Depends(access_token_bearer),
                                        session: AsyncSession = Depends(get_session)):

    purchase_return = await send_purchase_return_service.send_return_email_to_supplier(
        session=session,
        purchase_return_id=purchase_return_id,
        supplier_email=request.supplier_email
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
                                   token_details: dict = Depends(access_token_bearer),
                                   session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']

    purchase_return = await complete_purchase_return_service.complete_purchase_return(
        session=session,
        purchase_return_id=purchase_return_id,
        completed_by=user_id
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Hoàn tất phiếu hoàn trả thành công",
            "content": purchase_return
        }
    )
    
    
@return_purchase_admin_router.get("/")
async def get_all_purchase_returns(warehouse_id: str,
                                   status_pr: Optional[PurchaseReturnStatus] = Query(None, description="Trạng thái phiếu"),
                                   return_type: Optional[ReturnType] = Query(None, description="Loại hoàn trả"),
                                   purchase_order_id: Optional[str] = Query(None, description="ID đơn hàng"),
                                   goods_receipt_id: Optional[str] = Query(None, description="ID phiếu nhập kho"),
                                   supplier_id: Optional[str] = Query(None, description="ID nhà cung cấp"),
                                   from_date: Optional[datetime] = Query(None, description="Từ ngày"),
                                   to_date: Optional[datetime] = Query(None, description="Đến ngày"),
                                   search: Optional[str] = Query(None, description="Tìm kiếm theo mã phiếu", max_length=100),
                                   sort_by: Optional[SortBy] = Query(SortBy.RETURN_DATE_DESC, description="Sắp xếp"),
                                   skip: int = Query(ge=0, description="Số bản ghi bỏ qua"), 
                                   limit: int = Query(ge=1, le=100, description="Số bản ghi tối đa"),
                                   token_details: dict = Depends(access_token_bearer),
                                   session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()
        
    query_params = GetPurchaseReturnsQuery(
            warehouse_id=warehouse_id,
            status_pr=status_pr,
            return_type=return_type,
            purchase_order_id=purchase_order_id,
            goods_receipt_id=goods_receipt_id,
            supplier_id=supplier_id,
            from_date=from_date,
            to_date=to_date,
            search=search,
            sort_by=sort_by,
            skip=skip,
            limit=limit
        )
    
    purchase_returns = await get_purchase_returns_service.get_purchase_returns(
            session=session,
            warehouse_id=query_params.warehouse_id,
            status_pr=query_params.status_pr.value if query_params.status_pr else None,
            return_type=query_params.return_type.value if query_params.return_type else None,
            purchase_order_id=query_params.purchase_order_id,
            goods_receipt_id=query_params.goods_receipt_id,
            supplier_id=query_params.supplier_id,
            from_date=query_params.from_date,
            to_date=query_params.to_date,
            search=query_params.search,
            sort_by=query_params.sort_by,
            skip=query_params.skip,
            limit=query_params.limit
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Lấy danh sách phiếu hoàn trả thành công",
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
        
    purchase_return = await get_detail_purchase_return_service.get_purchase_return_by_id(purchase_return_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Lấy chi tiết phiếu hoàn trả thành công",
            "content": purchase_return
        }
    )


@return_purchase_admin_router.put("/{purchase_return_id}")
async def update_purchase_return(purchase_return_id: str, 
                                 request: UpdatePurchaseReturnRequest,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    update_data = request.model_dump(exclude_none=True)

    pr = await update_purchase_return_service.update_purchase_return(session, purchase_return_id, update_data)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật phiếu hoàn trả thành công",
            "content": pr
        }
    )


@return_purchase_admin_router.delete("/{purchase_return_id}")
async def delete_purchase_return(purchase_return_id: str,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role != 'admin':
        PurchaseReturnException.only_admin_can_delete_pr()

    await delete_purchase_return_service.delete_purchase_return(session, purchase_return_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa phiếu hoàn trả thành công"
        }
    )


