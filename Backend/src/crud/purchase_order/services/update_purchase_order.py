from datetime import datetime
from sqlalchemy.orm import selectinload
from sqlmodel import and_
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
from src.schemas.purchase_order import UpdatePurchaseOrderRequest

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
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.product),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.color)
        ]

        po = await purchase_order_repository.get_purchase_order(session=session, where_conditions=condition_po, options=options)
        if not po:
            PurchaseOrderException.po_not_found()

        if po.status != "draft":
            PurchaseOrderException.only_draft_can_update()

        if request.supplier_id and request.supplier_id != po.supplier_id:
            condition_supplier = [Supplier.id == request.supplier_id]
            supplier = await supplier_repository.get_supplier(session=session, where_conditions=condition_supplier)
            if not supplier:
                SupplierException.supplier_not_found()

            if not supplier.is_active:
                SupplierException.supplier_not_active()

            po.supplier_id = request.supplier_id

        if request.warehouse_id and request.warehouse_id != po.warehouse_id:
            condition_warehouse = and_(Warehouse.id == request.warehouse_id)
            warehouse = await warehouse_repository.get_warehouse(condition_warehouse, session)
            if not warehouse:
                WareHouseException.warehouse_not_found()

            if not warehouse.is_active:
                WareHouseException.warehouse_already_inactive()

            po.warehouse_id = request.warehouse_id

        if request.notes is not None:
            po.notes = request.notes

        new_details = None
        if request.items is not None:
            new_details = []
            sub_total = 0

            for item in request.items:
                condition_variant = [Product_Variant.id == item.product_variant_id, Product_Variant.deleted_at.is_(None)]
                variant = await product_variant_repository.get_product_variant(session=session, where_conditions=condition_variant)
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
            po.discount_amount = 0
            po.shipping_cost = 15000
            po.total_amount = sub_total + po.shipping_cost - po.discount_amount


        updated_po = await purchase_order_repository.update_purchase_order(session, po, new_details)

        return {
            "id": str(updated_po.id),
        }









