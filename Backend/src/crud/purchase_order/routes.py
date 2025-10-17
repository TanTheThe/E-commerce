from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, Depends, Query
from src.crud.purchase_order.services.approve_purchase_order import ApprovePurchaseOrderService
from src.crud.purchase_order.services.confirm_purchase_order import ConfirmPurchaseOrderService
from src.crud.purchase_order.services.create_purchase_order import CreatePurchaseOrderService
from src.crud.purchase_order.services.delete_purchase_order import DeletePurchaseOrderService
from src.crud.purchase_order.services.get_purchase_order_by_id import GetPurchaseOrderByIDService
from src.crud.purchase_order.services.get_purchase_orders import GetPurchaseOrdersService
from src.crud.purchase_order.services.send_purchase_order import SendPurchaseOrderService
from src.crud.purchase_order.services.update_po_after_negotiation import UpdatePOAfterNegotiationService
from src.crud.purchase_order.services.update_purchase_order import UpdatePurchaseOrderService
from src.dependencies import AccessTokenBearer, admin_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.user import UserException
from src.schemas.purchase_order import CreatePurchaseOrderRequest, UpdatePurchaseOrderRequest, \
    ApprovePurchaseOrderRequest, SendPurchaseOrderRequest, UpdatePurchaseOrderAfterNegotiationRequest

purchase_orders_admin_router = APIRouter(prefix="/purchase-orders")
purchase_orders_customer_router = APIRouter(prefix="/purchase-orders")
purchase_orders_staff_router = APIRouter(prefix="/purchase-orders")

create_purchase_order_service = CreatePurchaseOrderService()
get_purchase_order_by_id_service = GetPurchaseOrderByIDService()
get_purchase_orders_service = GetPurchaseOrdersService()
update_purchase_order_service = UpdatePurchaseOrderService()
delete_purchase_order_service = DeletePurchaseOrderService()
approve_purchase_order_service = ApprovePurchaseOrderService()
send_purchase_order_service = SendPurchaseOrderService()
update_po_after_negotiation_service = UpdatePOAfterNegotiationService()
confirm_purchase_order_service = ConfirmPurchaseOrderService()
access_token_bearer = AccessTokenBearer()


@purchase_orders_admin_router.post("/")
async def create_purchase_order(request: CreatePurchaseOrderRequest,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    user_id = token_details['user']['id']
        
    purchase_order = await create_purchase_order_service.create_purchase_order(request, user_id, session)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tạo đơn nhập hàng thành công",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.get("/all")
async def get_purchase_orders(po_status: Optional[str] = Query(None, description="Lọc theo trạng thái: draft, sent, confirmed, completed, cancelled"),
                             supplier_id: Optional[str] = None,
                             warehouse_id: Optional[str] = None,
                             payment_status: Optional[str] = Query(None, description="Lọc theo trạng thái thanh toán: unpaid, partially_paid, paid"),
                             from_date: Optional[datetime] = Query(None, description="Lọc từ ngày (order_date)"),
                             to_date: Optional[datetime] = Query(None, description="Lọc đến ngày (order_date)"),
                             skip: int = 0, limit: int = 10,
                             token_details: dict = Depends(access_token_bearer),
                             session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    purchase_orders = await get_purchase_orders_service.get_purchase_orders(session, po_status, supplier_id, warehouse_id,
                                                                           payment_status, from_date, to_date, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các đơn nhập hàng",
            "content": purchase_orders
        }
    )


@purchase_orders_admin_router.get("/{po_id}")
async def get_purchase_order_by_id(po_id: str,
                             token_details: dict = Depends(access_token_bearer),
                             session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    purchase_order = await get_purchase_order_by_id_service.get_purchase_order(po_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin chi tiết đơn nhập hàng",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.put("/{po_id}")
async def update_purchase_order(po_id: str, request: UpdatePurchaseOrderRequest,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    purchase_order = await update_purchase_order_service.update_purchase_order(po_id, request, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật thành công",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.put("/{po_id}/after-negotiation", dependencies=[Depends(admin_role_middleware)])
async def update_po_after_negotiation(po_id: str, request: UpdatePurchaseOrderAfterNegotiationRequest,
                                      token_details: dict = Depends(access_token_bearer),
                                      session: AsyncSession = Depends(get_session)):
    purchase_order = await update_po_after_negotiation_service.update_po_after_negotiation(po_id, request, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật thành công",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.put("/{po_id}/confirm", dependencies=[Depends(admin_role_middleware)])
async def confirm_purchase_order(po_id: str,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    await confirm_purchase_order_service.confirm_purchase_order(po_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật thành công"
        }
    )


@purchase_orders_admin_router.post("/{po_id}/approve", dependencies=[Depends(admin_role_middleware)])
async def approve_purchase_order(po_id: str, request: Optional[ApprovePurchaseOrderRequest] = None,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    purchase_order = await approve_purchase_order_service.approve_purchase_order(session, po_id, user_id, request)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Duyệt đơn nhập hàng thành công",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.post("/{po_id}/send", dependencies=[Depends(admin_role_middleware)])
async def send_purchase_order_to_supplier(po_id: str, request: Optional[SendPurchaseOrderRequest] = None,
                                          token_details: dict = Depends(access_token_bearer),
                                          session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    purchase_order = await send_purchase_order_service.send_purchase_order_to_supplier(session, po_id, user_id, request)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Gửi đơn nhập hàng thành công",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.delete("/{po_id}")
async def delete_purchase_order(po_id: str,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    await delete_purchase_order_service.delete_purchase_order(po_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xóa đơn đặt hàng thành công",
        }
    )














