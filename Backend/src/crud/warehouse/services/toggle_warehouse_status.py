from datetime import datetime
from typing import Optional
from sqlmodel import and_, or_, asc, desc

from src.crud.stock.repositories import StockRepository
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, Stock, User
from src.errors.warehouse import WareHouseException

warehouse_repository = WareHouseRepository()
stock_repository = StockRepository()
user_repository = UserRepository()

class ToggleWarehouseStatusService:
    async def toggle_warehouse_status(self, warehouse_id: str, session: AsyncSession):
        condition = [Warehouse.id == warehouse_id]
        warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition,
                                                                      for_update=True)

        if not warehouse :
            WareHouseException.warehouse_not_found()

        new_status = not warehouse.is_active

        if warehouse.is_active and not new_status:
            if warehouse.is_default:
                raise WareHouseException.inactive_must_be_not_default()

            has_stock = await self.check_warehouse_has_stock(warehouse_id, session)
            if has_stock:
                WareHouseException.cant_disable_warehouse_with_remaining_inventory()

        update_data = {
            "is_active": new_status,
            "updated_at": datetime.now()
        }

        await warehouse_repository.update_warehouse(
            and_(*condition),
            update_data,
            session
        )

        await session.commit()

        await session.refresh(warehouse)

        status_text = "kích hoạt" if new_status else "vô hiệu hóa"

        return {
            "warehouse_id": str(warehouse.id),
            "warehouse_name": warehouse.name,
            "warehouse_code": warehouse.code,
            "is_active": new_status,
            "message": f"Đã {status_text} kho thành công"
        }


    async def check_warehouse_has_stock(self, warehouse_id: str, session: AsyncSession):
        conditions = [
            Stock.warehouse_id == warehouse_id,
            Stock.quantity > 0
        ]

        _, count = await stock_repository.get_all_stocks(session=session, where_conditions=conditions)

        return count > 0

