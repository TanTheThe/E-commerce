from fastapi import APIRouter, status, Depends
from typing import Optional
from src.crud.stock.services.create_stock_inbound import CreateStockInboundService
from src.crud.stock.services.get_low_stock_items import GetLowStockItemsService
from src.crud.stock.services.get_stock_by_product import GetStockByProductService
from src.crud.stock.services.get_stock_by_warehouse import GetStockByWarehouseService
from src.crud.stock.services.get_total_inventory import GetTotalInventoryService
from src.dependencies import AccessTokenBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.dependencies import admin_role_middleware
from src.errors.user import UserException
from src.schemas.stock import StockInboundCreate, StockStatus, StockFilterParams, StockStatusFilter, TotalInventoryFilterParams

stock_admin_router = APIRouter(prefix="/stock")
stock_customer_router = APIRouter(prefix="/stock")
stock_staff_router = APIRouter(prefix="/stock")

get_stock_by_warehouse_service = GetStockByWarehouseService()
get_stock_by_product_service = GetStockByProductService()
get_total_inventory_service = GetTotalInventoryService()
create_stock_inbound_service = CreateStockInboundService()
get_low_stock_items_service = GetLowStockItemsService()
access_token_bearer = AccessTokenBearer()


@stock_admin_router.post("/inbound")
async def create_stock_inbound(inbound_data: StockInboundCreate, 
                               token_details: dict = Depends(access_token_bearer),
                               session: AsyncSession = Depends(get_session)):
    role = token_details.get('role')

    if role not in ['admin', 'staff']:
        UserException.role_invalid()
        
    stock = await create_stock_inbound_service.create_inbound(inbound_data, session)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tạo phiếu nhập hàng thành công",
            "content": stock
        }
    )


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
    stocks = await get_low_stock_items_service.get_low_stock_items(session, warehouse_id, skip, limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Danh sách tồn kho thấp",
            "content": stocks
        }
    )








