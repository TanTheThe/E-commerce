from datetime import datetime
from typing import Optional
from sqlalchemy.orm import selectinload
from src.config import Config
from src.crud.authentication.utils import create_url_safe_token
from src.crud.product_variant.repositories import ProductVariantRepository
from src.crud.purchase_order.repositories import PurchaseOrderRepository
from src.crud.supplier.repositories import SupplierRepository
from src.crud.warehouse.repositories import WareHouseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import Product_Variant, PurchaseOrderDetail, PurchaseOrder
from src.errors.purchase_order import PurchaseOrderException
from src.mail import create_message, mail
from src.schemas.purchase_order import SendPurchaseOrderRequest

supplier_repository = SupplierRepository()
warehouse_repository = WareHouseRepository()
product_variant_repository = ProductVariantRepository()
purchase_order_repository = PurchaseOrderRepository()


class SendPurchaseOrderService:
    async def send_purchase_order_to_supplier(self, session: AsyncSession, po_id: str, user_id: str,
                                              request: Optional[SendPurchaseOrderRequest] = None):
        condition_po = [PurchaseOrder.id == po_id]
        options_po = [
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.product),
            selectinload(PurchaseOrder.po_details).selectinload(PurchaseOrderDetail.product_variant).selectinload(
                Product_Variant.color)
        ]

        po = await purchase_order_repository.get_purchase_order(session=session, where_conditions=condition_po,
                                                                options=options_po)
        if not po:
            PurchaseOrderException.po_not_found()

        if po.status != "draft":
            PurchaseOrderException.only_sent_when_draft()

        supplier_email = None
        if request and request.supplier_email:
            supplier_email = request.supplier_email
        elif po.supplier and po.supplier.email:
            supplier_email = po.supplier.email
        else:
            PurchaseOrderException.supplier_email_not_found()

        try:
            await self.send_po_email_to_supplier(
                po=po,
                supplier_email=supplier_email
            )
        except Exception as e:
            raise ValueError(f"Lỗi khi gửi email: {str(e)}")

        po.status = "sent"
        po.approved_by = user_id
        po.sent_at = datetime.now()
        po.updated_at = datetime.now()

        if request and request.notes:
            po.notes = f"{po.notes}\n[Gửi NCC] {request.notes}" if po.notes else f"[Gửi NCC] {request.notes}"

        updated_po = await purchase_order_repository.update_purchase_order(session, po)

        return {
            "id": str(updated_po.id),
            "number": updated_po.po_number,
            "supplier_id": str(updated_po.supplier_id),
            "supplier_name": updated_po.supplier.name if updated_po.supplier else None,
            "supplier_code": updated_po.supplier.code if updated_po.supplier else None,
            "warehouse_id": str(updated_po.warehouse_id),
            "warehouse_name": updated_po.warehouse.name if updated_po.warehouse else None,
            "warehouse_code": updated_po.warehouse.code if updated_po.warehouse else None,
            "status": updated_po.status,
        }

    async def send_po_email_to_supplier(self, po: PurchaseOrder, supplier_email: str):
        def format_currency(amount: int) -> str:
            return f"{amount:,}".replace(",", ".")

        items_html = ""
        for idx, detail in enumerate(po.po_details, 1):
            variant_info = ""
            if detail.product_variant:
                variant_info = f"{detail.product_variant.sku}"
                if detail.product_variant.size:
                    variant_info += f" - Size {detail.product_variant.size}"

                color_name = None
                if detail.product_variant.color_name:
                    color_name = detail.product_variant.color_name
                elif detail.product_variant.color:
                    color_name = detail.product_variant.color.name

                if color_name:
                    variant_info += f" - {color_name}"

            product_name = detail.product_variant.product.name if detail.product_variant and detail.product_variant.product else "N/A"

            items_html += f"""
                                <tr style="border-bottom: 1px solid #e8e8e8;">
                                    <td style="padding: 14px 10px; text-align: center; color: #666;">{idx}</td>
                                    <td style="padding: 14px 10px;">
                                        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 4px;">{product_name}</div>
                                        <div style="color: #7f8c8d; font-size: 13px;">{variant_info}</div>
                                    </td>
                                    <td style="padding: 14px 10px; text-align: center; color: #34495e; font-weight: 500;">{detail.quantity}</td>
                                    <td style="padding: 14px 10px; text-align: right; color: #34495e;">{format_currency(detail.unit_cost)} đ</td>
                                    <td style="padding: 14px 10px; text-align: right; color: #2c3e50; font-weight: 600;">{format_currency(detail.total_cost)} đ</td>
                                </tr>
                                """

        html_message = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    </head>
                    <body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f6f9; padding: 30px 20px;">
                            <tr>
                                <td align="center">
                                    <table width="650" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">

                                        <!-- Header -->
                                        <tr>
                                            <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                                                <div style="font-size: 48px; margin-bottom: 10px;">📦</div>
                                                <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 600; letter-spacing: -0.5px;">Đơn Đặt Hàng</h1>
                                                <p style="color: rgba(255,255,255,0.9); margin: 12px 0 0 0; font-size: 16px;">#{po.po_number}</p>
                                            </td>
                                        </tr>

                                        <!-- Content -->
                                        <tr>
                                            <td style="padding: 40px 35px;">

                                                <p style="font-size: 17px; color: #2c3e50; line-height: 1.6; margin: 0 0 10px 0;">
                                                    Kính gửi <strong style="color: #667eea;">{po.supplier.name if po.supplier else 'Quý Nhà cung cấp'}</strong>,
                                                </p>

                                                <p style="font-size: 15px; color: #5a6c7d; line-height: 1.7; margin: 0 0 35px 0;">
                                                    Chúng tôi xin gửi đến Quý công ty đơn đặt hàng với thông tin chi tiết như bên dưới. 
                                                    Rất mong nhận được sự hợp tác và phản hồi từ phía Quý công ty.
                                                </p>

                                                <!-- Thông tin đơn hàng -->
                                                <div style="background: linear-gradient(to right, #f8f9fa, #ffffff); border-radius: 10px; padding: 25px; margin-bottom: 35px; border-left: 4px solid #667eea;">
                                                    <h3 style="color: #2c3e50; font-size: 16px; margin: 0 0 20px 0; font-weight: 600;">📋 Thông tin đơn hàng</h3>
                                                    <table width="100%" cellpadding="0" cellspacing="0">
                                                        <tr>
                                                            <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px; width: 45%;">
                                                                <span style="display: inline-block; width: 20px;">📄</span> Mã đơn hàng
                                                            </td>
                                                            <td style="padding: 8px 0; color: #2c3e50; font-weight: 600; font-size: 14px;">{po.po_number}</td>
                                                        </tr>
                                                        <tr>
                                                            <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px;">
                                                                <span style="display: inline-block; width: 20px;">📅</span> Ngày đặt hàng
                                                            </td>
                                                            <td style="padding: 8px 0; color: #2c3e50; font-weight: 600; font-size: 14px;">{po.order_date.strftime('%d/%m/%Y lúc %H:%M')}</td>
                                                        </tr>
                                                        <tr>
                                                            <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px;">
                                                                <span style="display: inline-block; width: 20px;">🚚</span> Ngày giao dự kiến
                                                            </td>
                                                            <td style="padding: 8px 0; color: #2c3e50; font-weight: 600; font-size: 14px;">{po.expected_delivery_date.strftime('%d/%m/%Y') if po.expected_delivery_date else 'Sẽ thống nhất sau'}</td>
                                                        </tr>
                                                        <tr>
                                                            <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px;">
                                                                <span style="display: inline-block; width: 20px;">🏢</span> Kho nhận hàng
                                                            </td>
                                                            <td style="padding: 8px 0; color: #2c3e50; font-weight: 600; font-size: 14px;">{po.warehouse.name if po.warehouse else 'Chưa xác định'}</td>
                                                        </tr>
                                                        <tr>
                                                            <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px; vertical-align: top;">
                                                                <span style="display: inline-block; width: 20px;">📍</span> Địa chỉ giao hàng
                                                            </td>
                                                            <td style="padding: 8px 0; color: #2c3e50; font-size: 14px; line-height: 1.5;">{po.warehouse.address if po.warehouse else 'Chưa xác định'}</td>
                                                        </tr>
                                                    </table>
                                                </div>

                                                <!-- Chi tiết sản phẩm -->
                                                <h3 style="color: #2c3e50; font-size: 18px; margin: 0 0 20px 0; font-weight: 600; display: flex; align-items: center;">
                                                    <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; width: 32px; height: 32px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 16px;">🛍️</span>
                                                    Chi tiết sản phẩm
                                                </h3>

                                                <table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #e8e8e8; border-radius: 8px; overflow: hidden;">
                                                    <thead>
                                                        <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                                                            <th style="padding: 14px 10px; text-align: center; color: white; font-size: 13px; font-weight: 600; width: 6%;">STT</th>
                                                            <th style="padding: 14px 10px; text-align: left; color: white; font-size: 13px; font-weight: 600; width: 38%;">Sản phẩm</th>
                                                            <th style="padding: 14px 10px; text-align: center; color: white; font-size: 13px; font-weight: 600; width: 14%;">Số lượng</th>
                                                            <th style="padding: 14px 10px; text-align: right; color: white; font-size: 13px; font-weight: 600; width: 20%;">Đơn giá</th>
                                                            <th style="padding: 14px 10px; text-align: right; color: white; font-size: 13px; font-weight: 600; width: 22%;">Thành tiền</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody style="background-color: #ffffff;">
                                                        {items_html}
                                                    </tbody>
                                                </table>

                                                <!-- Tổng cộng -->
                                                <div style="margin-top: 25px; padding: 20px; background: linear-gradient(to right, #f8f9fa, #ffffff); border-radius: 8px;">
                                                    <table width="100%" cellpadding="0" cellspacing="0">
                                                        <tr>
                                                            <td style="text-align: right; padding: 8px 0; color: #7f8c8d; font-size: 14px;">Tổng tiền hàng:</td>
                                                            <td style="text-align: right; padding: 8px 0; font-weight: 600; font-size: 15px; color: #2c3e50; width: 180px;">{format_currency(po.sub_total)} đ</td>
                                                        </tr>
                                                        <tr>
                                                            <td style="text-align: right; padding: 8px 0; color: #7f8c8d; font-size: 14px;">Phí vận chuyển:</td>
                                                            <td style="text-align: right; padding: 8px 0; font-weight: 600; font-size: 15px; color: #2c3e50;">+ {format_currency(po.shipping_cost)} đ</td>
                                                        </tr>
                                                        <tr>
                                                            <td style="text-align: right; padding: 8px 0; color: #7f8c8d; font-size: 14px;">Giảm giá:</td>
                                                            <td style="text-align: right; padding: 8px 0; font-weight: 600; font-size: 15px; color: #e74c3c;">- {format_currency(po.discount_amount)} đ</td>
                                                        </tr>
                                                        <tr style="border-top: 2px solid #667eea;">
                                                            <td style="text-align: right; padding: 15px 0 5px 0; font-size: 16px; font-weight: 600; color: #2c3e50;">TỔNG THANH TOÁN:</td>
                                                            <td style="text-align: right; padding: 15px 0 5px 0; font-weight: 700; font-size: 24px; color: #667eea;">{format_currency(po.total_amount)} đ</td>
                                                        </tr>
                                                    </table>
                                                </div>

                                                <!-- Ghi chú -->
                                                {f'''
                                                <div style="margin: 30px 0; padding: 18px 20px; background: linear-gradient(to right, #fff8e1, #ffffff); border-left: 4px solid #ffa726; border-radius: 6px;">
                                                    <div style="display: flex; align-items: flex-start;">
                                                        <span style="font-size: 20px; margin-right: 10px;">💬</span>
                                                        <div>
                                                            <strong style="color: #e65100; font-size: 14px; display: block; margin-bottom: 8px;">Ghi chú đặc biệt:</strong>
                                                            <p style="color: #5d4037; margin: 0; font-size: 14px; line-height: 1.6;">{po.notes}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                                ''' if po.notes else ''}

                                                <!-- Footer note -->
                                                <div style="margin-top: 40px; padding-top: 25px; border-top: 2px solid #f0f0f0;">
                                                    <p style="font-size: 15px; color: #5a6c7d; line-height: 1.7; margin: 0 0 20px 0;">
                                                        Vui lòng kiểm tra kỹ thông tin đơn hàng và liên hệ với chúng tôi nếu có bất kỳ thắc mắc nào. 
                                                        Chúng tôi rất mong được hợp tác cùng Quý công ty.
                                                    </p>
                                                    <div style="background: linear-gradient(to right, #f8f9fa, #ffffff); padding: 20px; border-radius: 8px; margin-top: 20px;">
                                                        <p style="font-size: 15px; color: #2c3e50; margin: 0; line-height: 1.8;">
                                                            Trân trọng,<br>
                                                            <strong style="color: #667eea; font-size: 16px;">Phòng Mua hàng</strong><br>
                                                            <span style="color: #7f8c8d; font-size: 14px;">Công ty E-Commerce</span>
                                                        </p>
                                                    </div>
                                                </div>

                                            </td>
                                        </tr>

                                        <!-- Footer -->
                                        <tr>
                                            <td style="background: linear-gradient(to right, #f8f9fa, #e9ecef); padding: 25px 35px; text-align: center; border-top: 1px solid #e0e0e0;">
                                                <p style="margin: 0; color: #95a5a6; font-size: 12px; line-height: 1.6;">
                                                    © 2025 E-Commerce Company. All rights reserved.<br>
                                                    <span style="font-size: 11px;">Email này được gửi tự động, vui lòng không trả lời trực tiếp email này.</span>
                                                </p>
                                            </td>
                                        </tr>

                                    </table>
                                </td>
                            </tr>
                        </table>
                    </body>
                    </html>
                    """
        subject = f"📦 Đơn đặt hàng #{po.po_number} từ E-Commerce"

        message = create_message(
            recipients=[supplier_email],
            subject=subject,
            body=html_message
        )

        await mail.send_message(message)
