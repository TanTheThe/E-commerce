from datetime import datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from src.config import Config
from src.crud.authentication.services.forgot_password.forgot_password_security import ForgotPasswordSecurityService
from src.crud.authentication.utils import create_url_safe_token, generate_password_hash
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.mail import mail, create_message
from src.schemas.user import ResetMethod, UserRole
import re
import secrets
import logging

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

user_repository = UserRepository()
forgot_password_security_service = ForgotPasswordSecurityService()

logger = logging.getLogger(__name__)

class ForgotPasswordService:
    async def forgot_password(self, email: str, check: ResetMethod, role: UserRole, session: AsyncSession):
        email = email.strip().lower()
        
        try:
            if not email:
                AuthException.email_required()

            if not re.match(EMAIL_REGEX, email):
                AuthException.invalid_email_format()
                
            await forgot_password_security_service.check_forgot_password_rate_limit(email)
            
            user = await self.find_and_validate_user(email, role, session)
            
            if check == ResetMethod.EMAIL:
                return await self.send_reset_email(user, role, session)
            elif check == ResetMethod.OTP:
                return await self.send_reset_otp(user, role, session)
            else:
                AuthException.invalid_reset_method()

        except Exception as e:
            logger.error(f"Forgot password failed for email {email}: {str(e)}")
            AuthException.forgot_password_failed()


    async def find_and_validate_user(self, email: str, role: UserRole, session: AsyncSession):
        condition = [
            User.email == email, User.deleted_at.is_(None), User.customer_status == "active"
        ]

        user = await user_repository.get_user(session=session, where_conditions=condition)

        if not user:
            AuthException.user_not_found()

        if not user.is_verified:
            AuthException.user_not_verified()

        if role == UserRole.ADMIN:
            if not user.is_admin:
                AuthException.unauthorized_admin()
        elif role == UserRole.STAFF:
            if not user.is_staff:
                AuthException.unauthorized_staff()
            if user.staff_status != "active":
                AuthException.staff_account_disabled()
        elif role == UserRole.CUSTOMER:
            if not user.is_customer:
                AuthException.unauthorized_customer()
            if user.customer_status != "active":
                AuthException.customer_account_disabled()

        return user


    async def send_reset_email(self, user, role: UserRole, session: AsyncSession):
        try:
            token_payload = {
                "email": user.email,
                "user_id": str(user.id),
                "timestamp": datetime.now().isoformat()
            }

            token = create_url_safe_token(
                token_payload,
                role.value,
                purpose="reset_password"
            )

            if role == UserRole.CUSTOMER:
                link = f"http://{Config.CUSTOMER_DOMAIN_CLIENT}/reset-password/{token}"
            else:
                link = f"http://{Config.ADMIN_DOMAIN_CLIENT}/reset-password/{token}"

            role_display = self.get_role_display(role)

            html_message = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        </head>
                        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px;">
                                <tr>
                                    <td align="center">
                                        <table width="600" cellpadding="0" cellspacing="0" style="background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                                            <!-- Header with gradient -->
                                            <tr>
                                                <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 40px 50px; text-align: center; position: relative;">
                                                    <div style="background: rgba(255,255,255,0.2); width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);">
                                                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 6C13.93 6 15.5 7.57 15.5 9.5C15.5 11.43 13.93 13 12 13C10.07 13 8.5 11.43 8.5 9.5C8.5 7.57 10.07 6 12 6ZM12 20C9.97 20 8.06 19.21 6.61 17.89C8.61 16.27 11.71 15.5 12 15.5C12.29 15.5 15.39 16.27 17.39 17.89C15.94 19.21 14.03 20 12 20Z" fill="white"/>
                                                        </svg>
                                                    </div>
                                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                                        Đặt lại mật khẩu
                                                    </h1>
                                                    <p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">
                                                        Tài khoản {role_display}
                                                    </p>
                                                </td>
                                            </tr>

                                            <!-- Content -->
                                            <tr>
                                                <td style="padding: 40px;">
                                                    <p style="margin: 0 0 16px; color: #333333; font-size: 16px; line-height: 1.6;">
                                                        Xin chào <strong style="color: #667eea;">{user.first_name} {user.last_name}</strong>,
                                                    </p>
                                                    <p style="margin: 0 0 24px; color: #666666; font-size: 15px; line-height: 1.6;">
                                                        Chúng tôi đã nhận được yêu cầu đặt lại mật khẩu cho tài khoản {role_display} của bạn. 
                                                        Nhấp vào nút bên dưới để tiếp tục:
                                                    </p>

                                                    <!-- CTA Button -->
                                                    <table width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 30px;">
                                                        <tr>
                                                            <td align="center" style="padding: 20px 0;">
                                                                <a href="{link}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 16px 48px; text-decoration: none; border-radius: 50px; display: inline-block; font-weight: 600; font-size: 16px; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); transition: all 0.3s;">
                                                                    🔐 Đặt lại mật khẩu
                                                                </a>
                                                            </td>
                                                        </tr>
                                                    </table>

                                                    <!-- Divider with text -->
                                                    <table width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px;">
                                                        <tr>
                                                            <td style="border-bottom: 1px solid #e0e0e0; position: relative; text-align: center; padding: 0 0 24px;">
                                                                <span style="background: #ffffff; padding: 0 16px; color: #999999; font-size: 13px; position: relative; top: 12px;">
                                                                    Hoặc copy link bên dưới
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    </table>

                                                    <!-- Link Box -->
                                                    <div style="background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%); border: 2px dashed #667eea; border-radius: 12px; padding: 20px; margin: 0 0 30px;">
                                                        <p style="margin: 0; color: #667eea; font-size: 13px; word-break: break-all; line-height: 1.6; font-family: 'Courier New', monospace;">
                                                            {link}
                                                        </p>
                                                    </div>

                                                    <!-- Info boxes -->
                                                    <div style="background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 8px; padding: 16px; margin: 0 0 16px;">
                                                        <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.5;">
                                                            ⏰ <strong>Lưu ý:</strong> Link này sẽ hết hạn sau <strong>1 giờ</strong> vì lý do bảo mật.
                                                        </p>
                                                    </div>

                                                    <div style="background: #e7f3ff; border-left: 4px solid #2196F3; border-radius: 8px; padding: 16px;">
                                                        <p style="margin: 0; color: #0c5460; font-size: 14px; line-height: 1.5;">
                                                            🛡️ Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này. Tài khoản của bạn vẫn an toàn.
                                                        </p>
                                                    </div>
                                                </td>
                                            </tr>

                                            <!-- Footer -->
                                            <tr>
                                                <td style="background: #f8f9fa; padding: 30px 40px; border-top: 1px solid #e9ecef;">
                                                    <p style="margin: 0 0 8px; color: #666666; font-size: 14px;">
                                                        Trân trọng,
                                                    </p>
                                                    <p style="margin: 0; color: #667eea; font-size: 15px; font-weight: 600;">
                                                        Đội ngũ hỗ trợ E-Commerce
                                                    </p>
                                                    <p style="margin: 16px 0 0; color: #999999; font-size: 12px;">
                                                        © 2024 E-Commerce. All rights reserved.
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

            subject = f"🔐 Đặt lại mật khẩu tài khoản {role_display}"

            message = create_message(
                recipients=[user.email],
                subject=subject,
                body=html_message
            )

            await mail.send_message(message)

            return f"Vui lòng kiểm tra email của bạn để biết hướng dẫn đặt lại mật khẩu {role_display}"

        except Exception as e:
            logger.error("Send reset email error: ", e)
            AuthException.email_send_failed()


    async def send_reset_otp(self, user, role: UserRole, session: AsyncSession):
        try:
            otp = await forgot_password_security_service.generate_and_store_otp(
                user_id=str(user.id),
                email=user.email
            )

            role_display = self.get_role_display(role)

            html_message = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        </head>
                        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 40px 20px;">
                                <tr>
                                    <td align="center">
                                        <table width="600" cellpadding="0" cellspacing="0" style="background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                                            <!-- Header with gradient -->
                                            <tr>
                                                <td style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 40px 40px 50px; text-align: center; position: relative;">
                                                    <div style="background: rgba(255,255,255,0.2); width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);">
                                                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                            <path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1ZM10 17L6 13L7.41 11.59L10 14.17L16.59 7.58L18 9L10 17Z" fill="white"/>
                                                        </svg>
                                                    </div>
                                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                                        Mã xác thực OTP
                                                    </h1>
                                                    <p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">
                                                        Đặt lại mật khẩu {role_display}
                                                    </p>
                                                </td>
                                            </tr>

                                            <!-- Content -->
                                            <tr>
                                                <td style="padding: 40px;">
                                                    <p style="margin: 0 0 16px; color: #333333; font-size: 16px; line-height: 1.6;">
                                                        Xin chào <strong style="color: #11998e;">{user.first_name} {user.last_name}</strong>,
                                                    </p>
                                                    <p style="margin: 0 0 32px; color: #666666; font-size: 15px; line-height: 1.6;">
                                                        Đây là mã OTP để đặt lại mật khẩu tài khoản {role_display} của bạn:
                                                    </p>

                                                    <!-- OTP Display -->
                                                    <table width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 32px;">
                                                        <tr>
                                                            <td align="center">
                                                                <div style="background: linear-gradient(135deg, #f0fff4 0%, #e0f7ef 100%); border: 3px dashed #11998e; border-radius: 16px; padding: 32px; display: inline-block; box-shadow: 0 8px 24px rgba(17, 153, 142, 0.15);">
                                                                    <div style="margin: 0 0 12px;">
                                                                        <span style="font-size: 14px; color: #11998e; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                                                            Mã xác thực
                                                                        </span>
                                                                    </div>
                                                                    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 48px; font-weight: 700; letter-spacing: 12px; font-family: 'Courier New', monospace; padding: 8px 0;">
                                                                        {otp}
                                                                    </div>
                                                                    <div style="margin: 12px 0 0;">
                                                                        <div style="display: inline-flex; align-items: center; background: rgba(17, 153, 142, 0.1); padding: 8px 16px; border-radius: 20px;">
                                                                            <span style="color: #e74c3c; font-weight: 600; font-size: 13px;">
                                                                                ⏱️ Có hiệu lực trong 5 phút
                                                                            </span>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </td>
                                                        </tr>
                                                    </table>

                                                    <!-- Instructions -->
                                                    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f0f4ff 100%); border-radius: 12px; padding: 24px; margin: 0 0 20px; border-left: 4px solid #2196F3;">
                                                        <p style="margin: 0 0 12px; color: #1976D2; font-size: 15px; font-weight: 600;">
                                                            📝 Hướng dẫn sử dụng:
                                                        </p>
                                                        <ol style="margin: 0; padding-left: 20px; color: #555555; font-size: 14px; line-height: 1.8;">
                                                            <li>Truy cập trang đặt lại mật khẩu</li>
                                                            <li>Nhập mã OTP bên trên</li>
                                                            <li>Tạo mật khẩu mới cho tài khoản của bạn</li>
                                                        </ol>
                                                    </div>

                                                    <!-- Warning Box -->
                                                    <div style="background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; padding: 16px; margin: 0 0 16px;">
                                                        <p style="margin: 0; color: #e65100; font-size: 14px; line-height: 1.5;">
                                                            ⚠️ <strong>Quan trọng:</strong> Không chia sẻ mã OTP này với bất kỳ ai, kể cả nhân viên hỗ trợ.
                                                        </p>
                                                    </div>

                                                    <div style="background: #f3f4f6; border-left: 4px solid #6b7280; border-radius: 8px; padding: 16px;">
                                                        <p style="margin: 0; color: #4b5563; font-size: 14px; line-height: 1.5;">
                                                            💡 Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này và kiểm tra bảo mật tài khoản.
                                                        </p>
                                                    </div>
                                                </td>
                                            </tr>

                                            <!-- Footer -->
                                            <tr>
                                                <td style="background: #f8f9fa; padding: 30px 40px; border-top: 1px solid #e9ecef;">
                                                    <p style="margin: 0 0 8px; color: #666666; font-size: 14px;">
                                                        Trân trọng,
                                                    </p>
                                                    <p style="margin: 0; color: #11998e; font-size: 15px; font-weight: 600;">
                                                        Đội ngũ hỗ trợ E-Commerce
                                                    </p>
                                                    <p style="margin: 16px 0 0; color: #999999; font-size: 12px;">
                                                        © 2024 E-Commerce. All rights reserved.
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

            subject = f"🔐 Mã OTP đặt lại mật khẩu {role_display} - {otp}"

            message = create_message(
                recipients=[user.email],
                subject=subject,
                body=html_message
            )

            await mail.send_message(message)

            return f"Vui lòng kiểm tra email để lấy mã OTP đặt lại mật khẩu {role_display}"

        except Exception as e:
            logger.error(f"Failed to send reset OTP: {str(e)}")
            AuthException.otp_send_failed()
            
    
    def get_role_display(self, role: UserRole):
        role_mapping = {
            UserRole.ADMIN: "quản trị viên",
            UserRole.STAFF: "nhân viên",
            UserRole.CUSTOMER: "khách hàng"
        }
        return role_mapping.get(role, "người dùng")













