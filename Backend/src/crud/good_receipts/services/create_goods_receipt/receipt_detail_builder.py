from datetime import datetime
from src.database.models import GoodsReceiptDetail
from src.schemas.goods_receipt import GoodsReceiptDetailCreate


class ReceiptDetailBuilderService:
    def create_receipt_detail(self, item: GoodsReceiptDetailCreate, po_detail: any, variant: any):
        unit_cost = po_detail.unit_cost
        total_cost = item.accepted_quantity * unit_cost
        
        product_snapshot = self.create_product_snapshot(variant, unit_cost)
        
        return GoodsReceiptDetail(
            product_variant_id=item.product_variant_id,
            po_detail_id=item.po_detail_id,
            ordered_quantity=item.ordered_quantity,
            received_quantity=item.received_quantity,
            accepted_quantity=item.accepted_quantity,
            rejected_quantity=item.rejected_quantity,
            unit_cost=unit_cost,
            total_cost=total_cost,
            rejection_reason=item.rejection_reason,
            product_snapshot=product_snapshot,
            notes=item.notes,
            created_at=datetime.now()
        )
        
    
    def create_product_snapshot(self, variant: any, unit_cost: int):
        return {
            "product_name": variant.product.name if variant.product else None,
            "variant_sku": variant.sku,
            "variant_size": variant.size,
            "variant_color_name": variant.color_name if variant.color_name else (
                variant.color.name if variant.color else None
            ),
            "variant_color_code": variant.color_code if variant.color_code else (
                variant.color.code if variant.color else None
            ),
            "variant_image": variant.image,
            "variant_price": variant.price,
            "unit_cost": unit_cost,
            "snapshot_date": datetime.now().isoformat()
        }