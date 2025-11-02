from sqlalchemy import delete
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.database.models import Supplier, PurchaseOrder, Supplier_Product
from src.errors.supplier import SupplierException

supplier_repository = SupplierRepository()
purchase_order_repository = PurchaseOrderRepository()


class DeleteSupplierService:
    async def delete_supplier(self, supplier_id: str, session: AsyncSession):
        condition = [Supplier.id == supplier_id]
        existing = await supplier_repository.get_supplier(session=session, where_conditions=condition)
        if not existing:
            SupplierException.supplier_not_found()

        condition_po = [PurchaseOrder.supplier_id == supplier_id,
                        PurchaseOrder.status.in_(['draft', 'sent', 'confirmed', 'partially_received'])]
        has_active_orders = await purchase_order_repository.get_purchase_order(session=session, where_conditions=condition_po)
        if has_active_orders:
            SupplierException.cant_delete_supplier_with_pending_orders()

        if existing.current_debt != 0:
            SupplierException.cant_delete_supplier_outstanding_debt()

        delete_supplier_products_stmt = delete(Supplier_Product).where(
            Supplier_Product.supplier_id == supplier_id
        )
        await session.execute(delete_supplier_products_stmt)

        success = await supplier_repository.delete_supplier(supplier_id, session)
        if not success:
            SupplierException.error_while_delete_supplier()
