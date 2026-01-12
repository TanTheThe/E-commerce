from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import and_, select
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.purchase_return.services.utils_service import UtilsPRService
from src.database.models import GoodsReceipt, Product_Variant, PurchaseReturn, PurchaseReturnDetail
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.product import ProductException
from src.errors.purchase_return import PurchaseReturnException
import logging

logger = logging.getLogger(__name__)


goods_receipt_repository = GoodsReceiptRepository()
purchase_return_repository = PurchaseReturnRepository()
product_variant_repository = ProductVariantRepository()
utils_pr_service = UtilsPRService()


class CreatePurchaseReturnService:
    async def create_return_from_goods_receipt(self, session: AsyncSession, goods_receipt_id: str, return_items: List[Dict],
                                               return_reason: str, return_type: str = "exchange", created_by: str = None,
                                               notes: Optional[str] = None):
        try:
            gr = await self.validate_and_get_gr(session, goods_receipt_id)
            validated_items = await self.validate_return_items(session, gr, return_items)

            return_number = await purchase_return_repository.generate_return_number(session)
            total_return_amount = sum(item['total_cost'] for item in validated_items)

            pr_data = {
                "return_number": return_number,
                "purchase_order_id": str(gr.purchase_order_id),
                "goods_receipt_id": goods_receipt_id,
                "supplier_id": str(gr.supplier_id),
                "warehouse_id": str(gr.warehouse_id),
                "status": "draft",
                "return_type": return_type,
                "return_date": datetime.now(),
                "total_return_amount": total_return_amount,
                "refund_amount": 0,
                "return_reason": return_reason,
                "created_by": created_by,
                "notes": notes,
                "created_at": datetime.now(),
            }

            pr = await purchase_return_repository.create_purchase_return(session=session, pr_data=pr_data)

            pr_details = []
            for item in validated_items:
                detail_data = {
                    "purchase_return_id": str(pr.id),
                    "product_variant_id": str(item['product_variant_id']),
                    "goods_receipt_detail_id": str(item['gr_detail_id']),
                    "return_quantity": item['return_quantity'],
                    "unit_cost": item['unit_cost'],
                    "total_cost": item['total_cost'],
                    "condition": item['condition'],
                    "rejection_evidence": item.get('rejection_evidence'),
                    "product_snapshot": item['product_snapshot'],
                    "notes": item.get('notes'),
                    "created_at": datetime.now(),
                }

                detail = await purchase_return_repository.create_purchase_return_detail(
                    session=session,
                    detail_data=detail_data
                )
                pr_details.append(detail)

            await session.commit()

            return {
                "id": str(pr.id),
                "return_number": pr.return_number,
                "status": pr.status,
                "goods_receipt": {
                    "id": str(gr.id),
                    "receipt_number": gr.receipt_number
                },
                "purchase_order": {
                    "id": str(gr.purchase_order_id),
                    "po_number": gr.purchase_order.po_number if gr.purchase_order else None
                },
                "supplier": {
                    "id": str(gr.supplier_id),
                    "name": gr.supplier.name if gr.supplier else None
                },
                "total_return_amount": total_return_amount,
                "total_items": len(pr_details),
                "return_items": [
                    {
                        "product_variant_id": str(d.product_variant_id),
                        "return_quantity": d.return_quantity,
                        "unit_cost": d.unit_cost,
                        "total_cost": d.total_cost,
                        "condition": d.condition
                    }
                    for d in pr_details
                ],
                "created_at": pr.created_at.isoformat()
            }
        except Exception as e:
            await session.rollback()
            logger.error("Error create purchase return: ", e)
            PurchaseReturnException.error_while_create_pr()
            

    async def validate_and_get_gr(self, session: AsyncSession, goods_receipt_id: str):
        condition = [GoodsReceipt.id == goods_receipt_id]
        options = [
            selectinload(GoodsReceipt.purchase_order),
            selectinload(GoodsReceipt.supplier),
            selectinload(GoodsReceipt.warehouse),
            selectinload(GoodsReceipt.receipt_details)
        ]

        gr = await goods_receipt_repository.get_goods_receipt(
            session=session,
            where_conditions=condition,
            options=options
        )

        if not gr:
            GoodsReceiptException.gr_not_found()

        if gr.status not in ['approved', 'has_issue', 'completed']:
            PurchaseReturnException.required_to_create()

        return gr


    async def validate_return_items(self, session: AsyncSession, gr: GoodsReceipt, return_items: List[Dict]):
        validated_items = []
        gr_details_map = {str(d.id): d for d in gr.receipt_details}

        variant_ids = list(set(str(d.product_variant_id) for d in gr.receipt_details))
        
        condition_variants = [Product_Variant.id.in_(variant_ids)]
        options = [selectinload(Product_Variant.product), selectinload(Product_Variant.color)]
        variants, _ = await product_variant_repository.get_all_product_variant(
            session=session, 
            where_conditions=condition_variants, 
            options=options
        )
        
        variants_map = {str(v.id): v for v in variants}
        
        gr_detail_ids = [item['gr_detail_id'] for item in return_items]
        already_returned_map = await utils_pr_service.get_already_returned_quantities_batch(
            session, gr_detail_ids, include_draft=True
        )

        for item in return_items:
            gr_detail_id = item['gr_detail_id']
            return_quantity = item['return_quantity']

            gr_detail = gr_details_map.get(gr_detail_id)
            if not gr_detail:
                GoodsReceiptException.gr_detail_not_found()

            if return_quantity <= 0:
                PurchaseReturnException.return_quantity_must_greater_than_0()

            already_returned = already_returned_map.get(gr_detail_id, 0)
            max_returnable = gr_detail.accepted_quantity - already_returned

            if return_quantity > max_returnable:
                PurchaseReturnException.return_quantity_greater_than_max_returnable()

            variant = variants_map.get(str(gr_detail.product_variant_id))
            if not variant:
                ProductException.not_found_variant()

            validated_items.append({
                "gr_detail_id": gr_detail_id,
                "product_variant_id": str(gr_detail.product_variant_id),
                "return_quantity": return_quantity,
                "unit_cost": gr_detail.unit_cost,
                "total_cost": return_quantity * gr_detail.unit_cost,
                "condition": item.get('condition', 'damaged'),
                "rejection_evidence": item.get('rejection_evidence'),
                "notes": item.get('notes'),
                "product_snapshot": {
                    "product_id": str(variant.product.id) if variant and variant.product else None,
                    "variant_id": str(variant.id),
                    "sku": variant.sku if variant else None,
                    "name": variant.product.name if variant and variant.product else None,
                    "unit_cost": gr_detail.unit_cost,
                    "size": variant.size,
                    "color_name": variant.color_name if variant.color_name else variant.color.name,
                    "variant_image": variant.image
                }
            })

        return validated_items










