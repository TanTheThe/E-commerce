from fastapi import APIRouter, status, Depends, Query, Path
from typing import Optional, List
from src.cache import cache_service
from src.crud.stock.services.get_all_variants_in_warehouse import GetVariantsInWarehouseService
from src.crud.stock.services.get_low_stock_items import GetLowStockItemsService
from src.crud.stock.services.get_products_summary import GetProductsSummaryService
from src.crud.stock.services.get_stock_detail import GetStockDetailService
from src.crud.stock.services.get_warehouse_filters import GetWarehouseFiltersService
from src.crud.stock.services.get_warehouse_summary import GetWarehouseSummaryService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.errors.user import UserException
from src.schemas.stock import ProductStockStatus, SortBy, SortOrder, ProductsSummaryQueryParams, LowStockQueryParams, \
    StockSeverity
import logging


logger = logging.getLogger(__name__)

stock_admin_router = APIRouter(prefix="/stock")
stock_customer_router = APIRouter(prefix="/stock")
stock_staff_router = APIRouter(prefix="/stock")

get_low_stock_items_service = GetLowStockItemsService()
get_stock_detail_service = GetStockDetailService()
get_products_summary_service = GetProductsSummaryService()
get_variants_in_warehouse_service = GetVariantsInWarehouseService()
get_warehouse_summary_service = GetWarehouseSummaryService()
get_warehouse_filters_service = GetWarehouseFiltersService()
access_token_bearer = AccessTokenBearer()


@stock_admin_router.get("/warehouse/{warehouse_id}/products")
async def get_products_in_warehouse(warehouse_id: str,
                                    skip: int = Query(ge=0, description="Số bản ghi bỏ qua"),
                                    limit: int = Query(ge=1, le=100, description="Số bản ghi tối đa"),
                                    search: Optional[str] = Query(None, max_length=100, description="Tìm kiếm"),
                                    category_ids: Optional[List[str]] = Query(default=None, max_items=50),
                                    brand_ids: Optional[List[str]] = Query(default=None, max_items=50),
                                    stock_status: ProductStockStatus = Query(default=ProductStockStatus.ALL),
                                    sort_by: SortBy = Query(default=SortBy.NAME),
                                    sort_order: SortOrder = Query(default=SortOrder.ASC),
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    query_params = ProductsSummaryQueryParams(
        search=search,
        category_ids=category_ids,
        brand_ids=brand_ids,
        stock_status=stock_status,
        sort_by=sort_by,
        sort_order=sort_order
    )

    product_summary = await get_products_summary_service.get_products_summary(session, warehouse_id, query_params, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách thông tin các sản phẩm trong kho",
            "content": product_summary
        }
    )


@stock_admin_router.get("/warehouse/{warehouse_id}/products/{product_id}/variants")
async def get_product_variants_in_warehouse(warehouse_id: str = Path(..., description="UUID của warehouse"),
                                            product_id: str = Path(..., description="UUID của product"),
                                            token_details: dict = Depends(access_token_bearer),
                                            session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    result = await get_variants_in_warehouse_service.get_product_variants_detail(session, warehouse_id, product_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Chi tiết variants của sản phẩm",
            "content": result
        }
    )


@stock_admin_router.get("/warehouse/{warehouse_id}/stocks/summary")
async def get_warehouse_summary(warehouse_id: str = Path(..., description="UUID của warehouse"),
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    cache_key = f"stock:warehouse:{warehouse_id}:summary"

    cached_summary = await cache_service.get(cache_key)
    if cached_summary is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Tổng quan kho hàng",
                "content": cached_summary
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    result = await get_warehouse_summary_service.get_warehouse_summary(session, warehouse_id)

    await cache_service.set(cache_key, result, ttl=600)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tổng quan kho hàng",
            "content": result
        }
    )


@stock_admin_router.get('/low-stock', dependencies=[Depends(admin_role_middleware)])
async def get_low_stock_items(warehouse_id: Optional[str] = Query(None, description="ID kho hàng"),
                              severity: Optional[StockSeverity] = Query(None, description="Lọc theo mức độ nghiêm trọng"),
                              skip: int = Query(ge=0, description="Số bản ghi bỏ qua"),
                              limit: int = Query(ge=1, le=100, description="Số bản ghi tối đa"),
                              token_details: dict = Depends(access_token_bearer),
                              session: AsyncSession = Depends(get_session)):
    severity_str = severity.value if severity else None

    warehouse_part = f"warehouse:{warehouse_id}" if warehouse_id else "all_warehouses"
    severity_part = f"severity:{severity_str}" if severity_str else "all_severity"

    cache_key = f"stock:low_stock:{warehouse_part}:{severity_part}:skip:{skip}:limit:{limit}"

    cached_stocks = await cache_service.get(cache_key)
    if cached_stocks is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Danh sách tồn kho thấp",
                "content": cached_stocks
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    params = LowStockQueryParams(
        warehouse_id=warehouse_id,
        severity=severity
    )
    stocks = await get_low_stock_items_service.get_low_stock_items(session, params, skip, limit)

    await cache_service.set(cache_key, stocks, ttl=300)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách tồn kho thấp",
            "content": stocks
        }
    )


@stock_admin_router.get('/{stock_id}', dependencies=[Depends(admin_role_middleware)])
async def get_stock_detail(stock_id: str = Path(..., description="UUID của stock"),
                           token_details: dict = Depends(access_token_bearer),
                           session: AsyncSession = Depends(get_session)):
    stock = await get_stock_detail_service.get_stock_detail(stock_id, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tồn kho chi tiết",
            "content": stock
        }
    )


@stock_admin_router.get("/warehouse/{warehouse_id}/filters")
async def get_warehouse_filters(warehouse_id: str,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    cache_key = f"stock:warehouse:{warehouse_id}:filters"

    cached_filters = await cache_service.get(cache_key)
    if cached_filters is not None:
        logger.debug(f"Cache HIT: {cache_key}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Dữ liệu filters",
                "content": cached_filters
            }
        )

    logger.debug(f"Cache MISS: {cache_key}")

    result = await get_warehouse_filters_service.get_warehouse_filters(session, warehouse_id)

    await cache_service.set(cache_key, result, ttl=1800)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Dữ liệu filters",
            "content": result
        }
    )








