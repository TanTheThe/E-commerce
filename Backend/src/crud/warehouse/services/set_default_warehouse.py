from datetime import datetime
from typing import Optional
from sqlmodel import and_
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse
from src.errors.warehouse import WareHouseException

warehouse_repository = WareHouseRepository()

class SetDefaultWarehouseService:
    async def set_default_warehouse(self, warehouse_id: str, session: AsyncSession):
        condition = and_(Warehouse.id == warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(condition, session)

        if not warehouse:
            WareHouseException.warehouse_not_found()

        if not warehouse.is_active:
            WareHouseException.default_must_is_active()

        if warehouse.is_default:
            WareHouseException.warehouse_already_default()

        await self.unset_all_defaults(warehouse_id, session)

        condition = and_(Warehouse.id == warehouse_id)
        await warehouse_repository.update_warehouse(condition, {"is_default": True, "updated_at": datetime.now()},
                                                    session)
        await session.commit()


    async def unset_all_defaults(self, exclude_id: Optional[str], session: AsyncSession):
        condition_remove_default = [Warehouse.is_default == True]
        if exclude_id:
            condition_remove_default.append(Warehouse.id != exclude_id)

        warehouses, _ = await warehouse_repository.get_all_warehouse(session=session, where_conditions=condition_remove_default)

        for warehouse in warehouses:
            condition = and_(Warehouse.id == warehouse.id)
            await warehouse_repository.update_warehouse(condition, {"is_default": False, "updated_at": datetime.now()}, session)

        await session.commit()





