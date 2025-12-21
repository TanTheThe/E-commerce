from typing import Optional
from sqlalchemy import func
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

        if search and search.strip():
            search_term = search.strip()
            search_filter = (
                (Supplier.name.ilike(f"%{search_term}%")) |
                (Supplier.code.ilike(f"%{search_term}%")) |
                (Supplier.contact_person.ilike(f"%{search_term}%"))
            )
            conditions.append(search_filter)

        order_by = desc(Supplier.created_at)

        suppliers, total = await supplier_repository.get_all_suppliers(session=session, where_conditions=conditions,
                                                                       order_by=order_by, skip=skip, limit=limit)
        
        supplier_ids = [sup.id for sup in suppliers]
        
        product_counts = await self.get_product_counts_bulk(session, supplier_ids)

        items = self.format_supplier_list(suppliers, product_counts)

        return {
            "data": items,
            "total": total,
        }


    async def get_product_counts_bulk(self, session: AsyncSession, supplier_ids: list):
        if not supplier_ids:
            return {}
        
        select_columns = [
            Supplier_Product.supplier_id,
            func.count(Supplier_Product.id).label("product_count")
        ]
        
        conditions = [
            Supplier_Product.supplier_id.in_(supplier_ids),
            Supplier_Product.is_active == True
        ]
        
        group_by_columns = [Supplier_Product.supplier_id]
        
        rows, _ = await supplier_repository.get_all_suppliers_product(
            session=session,
            select_columns=select_columns,
            where_conditions=conditions,
            group_by_columns=group_by_columns,
            skip=0,
            limit=len(supplier_ids)
        )
        
        return {
            str(row.supplier_id): row.product_count
            for row in rows
        }
        
    
    def format_supplier_list(self, suppliers: list, product_counts: dict = None) -> list:
        items = []
        
        for sup in suppliers:
            supplier_id = str(sup.id)
            
            product_count = product_counts.get(supplier_id, 0) if product_counts else 0
            
            items.append({
                "id": supplier_id,
                "code": sup.code,
                "name": sup.name,
                "contact_person": sup.contact_person,
                "phone": sup.phone,
                "email": sup.email,
                "is_active": sup.is_active,
                "current_debt": sup.current_debt,
                "credit_limit": sup.credit_limit,
                "created_at": sup.created_at.isoformat() if sup.created_at else None,
                "product_count": product_count,
            })
        
        return items