from fastapi import APIRouter, status, Depends, Query, Path
from typing import Optional
from sqlmodel import and_
from starlette.requests import Request
from src.crud.payment_refund.repositories import PaymentRefundRepository
from src.crud.return_order.services.complete_return_order import CompleteReturnOrderService
from src.crud.return_order.services.create_return_order import CreateReturnOrderService
from src.crud.return_order.services.get_customer_returns import GetCustomerReturnsService
from src.crud.return_order.services.get_detail_return_order import GetDetailReturnOrderService
from src.crud.return_order.services.get_return_requests import GetReturnRequestsService
from src.crud.return_order.services.process_return_request import ProcessReturnOrderService
from src.crud.return_order.services.retry_refund_service import RetryRefundService
from src.crud.return_order.services.update_payment_refund_status import UpdatePaymentRefundStatusService
from src.database.models import PaymentRefund
from src.dependencies import AccessTokenBearer, customer_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.errors.payment import PaymentException
from src.schemas.return_order import CreateReturnRequest, ProcessReturnRequest, CompleteReturnRequest, \
    UpdateRefundStatusRequest, ReturnOrderStatus, ReturnOrderSortBy

return_order_admin_router = APIRouter(prefix="/return-order")
return_order_customer_router = APIRouter(prefix="/return-order")
return_order_staff_router = APIRouter(prefix="/return-order")

create_return_order_service = CreateReturnOrderService()
get_return_requests_service = GetReturnRequestsService()
process_return_order_service = ProcessReturnOrderService()
complete_return_order_service = CompleteReturnOrderService()
update_payment_refund_status_service = UpdatePaymentRefundStatusService()
get_detail_return_order_service = GetDetailReturnOrderService()
get_customer_returns_service = GetCustomerReturnsService()
payment_refund_repository = PaymentRefundRepository()
retry_refund_service = RetryRefundService()
access_token_bearer = AccessTokenBearer()

@return_order_customer_router.post("/{order_id}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(customer_role_middleware)])
async def create_return_order(order_id: str,
                              request_data: CreateReturnRequest,
                              request: Request,
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']

    message, result = await create_return_order_service.create_return_request(
        order_id=order_id,
        user_id=user_id,
        request_data=request_data.dict(),
        session=session
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": message,
            "content": result
        }
    )

@return_order_customer_router.get('/check-eligibility/{order_id}', dependencies=[Depends(customer_role_middleware)])
async def check_return_eligibility(order_id: str,
                                   token_details: dict = Depends(access_token_bearer),
                                   session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    is_valid, message, order = await create_return_order_service.validate_return_eligibility(
        order_id=order_id,
        user_id=user_id,
        session=session
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message,
            "content": {
                "eligible": is_valid,
                "order_details": [
                    {
                        "id": str(detail.id),
                        "product_name": detail.product_snapshot.get("name") if detail.product_snapshot else "Unknown",
                        "quantity": detail.quantity,
                        "price": detail.price
                    }
                    for detail in order.order_detail
                ] if order else []
            }
        }
    )

@return_order_customer_router.get("/my-returns", dependencies=[Depends(customer_role_middleware)])
async def get_my_returns(skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
                         limit: int = Query(20, ge=1, le=100, description="Số lượng lấy (1-100)"),
                         status_filter: Optional[ReturnOrderStatus] = Query(None, alias="status", description="Lọc theo trạng thái"),
                         sort_by: ReturnOrderSortBy = Query(ReturnOrderSortBy.CREATED_DESC, description="Sắp xếp theo"),
                         token_details: dict = Depends(access_token_bearer),
                         session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']

    returns_data = await get_customer_returns_service.get_customer_returns(
        user_id=user_id,
        session=session,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        sort_by=sort_by
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Lấy danh sách yêu cầu hoàn trả thành công",
            "content": returns_data
        }
    )


@return_order_admin_router.get("/requests", dependencies=[Depends(admin_role_middleware)])
async def get_return_requests(skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
                              limit: int = Query(20, ge=1, le=100, description="Số lượng lấy (1-100)"),
                              status_filter: Optional[ReturnOrderStatus] = Query(None, description="Lọc theo trạng thái"),
                              sort_by: ReturnOrderSortBy = Query(ReturnOrderSortBy.CREATED_DESC, description="Sắp xếp theo"),
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    returns_data = await get_return_requests_service.get_return_requests(
        session=session,
        status=status_filter,
        skip=skip,
        limit=limit,
        sort_by=sort_by
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách yêu cầu hoàn trả",
            "content": returns_data
        }
    )


@return_order_admin_router.post("/process/{return_order_id}", dependencies=[Depends(admin_role_middleware)])
async def process_return_request(request: Request,
                                 return_order_id: str = Path(..., description="ID của return order", min_length=36, max_length=36),
                                 request_data: ProcessReturnRequest = ...,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    admin_id = token_details['user']['id']
    admin_email = token_details['user'].get('email', 'unknown')

    message, result = await process_return_order_service.process_return_request(
        return_order_id=return_order_id,
        action=request_data.action,
        admin_note=request_data.admin_note,
        reject_reason=request_data.reject_reason,
        attempt_count=request_data.attempt_count,
        admin_id=admin_id,
        admin_email=admin_email,
        session=session
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message,
            "content": result
        }
    )

@return_order_admin_router.post("/complete/{return_order_id}", dependencies=[Depends(admin_role_middleware)])
async def complete_return_order(return_order_id: str = Path(..., description="ID của return order", min_length=36, max_length=36),
                                request_data: CompleteReturnRequest = ...,
                                request: Request = ...,
                                background_tasks: BackgroundTasks = ...,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    message, result = await complete_return_order_service.complete_return(
        return_order_id=return_order_id,
        restore_stock=request_data.restore_stock,
        request=request,
        session=session
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message,
            "content": result
        }
    )

@return_order_admin_router.post("/retry-refund/{refund_id}", dependencies=[Depends(admin_role_middleware)])
async def retry_refund(refund_id: str,
                       request: Request,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    result = await retry_refund_service.retry_refund_payment(
        refund_id=refund_id,
        request=request,
        session=session
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thử lại hoàn tiền",
            "content": result
        }
    )

@return_order_admin_router.get("/{return_order_id}", dependencies=[Depends(admin_role_middleware)])
async def get_return_detail(return_order_id: str = Path(..., description="ID của return order", min_length=36, max_length=36),
                            token_details: dict = Depends(access_token_bearer),
                            session: AsyncSession = Depends(get_session)):
    result = await get_detail_return_order_service.get_detail_return_order(return_order_id=return_order_id, session=session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Nội dung chi tiết thông tin hoàn trả",
            "content": result
        }
    )

@return_order_admin_router.put("/refund/{refund_id}/status", dependencies=[Depends(admin_role_middleware)])
async def update_refund_status(refund_id: str,
                               request_data: UpdateRefundStatusRequest,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    refund = await payment_refund_repository.get_payment_refund(
        and_(PaymentRefund.id == refund_id),
        session
    )

    if not refund:
        PaymentException.payment_refund_not_found()

    if refund.status not in ["failed", "manual_required"]:
        PaymentException.only_update_failed_or_manual_required()

    message = await update_payment_refund_status_service.update_payment_refund_status(
        refund_id=refund_id,
        status=request_data.status,
        session=session
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message,
        }
    )









