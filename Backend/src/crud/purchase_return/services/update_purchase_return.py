from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import delete
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_return.services.utils_service import UtilsPRService
from src.database.models import GoodsReceipt, GoodsReceiptDetail, Product_Variant, PurchaseReturn, PurchaseReturnDetail
from sqlalchemy.orm import selectinload
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.product import ProductException
from src.errors.purchase_return import PurchaseReturnException
import logging

logger = logging.getLogger(__name__)

utils_pr_service = UtilsPRService()
product_variant_repository = ProductVariantRepository()
goods_receipt_repository = GoodsReceiptRepository()

class UpdatePurchaseReturnService:
    async def update_purchase_return(self, session: AsyncSession, purchase_return_id: str, update_data: Dict[str, Any]):
        pr = await self.validate_and_get_pr(session, purchase_return_id)
        
        try:
            if "return_date" in update_data:
                pr.return_date = update_data["return_date"]

            if "return_type" in update_data:
                pr.return_type = update_data["return_type"]

            if "return_reason" in update_data:
                pr.return_reason = update_data["return_reason"]

            if "delivery_note_number" in update_data:
                pr.delivery_note_number = update_data["delivery_note_number"]

            if "refund_amount" in update_data:
                refund_amount = update_data["refund_amount"]

                if refund_amount > pr.total_return_amount:
                    PurchaseReturnException.refund_amount_exceed_total_return(refund_amount, pr.total_return_amount)

            if "notes" in update_data:
                pr.notes = update_data["notes"]

            if "return_details" in update_data:
                await self.update_return_details(
                    session=session,
                    pr=pr,
                    details_data=update_data["return_details"]
                )

            total_return_amount = sum(d.total_cost for d in pr.return_details)
            pr.total_return_amount = total_return_amount
            
            if pr.refund_amount and pr.refund_amount > total_return_amount:
                PurchaseReturnException.refund_amount_exceeds_new_total_refund(pr.refund_amount)

            pr.updated_at = datetime.now()

            session.add(pr)
            await session.commit()
            await session.refresh(pr)

            return {
                "id": str(pr.id),
                "return_number": pr.return_number,
                "status": pr.status,
                "total_return_amount": pr.total_return_amount,
                "refund_amount": pr.refund_amount,
                "total_items": len(pr.return_details),
                "updated_at": pr.updated_at.isoformat()
            }
            
        except Exception as e:
            await session.rollback()
            logger.error("Error update purchase return: ", e)
            PurchaseReturnException.error_while_update_pr()


    async def update_return_details(self, session: AsyncSession, pr: PurchaseReturn, details_data: List[Dict[str, Any]]):
        existing_details_map = {str(d.id): d for d in pr.return_details}
        updated_detail_ids = set()
        
        variant_ids = list(set(d["product_variant_id"] for d in details_data))
        gr_detail_ids = list(set(
            d["goods_receipt_detail_id"] 
            for d in details_data 
            if d.get("goods_receipt_detail_id")
        ))
        
        variants_map = await self.batch_validate_variants(session, variant_ids)
        
        if gr_detail_ids:
            gr_details_map = await self.batch_validate_gr_details(
                session, pr.goods_receipt_id, gr_detail_ids
            )
        else:
            gr_details_map = {}

        for detail_data in details_data:
            detail_id = detail_data.get("id")
            variant_id = detail_data["product_variant_id"]
            gr_detail_id = detail_data.get("goods_receipt_detail_id")
            return_qty = detail_data["return_quantity"]
            unit_cost = detail_data["unit_cost"]
            
            variant = variants_map.get(variant_id)
            if not variant:
                ProductException.not_found_variant()
                
            if gr_detail_id:
                gr_detail = gr_details_map.get(gr_detail_id)
                if not gr_detail:
                    GoodsReceiptException.gr_detail_not_found()

                await self.validate_returnable_quantity(
                    session=session,
                    gr_detail=gr_detail,
                    return_quantity=return_qty,
                    current_detail_id=detail_id 
                )
                
            total_cost = return_qty * unit_cost
            
            product_snapshot = {
                "product_id": str(variant.product.id) if variant.product else None,
                "variant_id": str(variant.id),
                "sku": variant.sku,
                "name": variant.product.name if variant.product else None,
                "unit_cost": unit_cost,
                "size": variant.size,
                "color_name": variant.color_name if variant.color_name else (
                    variant.color.name if variant.color else None
                ),
                "variant_image": variant.image
            }

            if detail_id and detail_id in existing_details_map:
                detail = existing_details_map[detail_id]
                
                detail.product_variant_id = variant_id
                detail.goods_receipt_detail_id = gr_detail_id
                detail.return_quantity = return_qty
                detail.unit_cost = unit_cost
                detail.total_cost = total_cost
                detail.condition = detail_data.get("condition", "damaged")
                detail.rejection_evidence = detail_data.get("rejection_evidence")
                detail.notes = detail_data.get("notes")
                detail.product_snapshot = product_snapshot

                session.add(detail)
                updated_detail_ids.add(detail_id)
            else:
                new_detail = PurchaseReturnDetail(
                    purchase_return_id=pr.id,
                    product_variant_id=variant_id,
                    goods_receipt_detail_id=gr_detail_id,
                    return_quantity=return_qty,
                    unit_cost=unit_cost,
                    total_cost=total_cost,
                    condition=detail_data.get("condition", "damaged"),
                    rejection_evidence=detail_data.get("rejection_evidence"),
                    notes=detail_data.get("notes"),
                    product_snapshot=product_snapshot,
                    created_at=datetime.now()
                )
                session.add(new_detail)
                pr.return_details.append(new_detail)

        details_to_delete = set(existing_details_map.keys()) - updated_detail_ids
        if details_to_delete:
            await session.execute(
                delete(PurchaseReturnDetail)
                .where(PurchaseReturnDetail.id.in_(details_to_delete))
            )

        await session.flush()


    async def validate_and_get_pr(self, session: AsyncSession, purchase_return_id: str):
        pr = await utils_pr_service.validate_and_get_pr(
            session, 
            purchase_return_id,
        )
        
        if pr.status != 'draft':
            PurchaseReturnException.only_update_when_draft()
            
        if pr.shipped_date:
            PurchaseReturnException.cant_update_return_shipped()
            
        if pr.approved_at:
            PurchaseReturnException.cant_update_return_approved()
            
        return pr
    
    
    async def batch_validate_variants(self, session: AsyncSession, variant_ids: List[str]) -> Dict[str, Product_Variant]:
        conditions = [Product_Variant.id.in_(variant_ids)]
        options = [
            selectinload(Product_Variant.product),
            selectinload(Product_Variant.color)
        ]
        
        variants, _ = await product_variant_repository.get_all_product_variant(session=session, where_conditions=conditions,
                                                                               options=options)
        
        found_ids = {str(v.id) for v in variants}
        missing_ids = set(variant_ids) - found_ids
        if missing_ids:
            ProductException.not_found_variant()
            
        return {str(v.id): v for v in variants}
    
    
    async def batch_validate_gr_details(self, session: AsyncSession, goods_receipt_id: str, gr_detail_ids: List[str]):
        conditions = [
            GoodsReceiptDetail.id.in_(gr_detail_ids),
            GoodsReceiptDetail.goods_receipt_id == goods_receipt_id
        ]
        
        gr_details, _ = await goods_receipt_repository.get_all_goods_receipt_detail(session=session, where_conditions=conditions)
        
        found_ids = {str(d.id) for d in gr_details}
        missing_ids = set(gr_detail_ids) - found_ids
        if missing_ids:
            GoodsReceiptException.gr_detail_not_found()
            
        return {str(d.id): d for d in gr_details}
    

    async def validate_returnable_quantity(self, session: AsyncSession, gr_detail: GoodsReceiptDetail, 
                                           return_quantity: int, current_detail_id: Optional[str] = None):
        already_returned = await utils_pr_service.get_already_returned_quantity(
            session=session,
            gr_detail_id=str(gr_detail.id),
            include_draft=True,
            exclude_detail_id=current_detail_id
        )
        
        max_returnable = gr_detail.accepted_quantity - already_returned

        if return_quantity > max_returnable:
            PurchaseReturnException.number_refunds_exceed_refund_available(
                return_quantity, max_returnable, already_returned, gr_detail.accepted_quantity
            )
        
        
            
        








