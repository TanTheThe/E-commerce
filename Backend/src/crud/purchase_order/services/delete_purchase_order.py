from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.goods_receipt.repositories import GoodsReceiptRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.user.repositories import UserRepository
from src.database.models import PurchaseOrder, GoodsReceipt, SupplierPayment
from src.errors.purchase_order import PurchaseOrderException


purchase_order_repository = PurchaseOrderRepository()
user_repository = UserRepository()
goods_receipt_repository = GoodsReceiptRepository()
supplier_repository = SupplierRepository()

class DeletePurchaseOrderService:
    async def delete_purchase_order(self, po_id: str, session: AsyncSession):
        condition = [PurchaseOrder.id == po_id]
        po = await purchase_order_repository.get_purchase_order(session=session, where_conditions=condition)
        if not po:
            PurchaseOrderException.po_not_found()

        if po.status != "draft":
            PurchaseOrderException.only_draft_can_delete()

        condition_receipts = [GoodsReceipt.purchase_order_id == po_id]
        has_receipts = await goods_receipt_repository.get_goods_receipt(session=session, where_conditions=condition_receipts)
        if has_receipts:
            PurchaseOrderException.cant_delete_po_has_goods_receipts()

        condition_payment = [SupplierPayment.purchase_order_id == po_id]
        has_payments = await supplier_repository.get_supplier_payment(session=session, where_conditions=condition_payment)
        if has_payments:
            PurchaseOrderException.cant_delete_po_has_payment()

        success = await purchase_order_repository.delete_purchase_order(po_id=po_id, session=session)
        if not success:
            PurchaseOrderException.error_while_delete_po()




