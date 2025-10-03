from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import and_, or_, asc, desc, func
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User

warehouse_repository = WareHouseRepository()

class GetAllWarehousesService:
    async def get_all_warehouses(self, search: Optional[str], is_active: Optional[bool],
                                 sort_by: Optional[str], skip: int, limit: int, session: AsyncSession):
        conditions = []
        joins = None

        if search:
            search_term = f"%{search}%"

            joins = [(User, Warehouse.manager_id == User.id)]

            conditions.append(or_(
                Warehouse.name.ilike(search_term),
                Warehouse.code.ilike(search_term),
                Warehouse.address.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            ))

        if is_active is not None:
            conditions.append(Warehouse.is_active == is_active)

        order_by_clause = asc(Warehouse.created_at) if sort_by == "created_asc" else desc(Warehouse.created_at)

        options = [selectinload(Warehouse.manager)]

        warehouses, total = await warehouse_repository.get_all_warehouse(conditions, session, skip, limit,
                                                       joins, order_by_clause, options)

        warehouses_list = []
        for wh in warehouses:
            manager_name = None
            if wh.manager:
                manager_name = f"{wh.manager.first_name} {wh.manager.last_name}".strip()

            warehouse_dict = {
                "id": str(wh.id),
                "name": wh.name,
                "code": wh.code,
                "address": wh.address,
                "phone": wh.phone,
                "email": wh.email,
                "manager_name": manager_name,
                "is_active": wh.is_active,
                "is_default": wh.is_default,
                "created_at": wh.created_at.isoformat() if wh.created_at else None
            }
            warehouses_list.append(warehouse_dict)

        return {
            "data": warehouses_list,
            "total": total
        }

