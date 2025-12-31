from typing import List, Dict
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.database.models import GoodsReceipt, PurchaseOrder, Product_Variant
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.product import ProductException
from src.errors.purchase_order import PurchaseOrderException
from src.errors.supplier import SupplierException
from src.errors.warehouse import WareHouseException
from src.schemas.goods_receipt import ReceiptDetailUpdate

goods_receipt_repository = GoodsReceiptRepository()
product_variant_repository = ProductVariantRepository()

class UpdateGRValidationService:
    async def validate_gr_for_update(self, goods_receipt_id: str, session: AsyncSession):
        conditions = [GoodsReceipt.id == goods_receipt_id]
        options = [
            selectinload(GoodsReceipt.purchase_order).selectinload(PurchaseOrder.po_details),
            selectinload(GoodsReceipt.warehouse),
            selectinload(GoodsReceipt.supplier),
            selectinload(GoodsReceipt.receipt_details)
        ]

        gr = await goods_receipt_repository.get_goods_receipt(
            session=session,
            where_conditions=conditions,
            options=options
        )

        if not gr:
            GoodsReceiptException.gr_not_found()

        if gr.status != "pending":
            GoodsReceiptException.can_only_update_pending()

        if not gr.warehouse or not gr.warehouse.is_active:
            WareHouseException.warehouse_already_inactive()

        if not gr.supplier or not gr.supplier.is_active:
            SupplierException.supplier_not_active()

        if not gr.purchase_order:
            PurchaseOrderException.po_not_found()

        return gr

    async def validate_receipt_details(self, details_data: List[ReceiptDetailUpdate], gr, session: AsyncSession):
        po = gr.purchase_order
        po_details_map = {str(d.id): d for d in po.po_details}

        for detail in details_data:
            if detail.po_detail_id not in po_details_map:
                PurchaseOrderException.po_detail_not_exist()

        variant_ids = [d.product_variant_id for d in details_data]
        variants_map = await self.batch_load_variants(variant_ids, session)

        missing_variants = [vid for vid in variant_ids if vid not in variants_map]
        if missing_variants:
            ProductException.not_found_variant()

        for detail in details_data:
            po_detail = po_details_map[detail.po_detail_id]
            if str(po_detail.product_variant_id) != detail.product_variant_id:
                PurchaseOrderException.variant_not_match()

        return variants_map, po_details_map

    async def batch_load_variants(self, variant_ids: List[str], session: AsyncSession) -> Dict[str, any]:
        conditions = [Product_Variant.id.in_(variant_ids)]
        options = [
            selectinload(Product_Variant.product),
            selectinload(Product_Variant.color)
        ]

        variants, _ = await product_variant_repository.get_all_product_variant(
            session=session,
            where_conditions=conditions,
            options=options
        )

        return {str(v.id): v for v in variants}