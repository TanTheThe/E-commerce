from datetime import datetime, timedelta
from sqlalchemy import delete, update
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.database.models import Supplier, PurchaseOrder, Supplier_Product
from src.errors.supplier import SupplierException

supplier_repository = SupplierRepository()
purchase_order_repository = PurchaseOrderRepository()


class DeleteSupplierService:
    async def delete_supplier(self, supplier_id: str, session: AsyncSession, force: bool = False, permanent: bool = False):
        condition = [Supplier.id == supplier_id]
        supplier = await supplier_repository.get_supplier(session=session, where_conditions=condition)
        if not supplier:
            SupplierException.supplier_not_found()
            
        validation_result = await self.validate_can_delete(
            supplier_id, supplier, session, force
        )
        
        if not validation_result['can_delete']:
            raise SupplierException.cannot_delete_supplier(
                reasons=validation_result['reasons']
            )
        
        if permanent:
            await self.permanent_delete(supplier_id, session)
            deletion_type = "permanent"
        else:
            await self.soft_delete(supplier_id, session)
            deletion_type = "soft"
        
        await session.commit()
        
        return {
            "supplier_id": supplier_id,
            "supplier_name": supplier.name,
            "supplier_code": supplier.code,
            "deletion_type": deletion_type,
            "deleted_at": datetime.now().isoformat(),
            "warnings": validation_result.get('warnings', [])
        }

            
    async def validate_can_delete(self, supplier_id: str, supplier, session: AsyncSession, force: bool):
        reasons = []
        warnings = []
        
        active_statuses = ['draft', 'sent', 'confirmed', 'partially_received']
        condition_po = [PurchaseOrder.supplier_id == supplier_id,
                        PurchaseOrder.status.in_(active_statuses)]
        
        _, active_orders_count = await purchase_order_repository.get_all_purchase_orders(
            session=session,
            where_conditions=condition_po
        )
        
        if active_orders_count > 0:
            reasons.append(
                f"Nhà cung cấp có {active_orders_count} đơn hàng đang chờ xử lý. "
                "Vui lòng hoàn tất hoặc hủy các đơn hàng trước."
            )
            
        if not force:
            cutoff_date = datetime.now() - timedelta(days=30)
            condition_recent_po = [
                PurchaseOrder.supplier_id == supplier_id,
                PurchaseOrder.created_at >= cutoff_date
            ]
            _, recent_transactions = await purchase_order_repository.get_all_purchase_orders(
                session=session, where_conditions=condition_recent_po
            )
            
            if recent_transactions > 0:
                warnings.append(
                    f"Nhà cung cấp có {recent_transactions} giao dịch trong 30 ngày gần đây"
                )
        
        _, linked_products = await supplier_repository.get_all_suppliers_product(
            session=session,
            where_conditions=[Supplier_Product.supplier_id == supplier_id]
        )
        if linked_products > 0:
            warnings.append(
                f"Nhà cung cấp đang liên kết với {linked_products} sản phẩm"
            )
            
        _, completed_orders = await purchase_order_repository.get_all_purchase_orders(
            session=session, where_conditions=[
                PurchaseOrder.supplier_id == supplier_id,
                PurchaseOrder.status.in_(['completed', 'cancelled'])
            ]
        )
        if completed_orders > 0:
            warnings.append(
                f"Nhà cung cấp có {completed_orders} đơn hàng đã hoàn thành. "
                "Dữ liệu lịch sử sẽ bị ảnh hưởng nếu xóa vĩnh viễn."
            )
            
        return {
            'can_delete': len(reasons) == 0,
            'reasons': reasons,
            'warnings': warnings
        }
        
        
    async def permanent_delete(self, supplier_id: str, session: AsyncSession):
        delete_products_stmt = delete(Supplier_Product).where(
            Supplier_Product.supplier_id == supplier_id
        )
        await session.execute(delete_products_stmt)
        
        delete_supplier_stmt = delete(Supplier).where(
            Supplier.id == supplier_id
        )
        result = await session.execute(delete_supplier_stmt)
        
        if result.rowcount == 0:
            raise SupplierException.error_while_delete_supplier()
        
    
    async def soft_delete(self, supplier_id: str, session: AsyncSession):
        now = datetime.now()
        
        update_supplier = update(Supplier).where(
            Supplier.id == supplier_id
        ).values(
            is_active=False,
            updated_at=now
        )
        await session.execute(update_supplier)
        
        update_products = update(Supplier_Product).where(
            Supplier_Product.supplier_id == supplier_id
        ).values(
            is_active=False,
            updated_at=now
        )
        await session.execute(update_products)