from src.crud.supplier.repositories import SupplierRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Supplier
from src.errors.supplier import SupplierException
from src.schemas.supplier import SupplierCreate

supplier_repository = SupplierRepository()



class CreateSupplierService:
    async def create_supplier(self, supplier_data: SupplierCreate, session: AsyncSession):
        condition = [Supplier.name == supplier_data.name]
        existing = await supplier_repository.get_supplier(session=session, where_conditions=condition)
        if existing:
            SupplierException.name_supplier_already_exists()

        if supplier_data.credit_limit is not None and supplier_data.credit_limit < 0:
            SupplierException.credit_cant_negative()

        supplier_dict = supplier_data.model_dump()

        supplier_dict["code"] = await supplier_repository.generate_supplier_code(session)

        supplier = await supplier_repository.create_supplier(supplier_dict, session)

        return {
            "id": str(supplier.id),
            "code": supplier.code,
            "name": supplier.name,
            "contact_person": supplier.contact_person,
            "phone": supplier.phone,
            "email": supplier.email,
            "address": supplier.address,
            "bank_account": supplier.bank_account,
            "bank_name": supplier.bank_name,
            "credit_limit": supplier.credit_limit,
            "is_active": supplier.is_active,
            "notes": supplier.notes,
        }







