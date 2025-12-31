from datetime import datetime
from typing import List
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import PurchaseOrder, PurchaseOrderDetail, Product_Variant
from src.errors.product import ProductException
from src.errors.purchase_order import PurchaseOrderException
from src.schemas.purchase_order import UpdatePurchaseOrderAfterNegotiationRequest, PurchaseOrderDetailUpdate

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

        po.supplier_invoice_urls = request.supplier_invoice_urls

        new_details = None
        if request.items is not None:
            new_details, sub_total = await self.build_new_details(request.items, session)
            po.sub_total = sub_total

        if request.discount_amount is not None:
            po.discount_amount = request.discount_amount

        if request.shipping_cost is not None:
            po.shipping_cost = request.shipping_cost

        total_amount = po.sub_total + po.shipping_cost - po.discount_amount

        if total_amount < 0:
            PurchaseOrderException.total_amount_negative()

        if total_amount > 2147483647:
            ProductException.total_cost_exceeds_limit()

        po.total_amount = total_amount
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
            "expected_delivery_date": updated_po.expected_delivery_date.isoformat() if updated_po.expected_delivery_date else None,
            "updated_at": updated_po.updated_at.isoformat() if updated_po.updated_at else None
        }

    async def build_new_details(self, items: List[PurchaseOrderDetailUpdate], session: AsyncSession):
        variant_ids = [item.product_variant_id for item in items]
        variants_dict = await self.get_variants_batch(variant_ids, session)

        new_details = []
        sub_total = 0

        for item in items:
            variant = variants_dict.get(item.product_variant_id)
            if not variant:
                ProductException.not_found_variant()

            if variant.price <= 0:
                ProductException.invalid_variant_price()

            total_cost = variant.price * item.quantity

            if total_cost > 2147483647:
                ProductException.total_cost_exceeds_limit()

            sub_total += total_cost

            product_snapshot = {
                "product_name": variant.product.name if variant.product else None,
                "variant_sku": variant.sku,
                "variant_size": variant.size,
                "variant_color_name": variant.color_name or (
                    variant.color.name if variant.color else None
                ),
                "variant_color_code": variant.color_code or (
                    variant.color.code if variant.color else None
                ),
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

        return new_details, sub_total

    async def get_variants_batch(self, variant_ids: List[str], session: AsyncSession):
        condition = [
            Product_Variant.id.in_(variant_ids),
            Product_Variant.deleted_at.is_(None)
        ]
        options = [
            selectinload(Product_Variant.product),
            selectinload(Product_Variant.color)
        ]

        variants, _ = await product_variant_repository.get_all_product_variant(
            session=session,
            where_conditions=condition,
            options=options
        )

        return {str(v.id): v for v in variants}

