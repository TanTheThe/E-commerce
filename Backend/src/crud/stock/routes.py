from fastapi import APIRouter, status, Depends
from typing import Optional, List
from src.crud.stock.services.get_all_variants_in_warehouse import GetVariantsInWarehouseService
from src.crud.stock.services.get_low_stock_items import GetLowStockItemsService
from src.crud.stock.services.get_products_in_warehouse import GetProductsInWarehouseService
from src.crud.stock.services.get_stock_detail import GetStockDetailService
from src.crud.stock.services.get_warehouse_filters import GetWarehouseFiltersService
from src.crud.stock.services.get_warehouse_summary import GetWarehouseSummaryService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.errors.user import UserException
from src.schemas.stock import ProductStockStatus, SortBy, SortOrder

stock_admin_router = APIRouter(prefix="/stock")
stock_customer_router = APIRouter(prefix="/stock")
stock_staff_router = APIRouter(prefix="/stock")

get_low_stock_items_service = GetLowStockItemsService()
get_stock_detail_service = GetStockDetailService()
get_products_in_warehouse_service = GetProductsInWarehouseService()
get_variants_in_warehouse_service = GetVariantsInWarehouseService()
get_warehouse_summary_service = GetWarehouseSummaryService()
get_warehouse_filters_service = GetWarehouseFiltersService()
access_token_bearer = AccessTokenBearer()


@stock_admin_router.get("/warehouse/{warehouse_id}/products")
async def get_products_in_warehouse(warehouse_id: str,
                                    skip: int = 0, limit: int = 10,
                                    search: Optional[str] = None,
                                    category_ids: Optional[List[str]] = None,
                                    brand_ids: Optional[List[str]] = None,
                                    stock_status: ProductStockStatus = ProductStockStatus.ALL,
                                    sort_by: SortBy = SortBy.NAME,
                                    sort_order: SortOrder = SortOrder.ASC,
                                    token_details: dict = Depends(access_token_bearer),
                                    session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    product_summary = await get_products_in_warehouse_service.get_products_summary(session, warehouse_id, skip, limit, search,
                                                                          category_ids, brand_ids, stock_status, sort_by,
                                                                          sort_order)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách thông tin các sản phẩm trong kho",
            "content": product_summary
        }
    )


@stock_admin_router.get("/warehouse/{warehouse_id}/products/{product_id}/variants")
async def get_product_variants_in_warehouse(warehouse_id: str,
                                            product_id: str,
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
async def get_warehouse_summary(warehouse_id: str,
                                token_details: dict = Depends(access_token_bearer),
                                session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()

    result = await get_warehouse_summary_service.get_warehouse_summary(session, warehouse_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tổng quan kho hàng",
            "content": result
        }
    )


@stock_admin_router.get('/low-stock', dependencies=[Depends(admin_role_middleware)])
async def get_low_stock_items(warehouse_id: Optional[str] = None,
                               skip: int = 0, limit: int = 10,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    stocks = await get_low_stock_items_service.get_low_stock_items(session, warehouse_id, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách tồn kho thấp",
            "content": stocks
        }
    )


@stock_admin_router.get('/{stock_id}', dependencies=[Depends(admin_role_middleware)])
async def get_stock_detail(stock_id: str,
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

    result = await get_warehouse_filters_service.get_warehouse_filters(session, warehouse_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Dữ liệu filters",
            "content": result
        }
    )








