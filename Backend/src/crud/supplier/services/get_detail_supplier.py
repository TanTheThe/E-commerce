from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.supplier.repositories import SupplierRepository
from src.database.models import Supplier, Supplier_Product
from src.errors.supplier import SupplierException

supplier_repository = SupplierRepository()


class GetDetailSupplierService:
    async def get_supplier_by_id(self, session: AsyncSession, supplier_id: str):
        conditions = [Supplier.id == supplier_id]
        options = [
            selectinload(Supplier.supplier_products).selectinload(Supplier_Product.products)
        ]

        sup = await supplier_repository.get_supplier(
            session=session, 
            where_conditions=conditions, 
            options=options
        )

        if not sup:
            SupplierException.supplier_not_found()

        products = []
        for sp in sup.supplier_products:
            if sp.products:
                product = sp.products
                products.append({
                    "id": str(product.id),
                    "name": product.name,
                    "image": product.images[0],
                    "status": product.status,
                    "is_active": sp.is_active,
                    "notes": sp.notes,
                })

        return {
            "id": str(sup.id),
            "code": sup.code,
            "name": sup.name,
            "contact_person": sup.contact_person,
            "phone": sup.phone,
            "email": sup.email,
            "address": sup.address,
            "bank_account": sup.bank_account,
            "bank_name": sup.bank_name,
            "credit_limit": sup.credit_limit,
            "is_active": sup.is_active,
            "notes": sup.notes,
            "current_debt": sup.current_debt,
            "created_at": str(sup.created_at),
            "updated_at": str(sup.updated_at) if sup.updated_at else None,
            "products": products,
            "total_products": len(products)
        }
