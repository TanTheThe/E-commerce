from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import and_, or_, asc, desc, func
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.errors.warehouse import WareHouseException

warehouse_repository = WareHouseRepository()

class GetWarehouseByIDService:
    async def get_warehouse_by_id(self, warehouse_id: str, session: AsyncSession):
        condition = and_(Warehouse.id == warehouse_id)
        options = [selectinload(Warehouse.manager)]

        warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition, options=options)

        if not warehouse:
            WareHouseException.warehouse_not_found()

        manager_name = None
        manager_id = None
        if warehouse.manager:
            first_name = warehouse.manager.first_name
            last_name = warehouse.manager.last_name
            if not first_name and not last_name:
                manager_name = None
            manager_name = f"{first_name or ''} {last_name or ''}".strip()
            manager_id = str(warehouse.manager.id)

        warehouse_dict = {
            "id": str(warehouse.id),
            "name": warehouse.name,
            "code": warehouse.code,
            "address": warehouse.address,
            "phone": warehouse.phone,
            "email": warehouse.email,
            "manager_id": manager_id,
            "manager_name": manager_name,
            "is_active": warehouse.is_active,
            "is_default": warehouse.is_default,
            "created_at": warehouse.created_at.isoformat() if warehouse.created_at else None
        }

        return warehouse_dict

