from typing import List
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import GoodsReceipt, PurchaseOrder, Supplier, Warehouse
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.purchase_order import PurchaseOrderException
from src.errors.supplier import SupplierException
from src.errors.warehouse import WareHouseException
from src.schemas.goods_receipt import CreateGoodsReceiptRequest, GoodsReceiptDetailCreate
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload


purchase_order_repository = PurchaseOrderRepository()
supplier_repository = SupplierRepository()
warehouse_repository = WareHouseRepository()
goods_receipt_repository = GoodsReceiptRepository()


class GoodsReceiptValidationService:
    def validate_request_data(self, request: CreateGoodsReceiptRequest):
        pass

    async def validate_purchase_order(self, po_id: str, supplier_id: str, warehouse_id: str, session: AsyncSession):
        condition_po = [PurchaseOrder.id == po_id]
        
        options_po = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse),
            selectinload(PurchaseOrder.po_details)
        ]
        
        purchase_order = await purchase_order_repository.get_purchase_order(
            session=session,
            where_conditions=condition_po,
            options=options_po
        )
        
        if not purchase_order:
            PurchaseOrderException.po_not_found()
        
        if purchase_order.status not in ["confirmed", "partial_received"]:
            PurchaseOrderException.invalid_status_for_receipt()
            
        if str(purchase_order.supplier.id) != supplier_id:
            SupplierException.supplier_not_match_with_po()
            
        if str(purchase_order.warehouse_id) != warehouse_id:
            WareHouseException.warehouse_not_match_with_po()
            
        return purchase_order
    
    
    async def validate_supplier(self, supplier_id: str, session: AsyncSession):
        condition_supplier = [Supplier.id == supplier_id]
        
        supplier = await supplier_repository.get_supplier(
            session=session,
            where_conditions=condition_supplier
        )
        
        if not supplier:
            SupplierException.supplier_not_found()
            
        if not supplier.is_active:
            SupplierException.supplier_not_active()
            
        return supplier
    
    
    async def validate_warehouse(self, warehouse_id: str, session: AsyncSession):
        condition_warehouse = [Warehouse.id == warehouse_id]
        warehouse = await warehouse_repository.get_warehouse(
            session=session,
            conditions=condition_warehouse
        )
        
        if not warehouse:
            WareHouseException.warehouse_not_found()
            
        if not warehouse.is_active:
            WareHouseException.warehouse_already_inactive()
            
        return warehouse
    
    
    async def validate_and_load_parent_receipt(self, parent_receipt_id: str, purchase_order_id: str, session: AsyncSession):
        condition_parent = [GoodsReceipt.id == parent_receipt_id]
        options_parent = [selectinload(GoodsReceipt.receipt_details)]

        parent_receipt = await goods_receipt_repository.get_goods_receipt(
            session=session,
            where_conditions=condition_parent,
            options=options_parent
        )
        
        if not parent_receipt:
            GoodsReceiptException.gr_parent_not_exist()
            
        if not parent_receipt.has_discrepancy:
            GoodsReceiptException.gr_parent_must_have_discrepancy()
            
        if str(parent_receipt.purchase_order_id) != purchase_order_id:
            GoodsReceiptException.gr_child_must_same_po_with_parent()

        parent_details_map = {
            str(detail.po_detail_id): detail
            for detail in parent_receipt.receipt_details
        }

        return parent_receipt, parent_details_map
        
        
        