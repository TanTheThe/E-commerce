from datetime import datetime
from sqlalchemy.orm import selectinload
from sqlmodel import and_
from src.crud.good_receipts.repositories import GoodsReceiptRepository
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.purchase_return.repositories import PurchaseReturnRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Warehouse, Product_Variant, Supplier, PurchaseOrder, \
    GoodsReceiptDetail, GoodsReceipt, PurchaseReturn
from src.errors.goods_receipt import GoodsReceiptException
from src.errors.product import ProductException
from src.errors.purchase_order import PurchaseOrderException
from src.errors.purchase_return import PurchaseReturnException
from src.errors.supplier import SupplierException
from src.errors.warehouse import WareHouseException
from src.schemas.goods_receipt import CreateGoodsReceiptRequest

supplier_repository = SupplierRepository()
warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
purchase_order_repository = PurchaseOrderRepository()
goods_receipt_repository = GoodsReceiptRepository()
purchase_return_repository = PurchaseReturnRepository()


class CreateGoodsReceiptService:
    async def create_goods_receipt(self, request: CreateGoodsReceiptRequest, created_by: str, session: AsyncSession):
        condition_po = [PurchaseOrder.id == request.purchase_order_id]
        options_po = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse),
            selectinload(PurchaseOrder.po_details)
        ]
        purchase_order = await purchase_order_repository.get_purchase_order(
            session=session,
            where_conditions=condition_po,
            options=options_po
        )
        if not purchase_order:
            PurchaseOrderException.po_not_found()

        if purchase_order.status != "confirmed":
            PurchaseOrderException.invalid_status_for_receipt()

        condition_supplier = [Supplier.id == request.supplier_id]
        supplier = await supplier_repository.get_supplier(
            session=session,
            where_conditions=condition_supplier
        )

        if not supplier:
            SupplierException.supplier_not_found()

        if not supplier.is_active:
            SupplierException.supplier_not_active()

        if str(purchase_order.supplier_id) != request.supplier_id:
            SupplierException.supplier_not_match_with_po()

        condition_warehouse = and_(Warehouse.id == request.warehouse_id)
        warehouse = await warehouse_repository.get_warehouse(
            session=session,
            conditions=condition_warehouse
        )

        if not warehouse:
            WareHouseException.warehouse_not_found()

        if not warehouse.is_active:
            WareHouseException.warehouse_already_inactive()

        if str(purchase_order.warehouse_id) != request.warehouse_id:
            WareHouseException.warehouse_not_match_with_po()

        if request.parent_receipt_id:
            condition_parent = [GoodsReceipt.id == request.parent_receipt_id]
            parent_receipt = await goods_receipt_repository.get_goods_receipt(
                session=session,
                where_conditions=condition_parent
            )

            if not parent_receipt:
                GoodsReceiptException.gr_parent_not_exist()

            if not parent_receipt.has_discrepancy:
                GoodsReceiptException.gr_parent_must_have_discrepancy()

            if str(parent_receipt.purchase_order_id) != request.purchase_order_id:
                GoodsReceiptException.gr_child_must_same_po_with_parent()

        receipt_details = []
        total_received_amount = 0
        has_discrepancy = False
        discrepancy_notes_list = []

        po_details_map = {str(detail.id): detail for detail in purchase_order.po_details}

        for item in request.items:
            po_detail = po_details_map.get(item.po_detail_id)
            if not po_detail:
                PurchaseOrderException.po_detail_not_exist()

            condition_variant = and_(Product_Variant.id == item.product_variant_id)
            joins_variant = [
                selectinload(Product_Variant.product),
                selectinload(Product_Variant.color)
            ]
            variant = await product_variant_repository.get_product_variant(
                condition_variant,
                session=session,
                joins=joins_variant
            )
            if not variant:
                ProductException.not_found_variant()

            if str(po_detail.product_variant_id) != item.product_variant_id:
                PurchaseOrderException.variant_not_match()

            if item.ordered_quantity != po_detail.quantity:
                PurchaseOrderException.order_quantity_not_equal_po_detail()

            if item.received_quantity != item.ordered_quantity:
                has_discrepancy = True
                discrepancy_notes_list.append(
                    f"SKU {variant.sku}: Đặt {item.ordered_quantity}, nhận {item.received_quantity}"
                )

            if item.rejected_quantity > 0:
                has_discrepancy = True
                discrepancy_notes_list.append(
                    f"SKU {variant.sku}: Từ chối {item.rejected_quantity} - {item.rejection_reason or 'Không rõ lý do'}"
                )

            if item.accepted_quantity + item.rejected_quantity != item.received_quantity:
                GoodsReceiptException.invalid_quantity_calculation()

            unit_cost = po_detail.unit_cost
            total_cost = item.accepted_quantity * unit_cost
            total_received_amount += total_cost

            product_snapshot = {
                "product_name": variant.product.name if variant.product else None,
                "variant_sku": variant.sku,
                "variant_size": variant.size,
                "variant_color_name": variant.color_name if variant.color_name else (
                    variant.color.name if variant.color else None
                ),
                "variant_color_code": variant.color_code if variant.color_code else (
                    variant.color.code if variant.color else None
                ),
                "variant_image": variant.image,
                "variant_price": variant.price,
                "unit_cost": unit_cost,
                "snapshot_date": datetime.now().isoformat()
            }

            receipt_detail = GoodsReceiptDetail(
                product_variant_id=item.product_variant_id,
                po_detail_id=item.po_detail_id,
                ordered_quantity=item.ordered_quantity,
                received_quantity=item.received_quantity,
                accepted_quantity=item.accepted_quantity,
                rejected_quantity=item.rejected_quantity,
                unit_cost=unit_cost,
                total_cost=total_cost,
                rejection_reason=item.rejection_reason,
                product_snapshot=product_snapshot,
                notes=item.notes,
                created_at=datetime.now()
            )
            receipt_details.append(receipt_detail)

        receipt_number = await goods_receipt_repository.generate_gr_number(session=session)

        discrepancy_notes = None
        if has_discrepancy:
            discrepancy_notes = "; ".join(discrepancy_notes_list)

        goods_receipt = GoodsReceipt(
            receipt_number=receipt_number,
            purchase_order_id=request.purchase_order_id,
            parent_receipt_id=request.parent_receipt_id,
            warehouse_id=request.warehouse_id,
            supplier_id=request.supplier_id,
            status="pending",
            receipt_date=request.receipt_date,
            delivery_note_number=request.delivery_note_number,
            total_received_amount=total_received_amount,
            received_by=created_by,
            received_at=datetime.now(),
            has_discrepancy=has_discrepancy,
            discrepancy_notes=discrepancy_notes,
            notes=request.notes,
            created_at=datetime.now()
        )

        created_gr = await goods_receipt_repository.create_goods_receipt(goods_receipt, receipt_details, session)

        await session.commit()

        return {
            "id": str(created_gr.id),
            "receipt_number": created_gr.receipt_number,
            "purchase_order_id": str(created_gr.purchase_order_id),
            "purchase_order_number": created_gr.purchase_order.po_number if created_gr.purchase_order else None,
            "parent_receipt_id": str(created_gr.parent_receipt_id) if created_gr.parent_receipt_id else None,
            "supplier_id": str(created_gr.supplier_id),
            "supplier_name": created_gr.supplier.name if created_gr.supplier else None,
            "warehouse_id": str(created_gr.warehouse_id),
            "warehouse_name": created_gr.warehouse.name if created_gr.warehouse else None,
            "status": created_gr.status,
            "receipt_date": created_gr.receipt_date.isoformat(),
            "total_received_amount": created_gr.total_received_amount,
            "has_discrepancy": created_gr.has_discrepancy,
            "discrepancy_notes": created_gr.discrepancy_notes,
            "created_at": created_gr.created_at.isoformat()
        }
