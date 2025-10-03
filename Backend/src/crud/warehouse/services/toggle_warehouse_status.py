from datetime import datetime
from typing import Optional
from sqlmodel import and_, or_, asc, desc
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse
from src.errors.warehouse import WareHouseException

warehouse_repository = WareHouseRepository()

class InactiveWarehouseService:
    async def toggle_warehouse_status(self, warehouse_id: str, session: AsyncSession):
        condition = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition, session)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        if not warehouse.is_active and warehouse.is_default:
            WareHouseException.inactive_must_be_not_default()

        new_status = not warehouse.is_active

        await warehouse_repository.update_warehouse(condition, {"is_active": False, "updated_at": datetime.now()}, session)


