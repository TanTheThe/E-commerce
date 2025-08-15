from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, status, Depends, Query
from src.crud.order.services import OrderService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.schemas.order import OrderCreateModel, StatusUpdateModel, OrderFilterModel
from src.dependencies import admin_role_middleware, customer_role_middleware

order_admin_router = APIRouter(prefix="/order")
order_customer_router = APIRouter(prefix="/order")
order_common_router = APIRouter(prefix="/order")

order_service = OrderService()
access_token_bearer = AccessTokenBearer()


@order_admin_router.get("/statistics/count-orders", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def count_new_orders(from_date: Optional[datetime] = Query(default=None),
                           to_date: Optional[datetime] = Query(default=None),
                           token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)):
    to_date = to_date or datetime.utcnow()
    from_date = from_date or (to_date - timedelta(days=7))
    count_orders = await order_service.count_new_orders(to_date, from_date, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thống kê số lượng",
            "content": {
                "count_orders": str(count_orders)
            }
        }
    )

@order_admin_router.get("/statistics/sales", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_total_sales(token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)):
    today = datetime.utcnow()
    seven_days_ago = today - timedelta(days=7)

    total_sales = await order_service.get_total_sales(today, seven_days_ago, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thống kê tổng doanh số",
            "content": {
                "total_sales": total_sales
            }
        }
    )

@order_admin_router.get("/statistics/revenue", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_total_revenue(token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)):
    today = datetime.utcnow()
    seven_days_ago = today - timedelta(days=7)

    total_revenue = await order_service.get_total_revenue(today, seven_days_ago, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thống kê tổng doanh số",
            "content": {
                "total_revenue": total_revenue
            }
        }
    )

@order_customer_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(customer_role_middleware)])
async def create_order(order_data: OrderCreateModel,
                       token_details: dict = Depends(access_token_bearer),
                       session: AsyncSession = Depends(get_session)):
    customer_id = token_details['user']['id']
    order_dict = await order_service.create_order(customer_id, order_data, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Sản phẩm mới vừa được thêm vào",
            "content": order_dict,
        }
    )

@order_customer_router.get("/{order_id}", status_code=status.HTTP_200_OK,
                           dependencies=[Depends(customer_role_middleware)])
async def get_detail_order_customer(order_id: str,
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    customer_id = token_details['user']['id']
    order_dict = await order_service.get_detail_order_customer(order_id, customer_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Chi tiết của đơn hàng",
            "content": order_dict
        }
    )


@order_admin_router.get("/{order_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_detail_order_admin(order_id: str,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    order_dict = await order_service.get_detail_order_admin(order_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Chi tiết của đơn hàng",
            "content": order_dict
        }
    )


@order_customer_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_role_middleware)])
async def get_all_order_customer(skip: int = 0, limit: int = 10,
                                 token_details: dict = Depends(access_token_bearer),
                                 session: AsyncSession = Depends(get_session)):
    customer_id = token_details['user']['id']
    order_dict = await order_service.get_all_order_customer(customer_id, session, skip=skip, limit=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các đơn hàng",
            "content": order_dict
        }
    )


@order_admin_router.get("/", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_role_middleware)])
async def get_all_order_admin(skip: int = 0, limit: int = 10,
                              search: Optional[str] = None,
                              sort_by_total_price: Optional[str] = None,
                              sort_by_created_at: Optional[str] = None,
                              status_filter: Optional[str] = None,
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    filter_data = OrderFilterModel(
        search=search,
        sort_by_total_price=sort_by_total_price,
        sort_by_created_at=sort_by_created_at,
        status=status_filter,
    )
    order_dict = await order_service.get_all_order_admin(session, filter_data, skip=skip, limit=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Thông tin các đơn hàng",
            "content": order_dict
        }
    )


@order_admin_router.put("/status/{order_id}", status_code=status.HTTP_201_CREATED,
                        dependencies=[Depends(admin_role_middleware)])
async def update_status(order_id: str,
                        status_update: StatusUpdateModel,
                        token_details: dict = Depends(access_token_bearer),
                        session: AsyncSession = Depends(get_session)):
    order_after_update = await order_service.update_status(order_id, status_update, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật trạng thái đơn hành thành công",
            "content": order_after_update.status
        }
    )
