from sqlalchemy.orm import selectinload
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.user.repositories import UserRepository
from src.database.models import GoodsReceipt, GoodsReceiptDetail, Product_Variant, PurchaseOrderDetail, PurchaseOrder, \
    PurchaseReturn, User, PurchaseReturnDetail
from src.errors.purchase_order import PurchaseOrderException
from src.errors.purchase_return import PurchaseReturnException


purchase_return_repository = PurchaseReturnRepository()
user_repository = UserRepository()

class GetDetailPurchaseReturnService:
    async def get_purchase_return_by_id(self, pr_id: str, session: AsyncSession):
        condition_pr = [PurchaseReturn.id == pr_id]
        options = [
            selectinload(PurchaseReturn.supplier),
            selectinload(PurchaseReturn.warehouse),
            selectinload(PurchaseReturn.purchase_order),
            selectinload(PurchaseReturn.goods_receipt),
            selectinload(PurchaseReturn.return_details).selectinload(PurchaseReturnDetail.product_variant).selectinload(
                Product_Variant.product),
            selectinload(PurchaseReturn.return_details).selectinload(PurchaseReturnDetail.product_variant).selectinload(
                Product_Variant.color),
            selectinload(PurchaseReturn.return_details).selectinload(PurchaseReturnDetail.goods_receipt_detail)
        ]
        pr = await purchase_return_repository.get_purchase_return(session=session, where_conditions=condition_pr,
                                                                  options=options)
        if not pr:
            PurchaseReturnException.pr_not_found()

        created_by_name = None
        if pr.created_by:
            condition_user = and_(User.id == pr.created_by)
            creator = await user_repository.get_user(condition_user, session=session)
            if creator:
                created_by_name = f"{creator.first_name} {creator.last_name}"

        approved_by_name = None
        if pr.approved_by:
            condition_user = and_(User.id == pr.approved_by)
            approver = await user_repository.get_user(condition_user, session=session)
            if approver:
                approved_by_name = f"{approver.first_name} {approver.last_name}"

        items = []
        for detail in pr.return_details:
            if detail.product_snapshot:
                product_name = detail.product_snapshot.get("product_name")
                variant_sku = detail.product_snapshot.get("variant_sku")
                variant_size = detail.product_snapshot.get("variant_size")
                variant_color_name = detail.product_snapshot.get("variant_color_name")
                variant_image = detail.product_snapshot.get("variant_image")
            else:
                product_name = detail.product_variant.product.name if detail.product_variant and detail.product_variant.product else None
                variant_sku = detail.product_variant.sku if detail.product_variant else None
                variant_size = detail.product_variant.size if detail.product_variant else None

                variant_color_name = None
                variant_image = None
                if detail.product_variant:
                    if detail.product_variant.color_name:
                        variant_color_name = detail.product_variant.color_name
                    elif detail.product_variant.color:
                        variant_color_name = detail.product_variant.color.name
                    variant_image = detail.product_variant.image

            items.append(
                {
                    "id": str(detail.id),
                    "product_id": str(detail.product_variant.product_id),
                    "product_variant_id": str(detail.product_variant_id),
                    "goods_receipt_detail_id": str(
                        detail.goods_receipt_detail_id) if detail.goods_receipt_detail_id else None,
                    "product_name": product_name,
                    "variant_sku": variant_sku,
                    "variant_size": variant_size,
                    "variant_color_name": variant_color_name,
                    "variant_image": variant_image,
                    "return_quantity": detail.return_quantity,
                    "unit_cost": detail.unit_cost,
                    "total_cost": detail.total_cost,
                    "condition": detail.condition,
                    "rejection_evidence": detail.rejection_evidence,
                    "product_snapshot": detail.product_snapshot,
                    "notes": detail.notes,
                    "created_at": str(detail.created_at),
                }
            )

        return {
            "id": str(pr.id),
            "return_number": pr.return_number,
            "purchase_order_id": str(pr.purchase_order_id),
            "purchase_order_number": pr.purchase_order.po_number if pr.purchase_order else None,
            "goods_receipt_id": str(pr.goods_receipt_id) if pr.goods_receipt_id else None,
            "goods_receipt_number": pr.goods_receipt.receipt_number if pr.goods_receipt else None,
            "supplier_id": str(pr.supplier_id),
            "supplier_name": pr.supplier.name if pr.supplier else None,
            "supplier_code": pr.supplier.code if pr.supplier else None,
            "warehouse_id": str(pr.warehouse_id),
            "warehouse_name": pr.warehouse.name if pr.warehouse else None,
            "warehouse_code": pr.warehouse.code if pr.warehouse else None,
            "status": pr.status,
            "return_type": pr.return_type,
            "return_date": str(pr.return_date),
            "shipped_date": str(pr.shipped_date) if pr.shipped_date else None,
            "total_return_amount": pr.total_return_amount,
            "refund_amount": pr.refund_amount,
            "return_reason": pr.return_reason,
            "delivery_note_number": pr.delivery_note_number,
            "notes": pr.notes,
            "created_by": str(pr.created_by) if pr.created_by else None,
            "created_by_name": created_by_name,
            "approved_by": str(pr.approved_by) if pr.approved_by else None,
            "approved_by_name": approved_by_name,
            "created_at": str(pr.created_at),
            "approved_at": str(pr.approved_at) if pr.approved_at else None,
            "completed_at": str(pr.completed_at) if pr.completed_at else None,
            "updated_at": str(pr.updated_at) if pr.updated_at else None,
            "items": items
        }



