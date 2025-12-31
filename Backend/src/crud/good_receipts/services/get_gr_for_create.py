from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.user.repositories import UserRepository
from src.database.models import GoodsReceipt, GoodsReceiptDetail, Product_Variant
from src.errors.goods_receipt import GoodsReceiptException


goods_receipt_repository = GoodsReceiptRepository()
user_repository = UserRepository()


class GetGRForCreateService:
    async def get_goods_receipt_for_create(self, parent_gr_id: str, session: AsyncSession):
        condition_gr = [GoodsReceipt.id == parent_gr_id]

        options = [
            selectinload(GoodsReceipt.receipt_details).selectinload(
                GoodsReceiptDetail.product_variant
            ).selectinload(Product_Variant.product),
            selectinload(GoodsReceipt.receipt_details).selectinload(
                GoodsReceiptDetail.product_variant
            ).selectinload(Product_Variant.color),
        ]

        parent_gr = await goods_receipt_repository.get_goods_receipt(
            session=session,
            where_conditions=condition_gr,
            options=options
        )

        if not parent_gr:
            GoodsReceiptException.gr_not_found()

        if parent_gr.status not in ['approved', 'completed']:
            GoodsReceiptException.invalid_parent_status()

        child_condition = [GoodsReceipt.parent_receipt_id == parent_gr_id]
        child_options = [selectinload(GoodsReceipt.receipt_details)]

        direct_children, _ = await goods_receipt_repository.get_all_goods_receipt(
            session=session,
            where_conditions=child_condition,
            options=child_options
        )

        child_received_map = {}

        for child_gr in direct_children:
            for child_detail in child_gr.receipt_details:
                variant_id = str(child_detail.product_variant_id)
                child_received_map[variant_id] = (
                        child_received_map.get(variant_id, 0) + child_detail.received_quantity
                )

        items = []
        for detail in parent_gr.receipt_details:
            if detail.rejected_quantity <= 0:
                continue

            variant_id = str(detail.product_variant_id)

            available_qty = detail.rejected_quantity - child_received_map.get(variant_id, 0)

            if available_qty <= 0:
                continue

            if detail.product_snapshot:
                product_name = detail.product_snapshot.get("product_name")
                variant_sku = detail.product_snapshot.get("variant_sku")
                variant_size = detail.product_snapshot.get("variant_size")
                variant_color_name = detail.product_snapshot.get("variant_color_name")
                variant_image = detail.product_snapshot.get("variant_image")
            else:
                product_variant = detail.product_variant
                product = product_variant.product if product_variant else None

                product_name = product.name if product else None
                variant_sku = product_variant.sku if product_variant else None
                variant_size = product_variant.size if product_variant else None
                variant_image = product_variant.image if product_variant else None

                variant_color_name = None
                if product_variant:
                    variant_color_name = (
                            product_variant.color_name or
                            (product_variant.color.name if product_variant.color else None)
                    )

            items.append({
                "product_variant_id": variant_id,
                "product_name": product_name,
                "variant_sku": variant_sku,
                "variant_size": variant_size,
                "variant_color_name": variant_color_name,
                "variant_image": variant_image,
                "rejected_quantity": detail.rejected_quantity,
                "already_received": child_received_map.get(variant_id, 0),
                "available_quantity": available_qty,
                "unit_cost": float(detail.unit_cost) if detail.unit_cost else None,
            })

        if not items:
            GoodsReceiptException.no_items_available_for_child_receipt()

        return {
            "parent_receipt_id": str(parent_gr.id),
            "parent_receipt_number": parent_gr.receipt_number,
            "parent_status": parent_gr.status,
            "total_items": len(items),
            "items": items
        }
