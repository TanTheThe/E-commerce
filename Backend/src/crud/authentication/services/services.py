from datetime import timedelta, datetime
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse
import random
from src.config import Config
from src.crud.user.services import user_repository
from src.database.models import User
from sqlmodel import and_
from src.crud.authentication.utils import verify_password, create_access_token, create_url_safe_token, \
    decode_url_safe_token, generate_password_hash
import pyotp
import qrcode
from io import BytesIO
import base64
# from src.database.redis import add_jti_to_blocklist
from src.mail import create_message, mail
from src.schemas.user import ForgotPasswordConfirmModel, LoginAdminModel, ResetMethod, UserLoginModel, Setup2FA, UserRole, VerifyLoginAdminModel, VerifyOTPModel
from src.errors.authentication import AuthException

REFRESH_TOKEN_EXPIRY = 2

class AuthenticationService:
    # async def revoke_token_service(self, token_details, request):
    #     jti = token_details['jti']
    #     await add_jti_to_blocklist(jti, request)


    async def forgot_password_service(self, email: str, check: ResetMethod, role: UserRole, session: AsyncSession):
        if not email or not email.strip():
            AuthException.email_required()

        email = email.strip().lower()

        try:
            user = await self.find_and_validate_user(email, role, session)
            
            if check == ResetMethod.EMAIL:
                return await self.send_reset_email(user, role, session)
            elif check == ResetMethod.OTP:
                return await self.send_reset_otp(user, role, session)
            else:
                AuthException.invalid_reset_method()
                
        except HTTPException:
            raise
        except Exception as e:
            AuthException.forgot_password_failed()
            
            
    async def find_and_validate_user(self, email: str, role: UserRole, session: AsyncSession):
        condition = and_(User.email == email, User.deleted_at.is_(None))
        user = await user_repository.get_user(condition, session)
        
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
                "timestamp": datetime.utcnow().isoformat()
            }
            
            token = create_url_safe_token(
                token_payload, 
                role.value, 
                purpose="reset_password"
            )
            
            if role == UserRole.CUSTOMER:
                link = f"http://{Config.DOMAIN_CLIENT}/reset-password/{token}"
            else:
                link = f"http://{Config.DOMAIN_CLIENT}/reset-password/{token}"

            role_display = self.get_role_display(role)
            
            html_message = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #333;">Đặt lại mật khẩu {role_display}</h1>
                <p>Xin chào {user.first_name} {user.last_name},</p>
                <p>Chúng tôi đã nhận được yêu cầu đặt lại mật khẩu cho tài khoản {role_display} của bạn.</p>
                <p>Vui lòng nhấp vào nút bên dưới để đặt lại mật khẩu:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" 
                       style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Đặt lại mật khẩu
                    </a>
                </div>
                <p>Hoặc copy và paste link sau vào trình duyệt:</p>
                <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 3px;">
                    {link}
                </p>
                <p style="color: #666; font-size: 14px;">
                    Link này sẽ hết hạn sau 1 giờ vì lý do bảo mật.
                </p>
                <p style="color: #666; font-size: 14px;">
                    Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
                </p>
                <hr style="border: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Trân trọng,<br>
                    Đội ngũ hỗ trợ "E-Commerce"
                </p>
            </div>
            """
            
            subject = f"Đặt lại mật khẩu tài khoản {role_display}"
            
            message = create_message(
                recipients=[user.email],
                subject=subject,
                body=html_message
            )
            
            await mail.send_message(message)
            
            return f"Vui lòng kiểm tra email của bạn để biết hướng dẫn đặt lại mật khẩu {role_display}"
            
        except Exception as e:
            AuthException.email_send_failed()
            
            
    async def send_reset_otp(self, user, role: UserRole, session: AsyncSession):
        try:
            otp = str(random.randint(100000, 999999))
            expires_at = datetime.utcnow() + timedelta(minutes=5)
            
            update_data = {
                'otp': otp,
                'expires_at': expires_at,
                'updated_at': datetime.now()
            }
            
            condition = and_(User.id == user.id, User.deleted_at.is_(None))
            await user_repository.update_user_some_field(condition, update_data, session)
            
            role_display = self.get_role_display(role)
            
            html_message = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #333;">Mã OTP đặt lại mật khẩu {role_display}</h1>
                <p>Xin chào {user.first_name} {user.last_name},</p>
                <p>Mã OTP để đặt lại mật khẩu tài khoản {role_display} của bạn là:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <div style="background-color: #f0f8ff; border: 2px dashed #4CAF50; 
                                padding: 20px; border-radius: 10px; display: inline-block;">
                        <span style="font-size: 32px; font-weight: bold; color: #4CAF50; 
                                     letter-spacing: 5px;">{otp}</span>
                    </div>
                </div>
                <p style="color: #e74c3c; font-weight: bold;">
                    Mã có hiệu lực trong 5 phút.
                </p>
                <p style="color: #666; font-size: 14px;">
                    Vui lòng nhập mã này vào trang đặt lại mật khẩu để xác thực danh tính của bạn.
                </p>
                <p style="color: #666; font-size: 14px;">
                    Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
                </p>
                <hr style="border: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Trân trọng,<br>
                    Đội ngũ hỗ trợ "E-Commerce"
                </p>
            </div>
            """
            
            subject = f"Mã OTP đặt lại mật khẩu {role_display} - {otp}"
            
            message = create_message(
                recipients=[user.email],
                subject=subject,
                body=html_message
            )
            
            await mail.send_message(message)
            
            return f"Vui lòng kiểm tra email để lấy mã OTP đặt lại mật khẩu {role_display}"
            
        except Exception as e:
            await session.rollback()
            AuthException.otp_send_failed()


    async def forgot_password_confirm_service(self, data: ForgotPasswordConfirmModel, role: UserRole, session: AsyncSession):
        try:
            token_data = decode_url_safe_token(
                data.token, 
                role.value, 
                purpose="reset_password"
            )
            
            user_email = token_data.get("email")
            user_id = token_data.get("user_id")
            
            if not user_email:
                AuthException.token_invalid()

            condition = and_(User.email == user_email, User.deleted_at.is_(None))
            user = await user_repository.get_user(condition, session)
            
            if not user:
                AuthException.user_not_found()
            
            if user_id and str(user.id) != user_id:
                AuthException.token_invalid()

            await self.validate_user_role(user, role)

            self.validate_password_strength(data.new_password)

            if verify_password(data.new_password, user.password):
                AuthException.same_password_error()

            password_hash = generate_password_hash(data.new_password)
            
            update_data = {
                'password': password_hash,
                'otp': None,
                'expires_at': None,
                'updated_at': datetime.now()
            }
            
            await user_repository.update_user_some_field(condition, update_data, session)
            
            role_display = self.get_role_display(role)
            
            return f"Đổi mật khẩu {role_display} thành công"
            
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            AuthException.forgot_password_failed()


    async def verify_otp(self, data: VerifyOTPModel, role: UserRole, session: AsyncSession):
        try:
            if not data.email or not data.otp:
                AuthException.otp_and_email_required()

            email = data.email.strip().lower()
            
            condition = and_(User.email == email, User.deleted_at.is_(None))
            user = await user_repository.get_user(condition, session)
            
            if not user:
                AuthException.user_not_found()

            await self.validate_user_role(user, role)

            if not user.otp:
                AuthException.otp_not_found()
                
            if user.otp != data.otp.strip():
                AuthException.invalid_otp()

            if not user.expires_at or datetime.utcnow() > user.expires_at:
                AuthException.otp_expired()

            update_data = {
                'otp': None,
                'expires_at': None,
                'updated_at': datetime.now()
            }
            
            condition_update = and_(User.id == user.id, User.deleted_at.is_(None))            
            await user_repository.update_user_some_field(condition_update, update_data, session)

            token_payload = {
                "email": user.email,
                "user_id": str(user.id),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            token = create_url_safe_token(
                token_payload, 
                role.value, 
                purpose='reset_password'
            )
            
            return token
            
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            AuthException.otp_verification_failed()
            
        
    async def validate_user_role(self, user, role: UserRole):
        if role == UserRole.ADMIN and not user.is_admin:
            AuthException.unauthorized_admin()
        elif role == UserRole.STAFF and not user.is_staff:
            AuthException.unauthorized_staff()
        elif role == UserRole.CUSTOMER and not user.is_customer:
            AuthException.unauthorized_customer()
        
        if role == UserRole.STAFF and user.staff_status != "active":
            AuthException.staff_account_disabled()
        elif role == UserRole.CUSTOMER and user.customer_status != "active":
            AuthException.customer_account_disabled()
        
        if user.deleted_at is not None:
            AuthException.account_deleted()


    def validate_password_strength(self, password: str):
        if len(password) < 8:
            AuthException.password_too_short()
        
        if len(password) > 100:
            AuthException.password_too_long()
        
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            AuthException.password_too_weak()


    def get_role_display(self, role: UserRole) -> str:
        role_mapping = {
            UserRole.ADMIN: "quản trị viên",
            UserRole.STAFF: "nhân viên", 
            UserRole.CUSTOMER: "khách hàng"
        }
        return role_mapping.get(role, "người dùng")
