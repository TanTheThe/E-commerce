from typing import Optional, Literal
from datetime import datetime
from fastapi import APIRouter, status, Depends, Query, Path
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request
from src.cache import cache_service, CacheKeys
from src.crud.order.services.cancel_order.cancel_order import CancelOrderService
from src.crud.order.services.cancel_order.get_cancellation_requests import GetCancellationRequestService
from src.crud.order.services.process_cancellation.process_cancellation import ProcessCancellationService
from src.crud.order.services.confirm_order_received import ConfirmOrderReceivedService
from src.crud.order.services.create_order.create_order import CreateOrderService
from src.crud.order.services.create_order.create_order_security import CreateOrderSecurityService
from src.crud.order.services.get_all_orders import GetAllOrdersService
from src.crud.order.services.get_detail_order import GetDetailOrderService
from src.crud.order.services.statistics_order import StatisticsOrderService
from src.crud.order.services.update_status import UpdateStatusOrderService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.schemas.order import OrderCreateModel, StatusUpdateModel, OrderFilterModel, CancelOrderRequest, \
    ProcessCancellationRequest, StatisticsPeriod, DateRangeCalculator
from src.dependencies import admin_role_middleware, customer_role_middleware
import logging

logger = logging.getLogger(__name__)

order_admin_router = APIRouter(prefix="/order")
order_customer_router = APIRouter(prefix="/order")
order_staff_router = APIRouter(prefix="/order")

limiter = Limiter(key_func=get_remote_address)

get_all_order_service = GetAllOrdersService()
create_order_service = CreateOrderService()
get_detail_order_service = GetDetailOrderService()
update_status_order_service = UpdateStatusOrderService()
confirm_order_received_service = ConfirmOrderReceivedService()
statistics_order_service = StatisticsOrderService()
cancel_order_service = CancelOrderService()
process_cancellation_service = ProcessCancellationService()
get_cancellation_requests_service = GetCancellationRequestService()
create_order_security_service = CreateOrderSecurityService()
access_token_bearer = AccessTokenBearer()


@order_admin_router.get("/statistics/overview", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_statistics_overview(from_date: Optional[datetime] = Query(None, description="Start date (inclusive)"),
                                  to_date: Optional[datetime] = Query(None, description="End date (inclusive)"),
                                  period: StatisticsPeriod = Query(
                                      StatisticsPeriod.LAST_7_DAYS,
                                      description="Predefined period (ignored if dates provided)"
                                  ),
                                  token_details: dict = Depends(access_token_bearer),
                                  session: AsyncSession = Depends(get_session)):
    calculated_from, calculated_to = DateRangeCalculator.get_date_range(
        from_date, to_date, period
    )

    if from_date and to_date:
        cache_key = CacheKeys.analytics_overview_key(calculated_from=calculated_from, calculated_to=calculated_to)
        ttl = 600
    else:
        cache_key = CacheKeys.analytics_overview_key(period=period)
        ttl_map = {
            "today": 300,  # 5 minutes
            "last_7_days": 900,  # 15 minutes
            "last_30_days": 1800,  # 30 minutes
            "last_90_days": 3600,  # 1 hour
        }
        ttl = ttl_map.get(period.value, 600)

    cached_stats = await cache_service.get(cache_key)

    if cached_stats is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Thống kê tổng quan",
                "content": {
                    "period": period.value if not (from_date and to_date) else "custom",
                    "from_date": calculated_from.isoformat(),
                    "to_date": calculated_to.isoformat(),
                    **cached_stats
                }
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    stats = await statistics_order_service.get_comprehensive_statistics(
        session=session,
        from_date=calculated_from,
        to_date=calculated_to
    )

    await cache_service.set(cache_key, stats, ttl=ttl)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thống kê tổng quan",
            "content": {
                "period": period.value if not (from_date and to_date) else "custom",
                "from_date": calculated_from.isoformat(),
                "to_date": calculated_to.isoformat(),
                **stats
            }
        }
    )


@order_admin_router.get("/cancellation-requests", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_cancellation_requests(skip: int = 0, limit: int = 20,
                                    status_filter: str = "pending",
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    should_cache = (status_filter == "pending" and skip == 0 and limit == 20)
    cache_key = CacheKeys.cancellation_pending_page_1()

    if should_cache:
        cached_data = await cache_service.get(cache_key)
        if cached_data is not None:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"Danh sách yêu cầu hủy đơn ({status_filter})",
                    "content": cached_data
                }
            )

    if status_filter == "pending":
        orders, total = await get_cancellation_requests_service.get_cancellation_requests(session, skip=skip, limit=limit)
    else:
        orders, total = await get_cancellation_requests_service.get_orders_by_status(session, "cancelled", skip, limit)

    orders_data = []
    for order in orders:
        orders_data.append({
            "id": str(order.id),
            "code": order.code,
            "total_price": order.total_price,
            "status": order.status,
            "cancellation_status": order.cancellation_status,
            "cancellation_reason": order.cancellation_reason,
            "cancellation_requested_at": str(order.cancellation_requested_at),
            "first_name": order.user.first_name if order.user else None,
            "last_name": order.user.last_name if order.user else None,
            "created_at": str(order.created_at)
        })

    result = {
        "data": orders_data,
        "total": total
    }

    if should_cache:
        await cache_service.set(cache_key, result, ttl=120)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Danh sách yêu cầu hủy đơn ({status_filter})",
            "content": result
        }
    )

@order_customer_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(customer_role_middleware)])
async def create_order(request: Request, order_data: OrderCreateModel,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    customer_id = token_details['user']['id']

    try:
        ip_address = create_order_security_service.get_client_ip(request)
        await create_order_security_service.check_create_order_rate_limit(ip_address)
    except Exception as e:
        logger.error(f"Error checking rate limit: {str(e)}")

    order_dict = await create_order_service.create_order(customer_id, order_data, session)

    await cache_service.delete_pattern(CacheKeys.analytics())

    await cache_service.delete_pattern(CacheKeys.order_list_user_without_page(user_id=customer_id))

    await cache_service.delete_pattern(CacheKeys.cart_user(user_id=customer_id))

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Đơn hàng đã được tạo thành công",
            "content": order_dict,
        }
    )

@order_customer_router.get("/status/{status_order}", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def get_all_order_customer(status_order: str, skip: int = Query(0, ge=0),
                                 limit: int = Query(10, ge=1, le=100),
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    customer_id = token_details['user']['id']

    should_cache = (skip == 0 and limit == 10)
    cache_key = CacheKeys.order_list_user(customer_id, page=1)

    cache_key = CacheKeys.order_list_user_with_status(cache_key, status_order)

    if should_cache:
        cached_data = await cache_service.get(cache_key)
        if cached_data is not None:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Thông tin các đơn hàng",
                    "content": cached_data
                }
            )

    order_dict = await get_all_order_service.get_all_order_customer(customer_id, status_order, session, skip=skip, limit=limit)

    if should_cache:
        await cache_service.set(cache_key, order_dict, ttl=180)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các đơn hàng",
            "content": order_dict
        }
    )

@order_customer_router.get("/{order_id}", status_code=status.HTTP_200_OK,
                           dependencies=[Depends(customer_role_middleware)])
async def get_detail_order_customer(order_id: str = Path(..., min_length=36, max_length=36),
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    customer_id = token_details['user']['id']

    cache_key = CacheKeys.order_detail_customer(order_id, customer_id)

    cached_order = await cache_service.get(cache_key)
    if cached_order is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Chi tiết của đơn hàng",
                "content": cached_order
            }
        )

    order_dict = await get_detail_order_service.get_detail_order_customer(order_id, customer_id, session)

    logger.debug(f"Cache MISS: {cache_key}")

    await cache_service.set(cache_key, order_dict, ttl=300)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Chi tiết của đơn hàng",
            "content": order_dict
        }
    )


@order_admin_router.get("/{order_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_detail_order_admin(order_id: str = Path(..., min_length=36, max_length=36),
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    cache_key = CacheKeys.order_detail_admin(order_id)

    cached_order = await cache_service.get(cache_key)
    if cached_order is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Chi tiết của đơn hàng",
                "content": cached_order
            }
        )

    order_dict = await get_detail_order_service.get_detail_order_admin(order_id, session)

    logger.debug(f"Cache MISS: {cache_key}")

    await cache_service.set(cache_key, order_dict, ttl=300)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Chi tiết của đơn hàng",
            "content": order_dict
        }
    )

@order_admin_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_all_order_admin(skip: int = Query(0, ge=0),
                              limit: int = Query(10, ge=1, le=100),
                              search: Optional[str] = Query(
                                  None,
                                  max_length=100,
                                  description="Tìm kiếm theo order code, customer name"
                              ),
                              status_filter: Optional[Literal[
                                  "pending", "confirmed", "shipping",
                                  "delivered", "received", "cancelled", "returned"
                              ]] = Query(None, description="Filter theo status"),
                              sort_by_total_price: Optional[Literal["cheapest", "most_expensive"]] = Query(
                                  None,
                                  description="Sắp xếp theo giá"
                              ),
                              sort_by_created_at: Optional[Literal["newest", "oldest"]] = Query(
                                  None,
                                  description="Sắp xếp theo thời gian tạo"
                              ),
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    filter_data = OrderFilterModel(
        search=search,
        sort_by_total_price=sort_by_total_price,
        sort_by_created_at=sort_by_created_at,
        status=status_filter,
    )
    order_dict = await get_all_order_service.get_all_order_admin(session, filter_data, skip=skip, limit=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các đơn hàng",
            "content": order_dict
        }
    )


@order_admin_router.post("/{order_id}/process-cancellation", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def process_cancellation_request(order_id: str,
                                       data: ProcessCancellationRequest,
                                       request: Request,
                                       token_details: dict = Depends(access_token_bearer),
                                       session: AsyncSession = Depends(get_session)):
    message, order = await process_cancellation_service.process_cancellation_by_admin(order_id, data, request, session)

    await cache_service.delete_pattern(f"{CacheKeys.order_detail(order_id)}:*")

    await cache_service.delete(CacheKeys.cancellation_pending_page_1())

    customer_id = str(order.get("user_id")) if isinstance(order, dict) else str(order.user_id)
    await cache_service.delete_pattern(CacheKeys.order_list_user_without_page(customer_id))

    if data.approved:
        await cache_service.delete_pattern(CacheKeys.analytics())

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message,
            "content": order
        }
    )


@order_customer_router.post("/{order_id}/cancel", dependencies=[Depends(customer_role_middleware)])
async def cancel_order(order_id: str, request: CancelOrderRequest,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    message, result = await cancel_order_service.cancel_order_by_customer(order_id, user_id, request, session)

    await cache_service.delete_pattern(f"{CacheKeys.order_detail(order_id)}:*")

    await cache_service.delete_pattern(CacheKeys.order_list_user_without_page(user_id))

    await cache_service.delete(CacheKeys.cancellation_pending_page_1())

    await cache_service.delete_pattern(CacheKeys.analytics())

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": message,
            "content": result
        }
    )

@order_admin_router.put("/{order_id}/status", status_code=status.HTTP_200_OK,
                        dependencies=[Depends(admin_role_middleware)])
async def update_status(order_id: str,
                        request: StatusUpdateModel,
                        token_details: dict = Depends(access_token_bearer),
                        session: AsyncSession = Depends(get_session)):
    order_updated, old_status = await update_status_order_service.update_status(order_id, request, session)

    await cache_service.delete_pattern(f"{CacheKeys.order_detail(order_id)}:*")

    customer_id = str(order_updated.user_id)
    await cache_service.delete_pattern(CacheKeys.order_list_user_without_page(customer_id))

    if request.status in ["delivered", "received", "cancelled"]:
        await cache_service.delete_pattern(CacheKeys.analytics())

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật trạng thái đơn hàng thành công",
            "content": {
                "order_id": str(order_updated.id),
                "current_status": order_updated.status,
                "previous_status": old_status,
            }
        }
    )

@order_customer_router.put("/{order_id}/confirm-received", status_code=status.HTTP_200_OK,
                        dependencies=[Depends(customer_role_middleware)])
async def confirm_order_received(order_id: str,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    user_id = token_details['user']['id']
    order_updated = await confirm_order_received_service.confirm_order_received_service(order_id, user_id, session)

    await cache_service.delete_pattern(f"{CacheKeys.order_detail(order_id)}:*")

    await cache_service.delete_pattern(CacheKeys.order_list_user_without_page(user_id))

    await cache_service.delete_pattern(CacheKeys.analytics())

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Xác nhận đã nhận hàng thành công",
            "content": {
                "order_id": str(order_updated.id),
                "status": order_updated.status,
                "received_at": order_updated.received_at.isoformat(),
            }
        }
    )
