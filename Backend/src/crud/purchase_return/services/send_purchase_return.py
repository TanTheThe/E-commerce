from datetime import datetime
from typing import Optional
from src.crud.purchase_return.services.utils_service import UtilsPRService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import PurchaseReturn
from src.errors.purchase_return import PurchaseReturnException
from src.mail import create_message, mail


utils_pr_service = UtilsPRService()


class SendPurchaseReturnService:
    async def send_return_email_to_supplier(self, session: AsyncSession, purchase_return_id: str,
                                            supplier_email: Optional[str] = None):
        pr = await utils_pr_service.validate_and_get_pr(session, purchase_return_id)

        if pr.status != "approved":
            PurchaseReturnException.only_send_mail_when_approved()

        if not supplier_email:
            if pr.supplier and pr.supplier.email:
                supplier_email = pr.supplier.email
            else:
                PurchaseReturnException.supplier_email_not_found()

        await self.send_pr_email_to_supplier(
            pr=pr,
            supplier_email=supplier_email
        )

        pr.status = "sent"
        pr.notes = (pr.notes or "") + \
            f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] Đã gửi email cho NCC: {supplier_email}"
        pr.updated_at = datetime.now()

        await session.commit()

        return {
            "id": str(pr.id),
            "return_number": pr.return_number,
            "supplier_email": supplier_email,
            "delivery_note_number": pr.delivery_note_number,
            "status": pr.status
        }

    async def send_pr_email_to_supplier(self, pr: PurchaseReturn, supplier_email: str):
        def format_currency(amount: int):
            return f"{amount:,}".replace(",", ".")

        items_html = ""
        for idx, detail in enumerate(pr.return_details, 1):
            variant_info = ""
            product_name = "N/A"

            if detail.product_variant:
                variant_info = f"{detail.product_variant.sku}"
                if detail.product_variant.size:
                    variant_info += f" - Size {detail.product_variant.size}"
                if detail.product_variant.color_name:
                    variant_info += f" - {detail.product_variant.color_name}"

                if detail.product_variant.product:
                    product_name = detail.product_variant.product.name

            condition_label = {
                "damaged": "Hư hỏng",
                "defective": "Lỗi kỹ thuật",
                "expired": "Hết hạn",
                "wrong_item": "Sai hàng"
            }.get(detail.condition, detail.condition)

            items_html += f"""
                <tr style="border-bottom: 1px solid #e8e8e8;">
                    <td style="padding: 14px 10px; text-align: center; color: #666;">{idx}</td>
                    <td style="padding: 14px 10px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div>
                                <div style="font-weight: 600; color: #2c3e50; margin-bottom: 4px;">{product_name}</div>
                                <div style="color: #7f8c8d; font-size: 13px;">{variant_info}</div>
                                <div style="color: #e74c3c; font-size: 12px; margin-top: 4px;">🔴 {condition_label}</div>
                            </div>
                        </div>
                    </td>
                    <td style="padding: 14px 10px; text-align: center; color: #e74c3c; font-weight: 600;">{detail.return_quantity}</td>
                    <td style="padding: 14px 10px; text-align: right; color: #34495e;">{format_currency(detail.unit_cost)} đ</td>
                    <td style="padding: 14px 10px; text-align: right; color: #e74c3c; font-weight: 600;">{format_currency(detail.total_cost)} đ</td>
                </tr>
                """

        gr_number = pr.goods_receipt.receipt_number if pr.goods_receipt else "N/A"
        po_number = pr.purchase_order.po_number if pr.purchase_order else "N/A"

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
                                <td style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 40px 30px; text-align: center;">
                                    <div style="font-size: 48px; margin-bottom: 10px;">↩️</div>
                                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 600; letter-spacing: -0.5px;">Thông Báo Hoàn Trả</h1>
                                    <p style="color: rgba(255,255,255,0.9); margin: 12px 0 0 0; font-size: 16px;">#{pr.return_number}</p>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px 35px;">
                                    
                                    <p style="font-size: 17px; color: #2c3e50; line-height: 1.6; margin: 0 0 10px 0;">
                                        Kính gửi <strong style="color: #e74c3c;">{pr.supplier.name if pr.supplier else 'Quý Nhà cung cấp'}</strong>,
                                    </p>
                                    
                                    <p style="font-size: 15px; color: #5a6c7d; line-height: 1.7; margin: 0 0 35px 0;">
                                        Chúng tôi xin thông báo về việc hoàn trả hàng hóa từ đơn hàng <strong>{po_number}</strong>. 
                                        Vui lòng xem thông tin chi tiết bên dưới và liên hệ với chúng tôi để sắp xếp việc nhận hàng trả.
                                    </p>
                                    
                                    <!-- Alert Box -->
                                    <div style="background: linear-gradient(to right, #fff5f5, #ffffff); border-left: 4px solid #e74c3c; border-radius: 8px; padding: 20px; margin-bottom: 30px;">
                                        <div style="display: flex; align-items: center; margin-bottom: 12px;">
                                            <span style="font-size: 24px; margin-right: 12px;">⚠️</span>
                                            <strong style="color: #c0392b; font-size: 16px;">Lý do hoàn trả:</strong>
                                        </div>
                                        <p style="color: #5a6c7d; margin: 0; font-size: 14px; line-height: 1.6; padding-left: 36px;">{pr.return_reason}</p>
                                    </div>
                                    
                                    <!-- Thông tin phiếu hoàn trả -->
                                    <div style="background: linear-gradient(to right, #f8f9fa, #ffffff); border-radius: 10px; padding: 25px; margin-bottom: 35px; border-left: 4px solid #e74c3c;">
                                        <h3 style="color: #2c3e50; font-size: 16px; margin: 0 0 20px 0; font-weight: 600;">📋 Thông tin phiếu hoàn trả</h3>
                                        <table width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px; width: 45%;">
                                                    <span style="display: inline-block; width: 20px;">📄</span> Mã phiếu hoàn trả
                                                </td>
                                                <td style="padding: 8px 0; color: #2c3e50; font-weight: 600; font-size: 14px;">{pr.return_number}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px;">
                                                    <span style="display: inline-block; width: 20px;">🔢</span> Mã phiếu giao nhận
                                                </td>
                                                <td style="padding: 8px 0; color: #e74c3c; font-weight: 700; font-size: 16px;">{pr.delivery_note_number}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px;">
                                                    <span style="display: inline-block; width: 20px;">📦</span> Đơn hàng gốc
                                                </td>
                                                <td style="padding: 8px 0; color: #2c3e50; font-weight: 600; font-size: 14px;">{po_number}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px;">
                                                    <span style="display: inline-block; width: 20px;">📥</span> Phiếu nhập hàng
                                                </td>
                                                <td style="padding: 8px 0; color: #2c3e50; font-weight: 600; font-size: 14px;">{gr_number}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px;">
                                                    <span style="display: inline-block; width: 20px;">📅</span> Ngày tạo phiếu
                                                </td>
                                                <td style="padding: 8px 0; color: #2c3e50; font-weight: 600; font-size: 14px;">{pr.return_date.strftime('%d/%m/%Y lúc %H:%M')}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #7f8c8d; font-size: 14px;">
                                                    <span style="display: inline-block; width: 20px;">🏢</span> Kho gửi hàng
                                                </td>
                                                <td style="padding: 8px 0; color: #2c3e50; font-weight: 600; font-size: 14px;">{pr.warehouse.name if pr.warehouse else 'Chưa xác định'}</td>
                                            </tr>
                                        </table>
                                    </div>
                                    
                                    <!-- Chi tiết sản phẩm hoàn trả -->
                                    <h3 style="color: #2c3e50; font-size: 18px; margin: 0 0 20px 0; font-weight: 600; display: flex; align-items: center;">
                                        <span style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; width: 32px; height: 32px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 16px;">📦</span>
                                        Chi tiết sản phẩm hoàn trả
                                    </h3>
                                    
                                    <table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #e8e8e8; border-radius: 8px; overflow: hidden;">
                                        <thead>
                                            <tr style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
                                                <th style="padding: 14px 10px; text-align: center; color: white; font-size: 13px; font-weight: 600; width: 6%;">STT</th>
                                                <th style="padding: 14px 10px; text-align: left; color: white; font-size: 13px; font-weight: 600; width: 38%;">Sản phẩm</th>
                                                <th style="padding: 14px 10px; text-align: center; color: white; font-size: 13px; font-weight: 600; width: 14%;">SL trả</th>
                                                <th style="padding: 14px 10px; text-align: right; color: white; font-size: 13px; font-weight: 600; width: 20%;">Đơn giá</th>
                                                <th style="padding: 14px 10px; text-align: right; color: white; font-size: 13px; font-weight: 600; width: 22%;">Thành tiền</th>
                                            </tr>
                                        </thead>
                                        <tbody style="background-color: #ffffff;">
                                            {items_html}
                                        </tbody>
                                    </table>
                                    
                                    <!-- Tổng cộng -->
                                    <div style="margin-top: 25px; padding: 20px; background: linear-gradient(to right, #fff5f5, #ffffff); border-radius: 8px; border: 1px solid #ffebee;">
                                        <table width="100%" cellpadding="0" cellspacing="0">
                                            <tr style="border-top: 2px solid #e74c3c;">
                                                <td style="text-align: right; padding: 15px 0 5px 0; font-size: 16px; font-weight: 600; color: #2c3e50;">TỔNG GIÁ TRỊ HOÀN TRẢ:</td>
                                                <td style="text-align: right; padding: 15px 0 5px 0; font-weight: 700; font-size: 24px; color: #e74c3c; width: 180px;">{format_currency(pr.total_return_amount)} đ</td>
                                            </tr>
                                        </table>
                                    </div>
                                    
                                    <!-- Ghi chú -->
                                    {f'''
                                    <div style="margin: 30px 0; padding: 18px 20px; background: linear-gradient(to right, #fff8e1, #ffffff); border-left: 4px solid #ffa726; border-radius: 6px;">
                                        <div style="display: flex; align-items: flex-start;">
                                            <span style="font-size: 20px; margin-right: 10px;">💬</span>
                                            <div>
                                                <strong style="color: #e65100; font-size: 14px; display: block; margin-bottom: 8px;">Ghi chú:</strong>
                                                <p style="color: #5d4037; margin: 0; font-size: 14px; line-height: 1.6;">{pr.notes}</p>
                                            </div>
                                        </div>
                                    </div>
                                    ''' if pr.notes else ''}

                                    <!-- Footer note -->
                                    <div style="margin-top: 40px; padding-top: 25px; border-top: 2px solid #f0f0f0;">
                                        <p style="font-size: 15px; color: #5a6c7d; line-height: 1.7; margin: 0 0 20px 0;">
                                            Vui lòng kiểm tra kỹ thông tin và sắp xếp thời gian nhận hàng trả.
                                            Sau khi nhận hàng, xin vui lòng xác nhận với chúng tôi để hoàn tất thủ tục.
                                        </p>
                                        <div style="background: linear-gradient(to right, #f8f9fa, #ffffff); padding: 20px; border-radius: 8px; margin-top: 20px;">
                                            <p style="font-size: 15px; color: #2c3e50; margin: 0; line-height: 1.8;">
                                                Trân trọng,<br>
                                                <strong style="color: #e74c3c; font-size: 16px;">Phòng Mua hàng</strong><br>
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

        subject = f"↩️ Thông báo hoàn trả #{pr.return_number} - Delivery Note: {pr.delivery_note_number}"

        message = create_message(
            recipients=[supplier_email],
            subject=subject,
            body=html_message
        )

        await mail.send_message(message)
