from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.supplier.repositories import SupplierRepository
from src.database.models import Supplier
from src.errors.supplier import SupplierException

supplier_repository = SupplierRepository()


class GetDetailSupplierService:
    async def get_supplier_by_id(self, session: AsyncSession,
                                supplier_id: str):
        conditions = [Supplier.id == supplier_id]

        sup = await supplier_repository.get_supplier(session=session, where_conditions=conditions)

        if not sup:
            SupplierException.supplier_not_found()

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
        }
