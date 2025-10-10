from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.categories_product.repositories import CategoriesProductRepository
from src.crud.product.repositories import ProductRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.stock.repositories import StockRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import Warehouse
from src.errors.warehouse import WareHouseException

warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
stock_repository = StockRepository()
category_product_repository = CategoriesProductRepository()
product_repository = ProductRepository()

class GetWarehouseSummaryService:
    async def get_warehouse_summary(self, session: AsyncSession, warehouse_id: str):
        condition_warehouse = and_(
            Warehouse.id == warehouse_id,
            Warehouse.is_active == True
        )
        warehouse = await warehouse_repository.get_warehouse(condition_warehouse, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        summary = await stock_repository.get_warehouse_summary(warehouse_id, session)

        return {
            "warehouse": {
                "id": str(warehouse.id),
                "name": warehouse.name,
                "code": warehouse.code
            },
            "summary": summary
        }







