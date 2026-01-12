from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.user.repositories import UserRepository
from src.database.models import Product_Variant, PurchaseReturn, User, PurchaseReturnDetail
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
            selectinload(PurchaseReturn.return_details)
                .selectinload(PurchaseReturnDetail.product_variant)
                .selectinload(Product_Variant.product),
            selectinload(PurchaseReturn.return_details)
                .selectinload(PurchaseReturnDetail.product_variant)
                .selectinload(Product_Variant.color),
            selectinload(PurchaseReturn.return_details)
                .selectinload(PurchaseReturnDetail.goods_receipt_detail)
        ]
        
        pr = await purchase_return_repository.get_purchase_return(session=session, where_conditions=condition_pr,
                                                                  options=options)
        if not pr:
            PurchaseReturnException.pr_not_found()
            
        user_ids = []
        if pr.created_by:
            user_ids.append(pr.created_by)
        if pr.approved_by and pr.approved_by not in user_ids:
            user_ids.append(pr.approved_by)
        if pr.confirmed_by and pr.confirmed_by not in user_ids:
            user_ids.append(pr.confirmed_by)
        if pr.completed_by and pr.completed_by not in user_ids:
            user_ids.append(pr.completed_by)

        users_map = {}
        if user_ids:
            users, _ = await user_repository.get_all_users(
                session=session,
                where_conditions=[User.id.in_(user_ids)]
            )
            users_map = {
                str(user.id): f"{user.first_name} {user.last_name}".strip()
                for user in users
            }
            
        created_by_name = users_map.get(str(pr.created_by)) if pr.created_by else None
        approved_by_name = users_map.get(str(pr.approved_by)) if pr.approved_by else None
        confirmed_by_name = users_map.get(str(pr.confirmed_by)) if pr.confirmed_by else None
        completed_by_name = users_map.get(str(pr.completed_by)) if pr.completed_by else None

        items = []
        for detail in pr.return_details:
            product_snapshot = detail.product_snapshot or {}
            
            if detail.product_variant:
                if not product_snapshot.get('sku'):
                    product_snapshot['sku'] = detail.product_variant.sku
                if not product_snapshot.get('size'):
                    product_snapshot['size'] = detail.product_variant.size
                if not product_snapshot.get('variant_image'):
                    product_snapshot['variant_image'] = detail.product_variant.image
                
                if detail.product_variant.product and not product_snapshot.get('name'):
                    product_snapshot['name'] = detail.product_variant.product.name
                
                if detail.product_variant.color and not product_snapshot.get('color_name'):
                    product_snapshot['color_name'] = detail.product_variant.color.name
            
            items.append({
                "id": str(detail.id),
                "product_id": str(detail.product_variant.product_id) if detail.product_variant else None,
                "product_variant_id": str(detail.product_variant_id),
                "goods_receipt_detail_id": str(detail.goods_receipt_detail_id) if detail.goods_receipt_detail_id else None,
                "return_quantity": detail.return_quantity,
                "unit_cost": detail.unit_cost,
                "total_cost": detail.total_cost,
                "condition": detail.condition,
                "rejection_evidence": detail.rejection_evidence,
                "product_snapshot": product_snapshot,
                "notes": detail.notes,
                "created_at": detail.created_at.isoformat() if detail.created_at else None,
            })

        return {
            "id": str(pr.id),
            "return_number": pr.return_number,
            "purchase_order": {
                "id": str(pr.purchase_order_id),
                "po_number": pr.purchase_order.po_number if pr.purchase_order else None
            } if pr.purchase_order_id else None,
            "goods_receipt": {
                "id": str(pr.goods_receipt_id),
                "receipt_number": pr.goods_receipt.receipt_number if pr.goods_receipt else None
            } if pr.goods_receipt_id else None,
            "supplier": {
                "id": str(pr.supplier_id),
                "name": pr.supplier.name if pr.supplier else None,
                "code": pr.supplier.code if pr.supplier else None,
                "email": pr.supplier.email if pr.supplier else None,
                "phone": pr.supplier.phone if pr.supplier else None
            } if pr.supplier_id else None,
            "warehouse": {
                "id": str(pr.warehouse_id),
                "name": pr.warehouse.name if pr.warehouse else None,
                "code": pr.warehouse.code if pr.warehouse else None
            } if pr.warehouse_id else None,
            "status": pr.status,
            "return_type": pr.return_type,
            "return_date": pr.return_date.isoformat() if pr.return_date else None,
            "shipped_date": pr.shipped_date.isoformat() if pr.shipped_date else None,
            "total_return_amount": pr.total_return_amount,
            "refund_amount": pr.refund_amount,
            "return_reason": pr.return_reason,
            "delivery_note_number": pr.delivery_note_number,
            "notes": pr.notes,
            "created_by": str(pr.created_by) if pr.created_by else None,
            "created_by_name": created_by_name,
            "approved_by": str(pr.approved_by) if pr.approved_by else None,
            "approved_by_name": approved_by_name,
            "confirmed_by": str(pr.confirmed_by) if pr.confirmed_by else None,
            "confirmed_by_name": confirmed_by_name,
            "completed_by": str(pr.completed_by) if pr.completed_by else None,
            "completed_by_name": completed_by_name,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
            "approved_at": pr.approved_at.isoformat() if pr.approved_at else None,
            "confirmed_at": pr.confirmed_at.isoformat() if pr.confirmed_at else None,
            "completed_at": pr.completed_at.isoformat() if pr.completed_at else None,
            "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
            "items": items
        }



