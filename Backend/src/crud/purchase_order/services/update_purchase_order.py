from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.user.repositories import UserRepository
from src.crud.warehouse.repositories import WareHouseRepository
from src.database.models import PurchaseOrder, PurchaseOrderDetail, Product_Variant, Supplier, Warehouse
from src.errors.product import ProductException
from src.errors.purchase_order import PurchaseOrderException
from src.errors.supplier import SupplierException
from src.errors.warehouse import WareHouseException
from src.schemas.purchase_order import PurchaseOrderDetailCreate, UpdatePurchaseOrderRequest

purchase_order_repository = PurchaseOrderRepository()
supplier_repository = SupplierRepository()
warehouse_repository = WareHouseRepository()
user_repository = UserRepository()
product_variant_repository = ProductVariantRepository()


class UpdatePurchaseOrderService:
    async def update_purchase_order(self, po_id: str, request: UpdatePurchaseOrderRequest, session: AsyncSession):
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

        if po.status != "draft":
            PurchaseOrderException.only_draft_can_update()

        if request.supplier_id and request.supplier_id != str(po.supplier_id):
            await self.validate_and_update_supplier(po, request.supplier_id, session)

        if request.warehouse_id and request.warehouse_id != str(po.warehouse_id):
            await self.validate_and_update_warehouse(po, request.warehouse_id, session)

        if request.notes is not None:
            po.notes = request.notes

        new_details = None
        if request.items is not None:
            new_details, sub_total = await self.build_new_details(request.items, session)

            total_amount = sub_total + 15000
            if total_amount > 2147483647:
                ProductException.total_cost_exceeds_limit()

            po.sub_total = sub_total
            po.discount_amount = 0
            po.shipping_cost = 15000
            po.total_amount = total_amount

        po.updated_at = datetime.now()

        updated_po = await purchase_order_repository.update_purchase_order(session, po, new_details)

        return {
            "id": str(updated_po.id),
            "po_number": updated_po.po_number,
            "status": updated_po.status,
            "updated_at": updated_po.updated_at.isoformat() if updated_po.updated_at else None
        }

    async def validate_and_update_supplier(self, po: PurchaseOrder, supplier_id: str, session: AsyncSession):
        condition_supplier = [Supplier.id == supplier_id]
        supplier = await supplier_repository.get_supplier(
            session=session,
            where_conditions=condition_supplier
        )

        if not supplier:
            SupplierException.supplier_not_found()

        if not supplier.is_active:
            SupplierException.supplier_not_active()

        po.supplier_id = supplier_id

    async def validate_and_update_warehouse(self, po: PurchaseOrder, warehouse_id: str, session: AsyncSession):
        condition_warehouse = [Warehouse.id == warehouse_id]
        warehouse = await warehouse_repository.get_warehouse(session=session, where_conditions=condition_warehouse)

        if not warehouse:
            WareHouseException.warehouse_not_found()

        if not warehouse.is_active:
            WareHouseException.warehouse_already_inactive()

        po.warehouse_id = warehouse_id

    async def build_new_details(self, items: List[PurchaseOrderDetailCreate], session: AsyncSession):
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

    async def get_variants_batch(self, variant_ids: List[str], session: AsyncSession) -> Dict[str, Any]:
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



