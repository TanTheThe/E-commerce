from typing import Dict, List
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.purchase_order import PurchaseOrderException
from src.schemas.goods_receipt import GoodsReceiptDetailCreate


class QuantityValidationService:
    def calculate_sibling_received_quantities(self, sibling_grs: List, po_detail_id: str):
        total = 0
        for sibling_gr in sibling_grs:
            for sibling_detail in sibling_gr.receipt_details:
                if str(sibling_detail.po_detail_id) == po_detail_id:
                    total += sibling_detail.received_quantity
        return total
    
    
    def validate_ordered_quantity_for_parent_receipt(self, item: GoodsReceiptDetailCreate, 
                                                     parent_details_map: Dict, sibling_grs: List = None):
        parent_detail = parent_details_map.get(item.po_detail_id)

        if not parent_detail:
            GoodsReceiptException.po_detail_not_exist_in_parent_receipt()
            
        expected_qty = parent_detail.rejected_quantity
        
        if sibling_grs:
            sibling_received = self.calculate_sibling_received_quantities(
                sibling_grs, 
                item.po_detail_id
            )
            expected_qty -= sibling_received
            
        expected_qty = max(0, expected_qty)

        if item.ordered_quantity != expected_qty:
            GoodsReceiptException.ordered_quantity_must_equal_expected_qty(expected_qty)
            
            
    def validate_ordered_quantity_for_po(self, item: GoodsReceiptDetailCreate, po_detail: any):
        if item.ordered_quantity != po_detail.quantity:
            raise PurchaseOrderException.order_quantity_not_equal_po_detail()