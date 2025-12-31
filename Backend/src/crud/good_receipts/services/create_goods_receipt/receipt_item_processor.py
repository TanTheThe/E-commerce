from typing import Dict, List

from src.crud.good_receipts.services.create_goods_receipt.discrepancy import DiscrepancyService
from src.crud.good_receipts.services.create_goods_receipt.goods_receipt_data_loader import GoodsReceiptDataLoaderService
from src.crud.good_receipts.services.create_goods_receipt.quantity_validation import QuantityValidationService
from src.crud.good_receipts.services.create_goods_receipt.receipt_detail_builder import ReceiptDetailBuilderService
from src.errors.product import ProductException
from src.errors.purchase_order import PurchaseOrderException
from src.schemas.goods_receipt import GoodsReceiptDetailCreate
from sqlmodel.ext.asyncio.session import AsyncSession


data_loader_service = GoodsReceiptDataLoaderService()
discrepancy_service = DiscrepancyService()
quantity_validation_service = QuantityValidationService()
receipt_detail_builder_service =ReceiptDetailBuilderService()

class ReceiptItemProcessorService:
    async def process_receipt_items(self, items: List[GoodsReceiptDetailCreate], purchase_order: any, 
                                    parent_details_map: Dict, session: AsyncSession, parent_receipt_id: str = None):
        po_details_map = {str(detail.id): detail for detail in purchase_order.po_details}
        
        missing_po_details = [
            item.po_detail_id for item in items 
            if item.po_detail_id not in po_details_map
        ]
        if missing_po_details:
            PurchaseOrderException.po_detail_not_exist()
            
        variants_map = await self.load_and_validate_variants(items, session)
        
        sibling_grs = None
        if parent_receipt_id:
            sibling_grs = await data_loader_service.batch_load_sibling_receipts(parent_receipt_id, session)
            
        receipt_details = []
        total_received_amount = 0
        discrepancy_notes_list = []
        
        for item in items:
            receipt_detail, item_discrepancies = self.process_single_item(
                item,
                po_details_map[item.po_detail_id],
                variants_map[item.product_variant_id],
                parent_details_map,
                sibling_grs
            )
            
            receipt_details.append(receipt_detail)
            total_received_amount += receipt_detail.total_cost
            
            if item_discrepancies:
                discrepancy_notes_list.extend(item_discrepancies)
                
        has_discrepancy, discrepancy_notes = discrepancy_service.aggregate_discrepancies(discrepancy_notes_list)

        return receipt_details, total_received_amount, has_discrepancy, discrepancy_notes
    
            
    async def load_and_validate_variants(self, items: List[GoodsReceiptDetailCreate], session: AsyncSession):
        variant_ids = [item.product_variant_id for item in items]
        variants_map = await data_loader_service.batch_load_variants(variant_ids, session)
        
        missing_variants = [vid for vid in variant_ids if vid not in variants_map]
        if missing_variants:
            ProductException.not_found_variant()
        
        return variants_map
    
    
    def process_single_item(self, item: GoodsReceiptDetailCreate, po_detail: any, variant: any, 
                            parent_details_map: Dict, sibling_grs: List):
        if str(po_detail.product_variant_id) != item.product_variant_id:
            PurchaseOrderException.variant_not_match()
            
        if parent_details_map:
            quantity_validation_service.validate_ordered_quantity_for_parent_receipt(item, parent_details_map, sibling_grs)
        else:
            quantity_validation_service.validate_ordered_quantity_for_po(item, po_detail)
        
        item_discrepancies = discrepancy_service.check_item_discrepancies(item, variant)
        
        receipt_detail = receipt_detail_builder_service.create_receipt_detail(item, po_detail, variant)
        
        return receipt_detail, item_discrepancies
        
        