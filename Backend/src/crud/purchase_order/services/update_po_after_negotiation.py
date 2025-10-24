from datetime import datetime
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import PurchaseOrder, PurchaseOrderDetail, Product_Variant
from src.errors.product import ProductException
from src.errors.purchase_order import PurchaseOrderException
from src.schemas.purchase_order import UpdatePurchaseOrderAfterNegotiationRequest

purchase_order_repository = PurchaseOrderRepository()
supplier_repository = SupplierRepository()
warehouse_repository = WareHouseRepository()
user_repository = UserRepository()
product_variant_repository = ProductVariantRepository()


class UpdatePOAfterNegotiationService:
    async def update_po_after_negotiation(self, po_id: str, request: UpdatePurchaseOrderAfterNegotiationRequest,
                                          session: AsyncSession):
        condition_po = [PurchaseOrder.id == po_id]

        options = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.product),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.color)
        ]

        po = await purchase_order_repository.get_purchase_order(
            session=session,
            where_conditions=condition_po,
            options=options
        )

        if not po:
            PurchaseOrderException.po_not_found()

        if po.status != "sent":
            PurchaseOrderException.only_sent_can_update()

        if request.expected_delivery_date is not None:
            po.expected_delivery_date = request.expected_delivery_date

        if request.notes is not None:
            po.notes = request.notes

        if request.supplier_invoice_urls is None:
            PurchaseOrderException.need_invoice_to_update_po()

        po.supplier_invoice_urls = request.supplier_invoice_urls

        new_details = None
        if request.items is not None:
            new_details = []
            sub_total = 0

            for item in request.items:
                condition_variant = and_(
                    Product_Variant.id == item.product_variant_id,
                    Product_Variant.deleted_at.is_(None)
                )
                variant = await product_variant_repository.get_product_variant(condition_variant, session)
                if not variant:
                    ProductException.not_found_variant()

                total_cost = variant.price * item.quantity
                sub_total += total_cost

                product_snapshot = {
                    "product_name": variant.product.name if variant.product else None,
                    "variant_sku": variant.sku,
                    "variant_size": variant.size,
                    "variant_color_name": variant.color_name if variant.color_name else (
                        variant.color.name if variant.color else None),
                    "variant_color_code": variant.color_code if variant.color_code else (
                        variant.color.code if variant.color else None),
                    "variant_image": variant.image,
                    "variant_price": variant.price,
                    "snapshot_date": datetime.now().isoformat()
                }

                po_detail = PurchaseOrderDetail(
                    product_variant_id=item.product_variant_id,
                    quantity=item.quantity,
                    received_quantity=0,
                    unit_cost=variant.price,
                    total_cost=total_cost,
                    product_snapshot=product_snapshot,
                    notes=item.notes
                )
                new_details.append(po_detail)

            po.sub_total = sub_total

        if request.discount_amount is not None:
            po.discount_amount = request.discount_amount

        if request.shipping_cost is not None:
            po.shipping_cost = request.shipping_cost

        po.total_amount = po.sub_total + po.shipping_cost - po.discount_amount

        po.updated_at = datetime.now()

        updated_po = await purchase_order_repository.update_purchase_order(session, po, new_details)

        return {
            "id": str(updated_po.id),
            "po_number": updated_po.po_number,
            "status": updated_po.status,
            "sub_total": updated_po.sub_total,
            "discount_amount": updated_po.discount_amount,
            "shipping_cost": updated_po.shipping_cost,
            "total_amount": updated_po.total_amount,
            "expected_delivery_date": updated_po.expected_delivery_date.isoformat() if updated_po.expected_delivery_date else None
        }
