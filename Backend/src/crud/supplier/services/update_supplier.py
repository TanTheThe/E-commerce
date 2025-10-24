from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.supplier.repositories import SupplierRepository
from src.database.models import Supplier
from src.errors.supplier import SupplierException
from src.schemas.supplier import SupplierUpdate

supplier_repository = SupplierRepository()


class UpdateSupplierService:
    async def update_supplier(self, supplier_id: str, supplier_data: SupplierUpdate, session: AsyncSession):
        condition = [Supplier.id == supplier_id]
        existing = await supplier_repository.get_supplier(session=session, where_conditions=condition)
        if not existing:
            SupplierException.supplier_not_found()

        if supplier_data.credit_limit is not None and supplier_data.credit_limit < 0:
            SupplierException.credit_cant_negative()

        update_data = supplier_data.model_dump(exclude_unset=True)
        await supplier_repository.update_supplier(and_(*condition), update_data, session)
        await session.commit()
