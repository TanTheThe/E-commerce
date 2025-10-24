from datetime import datetime
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, Product_Variant, Supplier, PurchaseOrderDetail, PurchaseOrder
from src.errors.product import ProductException
from src.errors.supplier import SupplierException
from src.errors.warehouse import WareHouseException
from src.schemas.purchase_order import CreatePurchaseOrderRequest

supplier_repository = SupplierRepository()
warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
purchase_order_repository = PurchaseOrderRepository()


class CreatePurchaseOrderService:
    async def create_purchase_order(self, request: CreatePurchaseOrderRequest, created_by: str, session: AsyncSession):
        condition_supplier = [
            Supplier.id == request.supplier_id,
        ]
        supplier = await supplier_repository.get_supplier(session=session, where_conditions=condition_supplier)
        if not supplier:
            SupplierException.supplier_not_found()

        if not supplier.is_active:
            SupplierException.supplier_not_active()

        condition_warehouse = and_(Warehouse.id == request.warehouse_id)

        warehouse = await warehouse_repository.get_warehouse(session=session, conditions=condition_warehouse)
        if not warehouse:
            WareHouseException.warehouse_not_found()

        if not warehouse.is_active:
            WareHouseException.warehouse_already_inactive()

        po_details = []
        sub_total = 0

        for item in request.items:
            condition = and_(Product_Variant.id == item.product_variant_id)
            joins = [
                selectinload(Product_Variant.product),
                selectinload(Product_Variant.color)
            ]
            variant = await product_variant_repository.get_product_variant(condition, session=session, joins=joins)
            if not variant:
                ProductException.not_found_variant()

            total_cost = variant.price * item.quantity
            sub_total += total_cost

            product_snapshot = {
                "product_name": variant.product.name if variant.product else None,
                "variant_sku": variant.sku,
                "variant_size": variant.size,
                "variant_color_name": variant.color_name if variant.color_name else (variant.color.name if variant.color else None),
                "variant_color_code": variant.color_code if variant.color_code else (variant.color.code if variant.color else None),
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
                notes=item.notes,
                created_at=datetime.now(),
            )
            po_details.append(po_detail)

        discount_amount = 0
        shipping_cost = 0
        total_amount = sub_total + shipping_cost - discount_amount

        po_number = await purchase_order_repository.generate_po_number(session=session)

        purchase_order = PurchaseOrder(
            po_number=po_number,
            supplier_id=request.supplier_id,
            warehouse_id=request.warehouse_id,
            status="draft",
            order_date=datetime.now(),
            expected_delivery_date=None,
            sub_total=sub_total,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            total_amount=total_amount,
            payment_status="unpaid",
            paid_amount=0,
            notes=request.notes,
            created_by=created_by,
            created_at=datetime.now()
        )

        created_po = await purchase_order_repository.create_purchase_order(purchase_order, po_details, session)

        return {
            "id": str(created_po.id),
            "number": created_po.po_number,
            "supplier_id": str(created_po.supplier_id),
            "supplier_name": created_po.supplier.name if created_po.supplier else None,
            "supplier_code": created_po.supplier.code if created_po.supplier else None,
            "warehouse_id": str(created_po.warehouse_id),
            "warehouse_name": created_po.warehouse.name if created_po.warehouse else None,
            "warehouse_code": created_po.warehouse.code if created_po.warehouse else None,
            "status": created_po.status,
        }




