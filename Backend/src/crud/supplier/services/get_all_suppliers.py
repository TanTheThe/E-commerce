from typing import Optional
from sqlmodel import desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.supplier.repositories import SupplierRepository
from src.database.models import Supplier, Supplier_Product

supplier_repository = SupplierRepository()

class GetAllSuppliersService:
    async def get_all_suppliers(self, session: AsyncSession,
                                  search: Optional[str] = None,
                                  is_active: Optional[bool] = None,
                                  skip: int = 0, limit: int = 10):
        conditions = []

        if is_active is not None:
            conditions.append(Supplier.is_active == is_active)

        if search:
            search_filter = (
                (Supplier.name.ilike(f"%{search}%")) |
                (Supplier.code.ilike(f"%{search}%")) |
                (Supplier.contact_person.ilike(f"%{search}%"))
            )
            conditions.append(search_filter)

        order_by = desc(Supplier.created_at)

        suppliers, total = await supplier_repository.get_all_suppliers(session=session, where_conditions=conditions,
                                                                       order_by=order_by, skip=skip, limit=limit)

        items = []
        for sup in suppliers:
            condition_supplier_product = [
                Supplier_Product.supplier_id == sup.id,
                Supplier_Product.is_active == True
            ]
            _, product_count = await supplier_repository.get_all_suppliers_product(session=session, where_conditions=condition_supplier_product)

            items.append(
                {
                    "id": str(sup.id),
                    "code": sup.code,
                    "name": sup.name,
                    "contact_person": sup.contact_person,
                    "phone": sup.phone,
                    "email": sup.email,
                    "is_active": sup.is_active,
                    "created_at": str(sup.created_at),
                    "product_count": product_count,
                }
            )

        return {
            "data": items,
            "total": total,
        }



