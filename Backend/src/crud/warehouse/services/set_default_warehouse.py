from datetime import datetime
from sqlmodel import and_
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse
from src.errors.warehouse import WareHouseException
import logging

logger = logging.getLogger(__name__)

warehouse_repository = WareHouseRepository()

class SetDefaultWarehouseService:
    async def set_default_warehouse(self, warehouse_id: str, session: AsyncSession):
        try:
            condition = [Warehouse.id == warehouse_id]
            warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition,
                                                                 for_update=True)

            if not warehouse:
                WareHouseException.warehouse_not_found()

            if not warehouse.is_active:
                WareHouseException.default_must_is_active()

            if warehouse.is_default:
                return {
                    "warehouse_id": str(warehouse.id),
                    "warehouse_name": warehouse.name,
                    "warehouse_code": warehouse.code,
                    "is_default": True,
                    "message": "Kho này đã là kho mặc định"
                }

            await self.unset_all_defaults_bulk(warehouse_id, session)

            condition = and_(Warehouse.id == warehouse_id)
            await warehouse_repository.update_warehouse(
                condition,
                {"is_default": True, "updated_at": datetime.now()},
                session
            )

            await session.commit()

            await session.refresh(warehouse)

            return {
                "warehouse_id": str(warehouse.id),
                "warehouse_name": warehouse.name,
                "warehouse_code": warehouse.code,
                "is_default": True,
                "message": "Gán kho mặc định thành công"
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in set default warehouse: {str(e)}")
            raise e


    async def unset_all_defaults_bulk(self, exclude_id: str, session: AsyncSession):
        conditions = and_(
            Warehouse.is_default == True,
            Warehouse.id != exclude_id
        )
        values = {
            "is_default": False,
            "updated_at": datetime.now()
        }
        await warehouse_repository.update_warehouse(conditions, values, session)





