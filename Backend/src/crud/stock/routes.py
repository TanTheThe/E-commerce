from fastapi import APIRouter, status, Depends
from typing import Optional
from src.crud.stock.services.get_stock_by_product import GetStockByProductService
from src.crud.stock.services.get_stock_by_warehouse import GetStockByWarehouseService
from src.crud.stock.services.get_total_inventory import GetTotalInventoryService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.schemas.stock import StockStatus, StockFilterParams, StockStatusFilter, TotalInventoryFilterParams

stock_admin_router = APIRouter(prefix="/stock")
stock_customer_router = APIRouter(prefix="/stock")
stock_staff_router = APIRouter(prefix="/stock")

get_stock_by_warehouse_service = GetStockByWarehouseService()
get_stock_by_product_service = GetStockByProductService()
get_total_inventory_service = GetTotalInventoryService()
access_token_bearer = AccessTokenBearer()


@stock_admin_router.get("/warehouse/{warehouse_id}", dependencies=[Depends(admin_role_middleware)])
async def get_stock_by_warehouse(warehouse_id: str,
                             status_stock: Optional[StockStatusFilter] = None,
                             min_quantity: Optional[int] = None,
                             max_quantity: Optional[int] = None,
                             low_stock_only: bool = False,
                             out_of_stock_only: bool = False,
                             skip: int = 0, limit: int = 10,
                             token_details: dict = Depends(access_token_bearer),
                             session: AsyncSession = Depends(get_session)):
    filters = StockFilterParams(
        status=status_stock,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        low_stock_only=low_stock_only,
        out_of_stock_only=out_of_stock_only,
    )

    stocks = await get_stock_by_warehouse_service.get_stock_by_warehouse(warehouse_id, filters, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách các tồn kho hiện tại",
            "content": stocks
        }
    )


@stock_admin_router.get('/product/{variant_id}', dependencies=[Depends(admin_role_middleware)])
async def get_stock_by_product(variant_id: str,
                               skip: int = 0, limit: int = 10,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    stocks = await get_stock_by_product_service.get_stock_by_product(variant_id, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách các tồn kho hiện tại",
            "content": stocks
        }
    )


@stock_admin_router.get('/all', dependencies=[Depends(admin_role_middleware)])
async def get_total_inventory(brand_id: Optional[str] = None,
                               material_id: Optional[str] = None,
                               tag_id: Optional[str] = None,
                               status_stock: Optional[StockStatusFilter] = None,
                               min_quantity: Optional[int] = None,
                               max_quantity: Optional[int] = None,
                               search: Optional[str] = None,
                               skip: int = 0, limit: int = 10,
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):

    filters = TotalInventoryFilterParams(
        brand_id=brand_id,
        material_id=material_id,
        tag_id=tag_id,
        status=status_stock,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        search=search
    )

    stocks = await get_total_inventory_service.get_total_inventory(filters, session, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách các tồn kho hiện tại",
            "content": stocks
        }
    )










