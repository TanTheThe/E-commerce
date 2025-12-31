from typing import List
from src.schemas.goods_receipt import GoodsReceiptDetailCreate

class DiscrepancyService:
    def check_item_discrepancies(self, item: GoodsReceiptDetailCreate, variant: any):
        discrepancies = []
        
        if item.received_quantity != item.ordered_quantity:
            discrepancies.append(
                f"SKU {variant.sku}: Đặt {item.ordered_quantity}, nhận {item.received_quantity}"
            )
            
        if item.rejected_quantity > 0:
            discrepancies.append(
                f"SKU {variant.sku}: Từ chối {item.rejected_quantity} - "
                f"{item.rejection_reason or 'Không rõ lý do'}"
            )

        return discrepancies
    
    
    def aggregate_discrepancies(self, discrepancy_notes_list: List[str]):
        if not discrepancy_notes_list:
            return False, None
        
        return True, "; ".join(discrepancy_notes_list)