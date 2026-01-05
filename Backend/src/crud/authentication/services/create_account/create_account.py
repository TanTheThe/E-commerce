from datetime import datetime, timedelta
from src.crud.authentication.services.create_account.create_account_security import CreateAccountSecurityService
from src.database.models import User
from src.errors.authentication import AuthException
from src.errors.user import UserException
from src.schemas.user import UserCreateModel, UserRole
from src.crud.authentication.utils import create_url_safe_token, generate_password_hash
from src.mail import create_message, mail
from fastapi import BackgroundTasks, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from src.config import Config
from src.crud.user.repositories import UserRepository
import logging

user_repository = UserRepository()
create_account_security_service = CreateAccountSecurityService()

logger = logging.getLogger(__name__)

class CreateAccountService:
    async def create_user_account(self, user_data: UserCreateModel, role: UserRole, bg_tasks: BackgroundTasks, 
                                  session: AsyncSession, request: Request = None):
        email = user_data.email.strip().lower()
        
        try:
            if request:
                ip_address = self.get_client_ip(request)
                await create_account_security_service.check_signup_rate_limit(ip_address)
                
            await create_account_security_service.check_email_signup_cooldown(email)

            condition = [User.email == email, User.deleted_at.is_(None)]
            user_exists = await user_repository.get_user(session=session, where_conditions=condition)

            if user_exists:
                if user_exists.is_verified:
                    UserException.email_exists()
                if user_exists.created_at and (datetime.now() - user_exists.created_at) > timedelta(hours=24):
                    condition_delete = [User.id == user_exists.id]
                    await user_repository.delete_user(session=session, where_conditions=condition_delete)
                else:
                    AuthException.email_already_registered()

            try:
                password_hash = generate_password_hash(user_data.password)
                user_create_data = {
                    **user_data.model_dump(),
                    "password": password_hash,
                    'email': email,
                    'is_verified': False,
                    'created_at': datetime.now(),
                }

                if role == UserRole.CUSTOMER:
                    user_create_data['is_customer'] = True
                    user_create_data['customer_status'] = "active"
                elif role == UserRole.STAFF:
                    user_create_data['is_staff'] = True
                    user_create_data['staff_status'] = "active"

                new_user = await user_repository.create_user(user_create_data, session)
                await session.commit()

            except Exception as e:
                await session.rollback()
                logger.error(f"Error creating user account: {str(e)}")
                raise AuthException.creation_failed()

            token_payload = {
                "email": email,
                "user_id": str(new_user.id),
                "timestamp": datetime.now().isoformat()
            }

            token = create_url_safe_token(
                token_payload,
                role.value,
                purpose="create_account"
            )
            
            await create_account_security_service.cache_verification_token(
                token=token,
                user_id=str(new_user.id),
                email=email,
                ttl=86400
            )
        
            link = f"http://{Config.DOMAIN}/api/v1/{role.value}/auth/verify/{token}"
        
            subject, html = self.create_verification_email_content(link, role)
        
            message = create_message(
                recipients=[email],
                subject=subject,
                body=html
            )
        
            bg_tasks.add_task(mail.send_message, message)
            
            await create_account_security_service.set_email_signup_cooldown(
                email=email,
                cooldown_minutes=5
            )

            return {
                "id": str(new_user.id), 
                "email": new_user.email, 
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "role": role.value
            }
        except Exception as e:
            logger.error(f"Signup failed for email {email}: {str(e)}")
            raise
        
        
    def create_verification_email_content(self, link: str, role: UserRole):
        if role == UserRole.CUSTOMER:
            subject = "Xác thực tài khoản khách hàng"
            role_text = "khách hàng"
            role_color = "#4F46E5"
            role_icon = "👤"
        else:
            subject = "Xác thực tài khoản nhân viên"
            role_text = "nhân viên"
            role_color = "#7C3AED"
            role_icon = "👔"

        html = f"""
            <!DOCTYPE html>
            <html lang="vi">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Xác thực email</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
                <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 0; padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <!-- Main Container -->
                            <table role="presentation" style="max-width: 600px; width: 100%; background: #ffffff; border-radius: 24px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); overflow: hidden;">
                                <!-- Header with gradient -->
                                <tr>
                                    <td style="background: linear-gradient(135deg, {role_color} 0%, #EC4899 100%); padding: 50px 40px; text-align: center;">
                                        <div style="font-size: 64px; margin-bottom: 16px;">{role_icon}</div>
                                        <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;">Xác thực email</h1>
                                        <p style="margin: 12px 0 0 0; color: rgba(255, 255, 255, 0.9); font-size: 16px;">Chào mừng bạn đến với hệ thống</p>
                                    </td>
                                </tr>

                                <!-- Content -->
                                <tr>
                                    <td style="padding: 50px 40px;">
                                        <p style="margin: 0 0 20px 0; color: #374151; font-size: 16px; line-height: 1.6;">
                                            Xin chào! 👋
                                        </p>
                                        <p style="margin: 0 0 20px 0; color: #374151; font-size: 16px; line-height: 1.6;">
                                            Cảm ơn bạn đã đăng ký tài khoản <strong style="color: {role_color};">{role_text}</strong>. 
                                            Chỉ còn một bước nữa để hoàn tất!
                                        </p>
                                        <p style="margin: 0 0 32px 0; color: #6B7280; font-size: 15px; line-height: 1.6;">
                                            Vui lòng nhấp vào nút bên dưới để xác thực địa chỉ email của bạn:
                                        </p>

                                        <!-- CTA Button -->
                                        <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td align="center" style="padding: 0 0 32px 0;">
                                                    <a href="{link}" style="display: inline-block; background: linear-gradient(135deg, {role_color} 0%, #EC4899 100%); color: #ffffff; text-decoration: none; padding: 18px 48px; border-radius: 12px; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3); transition: transform 0.2s;">
                                                        ✓ Xác thực email ngay
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>

                                        <!-- Divider -->
                                        <div style="border-top: 2px solid #F3F4F6; margin: 32px 0; position: relative;">
                                            <span style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #ffffff; padding: 0 16px; color: #9CA3AF; font-size: 13px; font-weight: 500;">HOẶC</span>
                                        </div>

                                        <!-- Alternative link -->
                                        <p style="margin: 32px 0 8px 0; color: #6B7280; font-size: 14px;">
                                            Copy và paste đường link sau vào trình duyệt:
                                        </p>
                                        <div style="background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; word-break: break-all;">
                                            <a href="{link}" style="color: {role_color}; text-decoration: none; font-size: 13px; font-family: 'Courier New', monospace;">
                                                {link}
                                            </a>
                                        </div>

                                        <!-- Warning box -->
                                        <div style="background: #FEF3C7; border-left: 4px solid #F59E0B; border-radius: 8px; padding: 16px; margin-top: 32px;">
                                            <p style="margin: 0; color: #92400E; font-size: 14px; line-height: 1.5;">
                                                <strong>⏰ Lưu ý:</strong> Link xác thực sẽ hết hạn sau <strong>24 giờ</strong>. Vui lòng xác thực sớm để không bỏ lỡ!
                                            </p>
                                        </div>
                                    </td>
                                </tr>

                                <!-- Footer -->
                                <tr>
                                    <td style="background: #F9FAFB; padding: 40px; text-align: center; border-top: 1px solid #E5E7EB;">
                                        <p style="margin: 0 0 8px 0; color: #6B7280; font-size: 14px;">
                                            Nếu bạn không đăng ký tài khoản này, vui lòng bỏ qua email này.
                                        </p>
                                        <p style="margin: 16px 0 0 0; color: #9CA3AF; font-size: 13px;">
                                            Trân trọng,<br>
                                            <strong style="color: {role_color};">Đội ngũ hỗ trợ</strong>
                                        </p>
                                        <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid #E5E7EB;">
                                            <p style="margin: 0; color: #9CA3AF; font-size: 12px;">
                                                © 2024 - Bản quyền thuộc về hệ thống
                                            </p>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
        
        return subject, html
    
    
    @staticmethod
    def get_client_ip(request: Request):
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"
