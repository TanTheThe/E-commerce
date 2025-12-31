from typing import Optional
from sqlalchemy.orm import selectinload
from sqlmodel import or_, asc, desc, func
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, User
from src.schemas.warehouse import WarehouseFilterParams

warehouse_repository = WareHouseRepository()

class GetAllWarehousesService:
    async def get_all_warehouses(self, filters: WarehouseFilterParams, skip: int, limit: int, session: AsyncSession):
        conditions = []
        joins = None

        if filters.search:
            search_term = f"%{filters.search}%"

            joins = [(User, {
                'type': 'outer',
                'on': Warehouse.manager_id == User.id
            })]

            conditions.append(or_(
                Warehouse.name.ilike(search_term),
                Warehouse.code.ilike(search_term),
                Warehouse.address.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                func.concat(User.first_name, ' ', User.last_name).ilike(search_term)
            ))

        if filters.is_active is not None:
            conditions.append(Warehouse.is_active == filters.is_active)

        order_by_clause = self.get_order_by_clause(filters.sort_by)

        options = [selectinload(Warehouse.manager)]

        warehouses, total = await warehouse_repository.get_all_warehouse(
            session=session,
            where_conditions=conditions,
            joins=joins,
            skip=skip,
            limit=limit,
            order_by=order_by_clause,
            options=options
        )

        warehouses_list = []
        for wh in warehouses:
            manager_name = None
            if wh.manager:
                first_name = wh.manager.first_name
                last_name = wh.manager.last_name
                if not first_name and not last_name:
                    manager_name = None
                manager_name = f"{first_name or ''} {last_name or ''}".strip()

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

    def get_order_by_clause(self, sort_by: str):
        order_mapping = {
            "created_asc": asc(Warehouse.created_at),
            "created_desc": desc(Warehouse.created_at),
            "name_asc": asc(Warehouse.name),
            "name_desc": desc(Warehouse.name),
        }
        return order_mapping.get(sort_by, desc(Warehouse.created_at))

