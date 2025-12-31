from datetime import datetime
from typing import List
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.good_receipts.services.create_goods_receipt.goods_receipt_validation import GoodsReceiptValidationService
from src.crud.good_receipts.services.create_goods_receipt.receipt_item_processor import ReceiptItemProcessorService
from src.database.models import GoodsReceipt, GoodsReceiptDetail
from src.schemas.goods_receipt import CreateGoodsReceiptRequest
from sqlmodel.ext.asyncio.session import AsyncSession


validation_service = GoodsReceiptValidationService()
item_processor_service = ReceiptItemProcessorService()
goods_receipt_repository = GoodsReceiptRepository()

class CreateGoodsReceiptService:
    async def create_goods_receipt(self, request: CreateGoodsReceiptRequest, created_by: str, session: AsyncSession):
        validation_service.validate_request_data(request)
        
        await validation_service.validate_supplier(request.supplier_id, session)
        
        await validation_service.validate_warehouse(request.warehouse_id, session)
        
        purchase_order = await validation_service.validate_purchase_order(
            request.purchase_order_id,
            request.supplier_id,
            request.warehouse_id,
            session
        )
        
        parent_receipt = None
        parent_details_map = {}

        if request.parent_receipt_id:
            parent_receipt, parent_details_map = await validation_service.validate_and_load_parent_receipt(
                request.parent_receipt_id,
                request.purchase_order_id,
                session
            )
            
        receipt_details, total_received_amount, has_discrepancy, discrepancy_notes = \
            await item_processor_service.process_receipt_items(
                request.items,
                purchase_order,
                parent_details_map,
                session,
                request.parent_receipt_id
            )
            
        created_gr = await self.create_and_save_receipt(
            request,
            created_by,
            total_received_amount,
            has_discrepancy,
            discrepancy_notes,
            receipt_details,
            session
        )
        
        return {
            "id": str(created_gr.id),
            "receipt_number": created_gr.receipt_number,
            "purchase_order_id": str(created_gr.purchase_order_id),
            "purchase_order_number": created_gr.purchase_order.po_number if created_gr.purchase_order else None,
            "parent_receipt_id": str(created_gr.parent_receipt_id) if created_gr.parent_receipt_id else None,
            "supplier_id": str(created_gr.supplier_id),
            "supplier_name": created_gr.supplier.name if created_gr.supplier else None,
            "warehouse_id": str(created_gr.warehouse_id),
            "warehouse_name": created_gr.warehouse.name if created_gr.warehouse else None,
            "status": created_gr.status,
            "receipt_date": created_gr.receipt_date.isoformat(),
            "total_received_amount": created_gr.total_received_amount,
            "has_discrepancy": created_gr.has_discrepancy,
            "discrepancy_notes": created_gr.discrepancy_notes,
            "created_at": created_gr.created_at.isoformat()
        }
        
        
    async def create_and_save_receipt(self, request: CreateGoodsReceiptRequest, created_by: str, total_received_amount: int,
                                      has_discrepancy: bool, discrepancy_notes: str, 
                                      receipt_details: List[GoodsReceiptDetail], session: AsyncSession):
        receipt_number = await goods_receipt_repository.generate_gr_number(session=session)

        goods_receipt = GoodsReceipt(
            receipt_number=receipt_number,
            purchase_order_id=request.purchase_order_id,
            parent_receipt_id=request.parent_receipt_id,
            warehouse_id=request.warehouse_id,
            supplier_id=request.supplier_id,
            status="pending",
            receipt_date=request.receipt_date,
            delivery_note_number=request.delivery_note_number,
            total_received_amount=total_received_amount,
            received_by=created_by,
            received_at=datetime.now(),
            has_discrepancy=has_discrepancy,
            discrepancy_notes=discrepancy_notes,
            notes=request.notes,
            created_at=datetime.now()
        )

        created_gr = await goods_receipt_repository.create_goods_receipt(
            goods_receipt,
            receipt_details,
            session
        )

        return created_gr