from sqlalchemy.orm import selectinload
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.user.repositories import UserRepository
from src.database.models import GoodsReceipt, GoodsReceiptDetail, PurchaseOrder, Product_Variant, User
from src.errors.goods_receipt import GoodsReceiptException


goods_receipt_repository = GoodsReceiptRepository()
user_repository = UserRepository()


class GetGRForCreateService:
    async def get_goods_receipt_for_create(self, parent_gr_id: str, session: AsyncSession):
        condition_gr = [GoodsReceipt.id == parent_gr_id]
    
        options = [
            selectinload(GoodsReceipt.receipt_details).selectinload(GoodsReceiptDetail.product_variant).selectinload(
                Product_Variant.product),
            selectinload(GoodsReceipt.receipt_details).selectinload(GoodsReceiptDetail.product_variant).selectinload(
                Product_Variant.color),
        ]
        
        parent_gr = await goods_receipt_repository.get_goods_receipt(
            session=session, 
            where_conditions=condition_gr,
            options=options
        )
        
        if not parent_gr:
            GoodsReceiptException.gr_not_found()

        adjusted_ordered_quantities = {}
    
        child_condition = [GoodsReceipt.parent_receipt_id == parent_gr_id]
        child_options = [selectinload(GoodsReceipt.receipt_details)]
        
        child_grs, _ = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=child_condition,
            options=child_options
        )

        for parent_detail in parent_gr.receipt_details:
            variant_id = parent_detail.product_variant_id
            
            available_qty = parent_detail.rejected_quantity
            
            for child_gr in child_grs:
                for child_detail in child_gr.receipt_details:
                    if child_detail.product_variant_id == variant_id:
                        available_qty -= child_detail.received_quantity
            
            adjusted_ordered_quantities[variant_id] = max(0, available_qty)

        items = []
        for detail in parent_gr.receipt_details:
            if detail.rejected_quantity <= 0:
                continue
                
            if detail.product_snapshot:
                product_name = detail.product_snapshot.get("product_name")
                variant_size = detail.product_snapshot.get("variant_size")
                variant_color_name = detail.product_snapshot.get("variant_color_name")
            else:
                product_name = detail.product_variant.product.name if detail.product_variant and detail.product_variant.product else None
                variant_size = detail.product_variant.size if detail.product_variant else None
                
                variant_color_name = None
                if detail.product_variant:
                    if detail.product_variant.color_name:
                        variant_color_name = detail.product_variant.color_name
                    elif detail.product_variant.color:
                        variant_color_name = detail.product_variant.color.name
            
            ordered_qty = adjusted_ordered_quantities.get(detail.product_variant_id, 0)
                
            items.append({
                "product_variant_id": str(detail.product_variant_id),
                "product_name": product_name,
                "variant_size": variant_size,
                "variant_color_name": variant_color_name,
                "ordered_quantity": ordered_qty,
            })
        
        return {
            "parent_receipt_id": str(parent_gr.id),
            "parent_receipt_number": parent_gr.receipt_number,
            "items": items
        }
