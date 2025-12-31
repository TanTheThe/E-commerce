from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, Depends, Query
from src.crud.purchase_order.services.approve_purchase_order import ApprovePurchaseOrderService
from src.crud.purchase_order.services.confirm_purchase_order import ConfirmPurchaseOrderService
from src.crud.purchase_order.services.create_purchase_order import CreatePurchaseOrderService
from src.crud.purchase_order.services.delete_purchase_order import DeletePurchaseOrderService
from src.crud.purchase_order.services.get_purchase_order_by_id import GetPurchaseOrderByIDService
from src.crud.purchase_order.services.get_purchase_orders import GetPurchaseOrdersService
from src.crud.purchase_order.services.get_purchase_orders_with_receipts import GetPurchaseOrdersWithReceiptsService
from src.crud.purchase_order.services.get_purchase_orders_with_returns import GetPurchaseOrdersWithReturnsService
from src.crud.purchase_order.services.send_purchase_order import SendPurchaseOrderService
from src.crud.purchase_order.services.update_po_after_negotiation import UpdatePOAfterNegotiationService
from src.crud.purchase_order.services.update_purchase_order import UpdatePurchaseOrderService
from src.dependencies import AccessTokenBearer, admin_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.purchase_order import PurchaseOrderException
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
get_purchase_orders_with_receipts_service = GetPurchaseOrdersWithReceiptsService()
get_purchase_orders_with_returns_service = GetPurchaseOrdersWithReturnsService()
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
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Tạo đơn nhập hàng thành công",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.get("/all")
async def get_purchase_orders(po_status: Optional[str] = Query(None,
                                                               description="Lọc theo trạng thái (phân tách bằng dấu phẩy): draft, sent, confirmed, completed, partial_received",
                                                               max_length=200),
                              supplier_id: Optional[str] = Query(None, description="ID nhà cung cấp"),
                              warehouse_id: Optional[str] = Query(None, description="ID kho"),
                              payment_status: Optional[str] = Query(None,
                                                                    description="Lọc theo trạng thái thanh toán: unpaid, partially_paid, paid",
                                                                    pattern="^(unpaid|partially_paid|paid)$"),
                              from_date: Optional[datetime] = Query(None, description="Lọc từ ngày (order_date)"),
                              to_date: Optional[datetime] = Query(None, description="Lọc đến ngày (order_date)"),
                              skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                              limit: int = Query(10, ge=1, le=100, description="Số bản ghi trả về"),
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    if from_date and to_date and from_date > to_date:
        PurchaseOrderException.from_date_greater_than_to_date()

    po_status_list = None
    if po_status:
        valid_statuses = {'draft', 'sent', 'confirmed', 'completed', 'partial_received', 'cancelled'}
        po_status_list = [s.strip() for s in po_status.split(',') if s.strip()]

        invalid_statuses = set(po_status_list) - valid_statuses
        if invalid_statuses:
            PurchaseOrderException.invalid_po_status(', '.join(invalid_statuses))

    purchase_orders = await get_purchase_orders_service.get_purchase_orders(
        session=session,
        status_list=po_status_list,
        supplier_id=supplier_id,
        warehouse_id=warehouse_id,
        payment_status=payment_status,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các đơn nhập hàng",
            "content": purchase_orders
        }
    )


@purchase_orders_admin_router.get("/purchase-orders-with-receipts")
async def get_purchase_orders_with_receipts(warehouse_id: str = Query(..., description="ID kho (bắt buộc)"),
                                            status_po: Optional[str] = Query(None, description="Lọc theo trạng thái PO",
                                                                             pattern="^(draft|sent|confirmed|completed|partial_received|cancelled)$"),
                                            search: Optional[str] = Query(None, max_length=100,
                                                                          description="Tìm kiếm theo mã PO"),
                                            skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                            limit: int = Query(12, ge=1, le=100, description="Số bản ghi trả về"),
                                            token_details: dict = Depends(access_token_bearer),
                                            session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    purchase_order = await get_purchase_orders_with_receipts_service.get_purchase_orders_with_receipts(
        session=session,
        warehouse_id=warehouse_id,
        status_po=status_po,
        search=search,
        skip=skip,
        limit=limit
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin đơn nhập hàng có phiếu nhập kho",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.get("/purchase-orders-with-returns")
async def get_purchase_orders_with_returns(warehouse_id: str = Query(..., description="ID kho (bắt buộc)"),
                                           status_po: Optional[str] = Query(None, description="Lọc theo trạng thái PO",
                                                                            pattern="^(draft|sent|confirmed|completed|partial_received|cancelled)$"),
                                           search: Optional[str] = Query(None, max_length=100,
                                                                         description="Tìm kiếm theo mã PO"),
                                           skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
                                           limit: int = Query(12, ge=1, le=100, description="Số bản ghi trả về"),
                                           token_details: dict = Depends(access_token_bearer),
                                           session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    purchase_order = await get_purchase_orders_with_returns_service.get_purchase_orders_with_returns(
        session=session,
        warehouse_id=warehouse_id,
        status_po=status_po,
        search=search,
        skip=skip,
        limit=limit
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin đơn nhập hàng có phiếu trả hàng",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.get("/{po_id}")
async def get_purchase_order_by_id(po_id: str, token_details: dict = Depends(access_token_bearer),
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
            "message": "Cập nhật đơn hàng thành công",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.put("/{po_id}/after-negotiation", dependencies=[Depends(admin_role_middleware)])
async def update_po_after_negotiation(po_id: str, request: UpdatePurchaseOrderAfterNegotiationRequest,
                                      token_details: dict = Depends(access_token_bearer),
                                      session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin']:
        UserException.role_invalid()

    purchase_order = await update_po_after_negotiation_service.update_po_after_negotiation(
        po_id, request, session
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật đơn hàng sau thương lượng thành công",
            "content": purchase_order
        }
    )


@purchase_orders_admin_router.put("/{po_id}/confirm", dependencies=[Depends(admin_role_middleware)])
async def confirm_purchase_order(po_id: str,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin']:
        UserException.role_invalid()

    await confirm_purchase_order_service.confirm_purchase_order(po_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xác nhận đơn hàng thành công"
        }
    )


@purchase_orders_admin_router.post("/{po_id}/approve", dependencies=[Depends(admin_role_middleware)])
async def approve_purchase_order(po_id: str, request: Optional[ApprovePurchaseOrderRequest] = None,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin']:
        UserException.role_invalid()

    user_id = token_details['user']['id']

    purchase_order = await approve_purchase_order_service.approve_purchase_order(
        session=session,
        po_id=po_id,
        approved_by=user_id,
        request=request
    )

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
    role = token_details.get('role')

    if role not in ['admin']:
        UserException.role_invalid()

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














