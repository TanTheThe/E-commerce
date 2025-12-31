from src.errors.goods_receipt import GoodsReceiptException
from src.errors.purchase_order import PurchaseOrderException
from src.errors.supplier import SupplierException
from src.errors.warehouse import WareHouseException


class ApproveGRValidationService:
    def validate_gr_exists(self, gr):
        if not gr:
            GoodsReceiptException.gr_not_found()

    def validate_gr_status_pending(self, gr):
        if gr.status != "pending":
            raise GoodsReceiptException.only_approved_when_pending()

    def validate_po_exists(self, gr):
        if not gr.purchase_order:
            PurchaseOrderException.po_not_found()

    def validate_warehouse_active(self, gr):
        if not gr.warehouse:
            WareHouseException.warehouse_not_found()

        if not gr.warehouse.is_active:
            WareHouseException.warehouse_already_inactive()

    def validate_supplier_active(self, gr):
        if not gr.supplier:
            SupplierException.supplier_not_found()

        if not gr.supplier.is_active:
            SupplierException.supplier_not_active()

    def validate_has_receipt_details(self, gr):
        if not gr.receipt_details or len(gr.receipt_details) == 0:
            GoodsReceiptException.gr_has_no_items()

    def validate_all_accepted_positive(self, gr):
        has_accepted = any(
            detail.accepted_quantity > 0
            for detail in gr.receipt_details
        )

        if not has_accepted:
            GoodsReceiptException.gr_has_no_accepted_items()