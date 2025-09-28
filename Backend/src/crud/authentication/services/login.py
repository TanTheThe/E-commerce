from datetime import timedelta, datetime
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse
from src.crud.user.services import user_repository
from src.database.models import User
from sqlmodel import and_
from src.crud.authentication.utils import verify_password, create_access_token, create_url_safe_token, \
    decode_url_safe_token
import pyotp
import qrcode
from io import BytesIO
import base64
from src.schemas.user import AdminStaffRole, UserLoginModel, Setup2FA, VerifyLoginAdminModel
from src.errors.authentication import AuthException

REFRESH_TOKEN_EXPIRY = 2

class LoginService:
    async def login_admin_staff(self, user_data: UserLoginModel, role: AdminStaffRole, session: AsyncSession):
        email = user_data.email
        password = user_data.password

        try:
            condition = and_(User.email == email)
            user = await user_repository.get_user(condition, session)
            
            if not user:
                AuthException.invalid_account()

            password_valid = verify_password(password, user.password)
            if not password_valid:
                AuthException.invalid_account()

            if not user.is_verified:
                AuthException.user_not_verified()

            if role == AdminStaffRole.ADMIN:
                if not user.is_admin:
                    AuthException.unauthorized_admin()
            elif role == AdminStaffRole.STAFF:
                if not user.is_staff:
                    AuthException.unauthorized_staff()
                if user.staff_status != "active":
                    AuthException.staff_account_disabled()

            token = create_url_safe_token(
                {"id": str(user.id), "email": user.email}, 
                role=role.value, 
                purpose='first_class_login'
            )
            
            role_display = "quản trị viên" if role == AdminStaffRole.ADMIN else "nhân viên"
            
            if not user.two_fa_secret or not user.two_fa_enabled:
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": f"Lần đăng nhập {role_display} đầu tiên, vui lòng thiết lập 2FA",
                        "data": {
                            "isFirstLogin": True,
                            "token": token,
                            "requiresSetup": True,
                            "role": role.value
                        }
                    }
                )
            else:
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": f"Vui lòng nhập mã OTP để tiếp tục đăng nhập {role_display}",
                        "data": {
                            "isFirstLogin": False,
                            "token": token,
                            "requiresSetup": False,
                            "role": role.value
                        }
                    }
                )
        except HTTPException:
            raise
        except Exception as e:
            AuthException.login_failed()
        

    async def setup_2fa(self, user_data: Setup2FA, role: AdminStaffRole, session: AsyncSession):
        try:
            token_data = decode_url_safe_token(
                user_data.token, 
                role=role.value, 
                purpose="first_class_login"
            )
            
            user_id = token_data.get("id")
            if not user_id:
                AuthException.token_invalid() 
                
            condition = and_(User.id == user_id, User.deleted_at.is_(None))
            user = await user_repository.get_user(condition, session)
            if not user:
                AuthException.invalid_account()   
                
            if role == AdminStaffRole.ADMIN and not user.is_admin:
                AuthException.unauthorized_admin()
            elif role == AdminStaffRole.STAFF and not user.is_staff:
                AuthException.unauthorized_staff()
                
            if user.two_fa_secret and user.two_fa_enabled:
                AuthException.two_fa_already_setup()
                
            secret = pyotp.random_base32()
            
            update_data = {
                'two_fa_secret': secret,
                'two_fa_enabled': True,
                'updated_at': datetime.now()
            }
            
            await user_repository.update_user_some_field(condition, update_data, session)
            
            await session.commit()
            
            role_display = "Admin" if role == AdminStaffRole.ADMIN else "Staff"
            issuer = f"E-Commerce {role_display}"
            account_name = f"{user.first_name} {user.last_name} ({user.email})"
            
            otp_url = pyotp.totp.TOTP(secret).provisioning_uri(
                name=account_name, 
                issuer_name=issuer
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(otp_url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            qr_img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            role_display_vn = "quản trị viên" if role == AdminStaffRole.ADMIN else "nhân viên"
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": f"Thiết lập 2FA cho {role_display_vn} thành công! Vui lòng quét QR code bằng Google Authenticator",
                    "data": {
                        "qr_code_base64": qr_base64,
                        "account_name": account_name,
                        "role": role.value
                    }
                }
            )
        
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            AuthException.setup_2fa_failed()
        

    async def verify_login(self, user_data: VerifyLoginAdminModel, role: AdminStaffRole, session: AsyncSession):
        try:
            token_data = decode_url_safe_token(
                user_data.token, 
                role=role.value, 
                purpose="first_class_login"
            )
            
            user_id = token_data.get("id")
            if not user_id:
                AuthException.token_invalid()
                
            condition = and_(User.id == user_id, User.deleted_at.is_(None))
            user = await user_repository.get_user(condition, session)
            if not user:
                AuthException.invalid_account()
                
            if role == AdminStaffRole.ADMIN:
                if not user.is_admin:
                    AuthException.unauthorized_admin()
            elif role == AdminStaffRole.STAFF:
                if not user.is_staff:
                    AuthException.unauthorized_staff()
                if user.staff_status != "active":
                    AuthException.staff_account_disabled()
            
            if not user_data.otp:
                AuthException.otp_required()
                
            if not user.two_fa_secret:
                AuthException.two_fa_not_setup()
                
            totp = pyotp.TOTP(user.two_fa_secret)
            if not totp.verify(user_data.otp, valid_window=1):
                AuthException.invalid_otp()
                
            user_payload = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "id": str(user.id)
            }
            
            if role == AdminStaffRole.STAFF:
                user_payload["staff_status"] = user.staff_status
                
            access_token = create_access_token(
                user_data=user_payload,
                role=role.value
            )
            
            refresh_token = create_access_token(
                user_data=user_payload,
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                role=role.value
            )
            
            await user_repository.update_user_some_field(
                condition, 
                {'updated_at': datetime.now()}, 
                session
            )
            
            user_response = {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name
            }
            
            if role == AdminStaffRole.STAFF:
                user_response["staff_status"] = user.staff_status

            role_display = "quản trị viên" if role == AdminStaffRole.ADMIN else "nhân viên"

            return JSONResponse(
                status_code=200,
                content={
                    "message": f"Đăng nhập {role_display} thành công",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": user_response,
                        "role": role.value
                    }
                }
            )
        
        except HTTPException:
            raise
        except Exception as e:
            AuthException.login_verification_failed()


    async def login_customer_service(self, user_data: UserLoginModel, session: AsyncSession):
        email = user_data.email
        password = user_data.password
        
        if not email or not email.strip():
            AuthException.email_required()
            
        if not password or not password.strip():
            AuthException.password_required()
            
        try:
            condition = and_(User.email == email.strip().lower(), User.deleted_at.is_(None))
            user = await user_repository.get_user(condition, session)
            if not user:
                AuthException.invalid_account()
                
            password_valid = verify_password(password, user.password)
            if not password_valid:
                AuthException.invalid_account()
            
            if not user.is_verified:
                AuthException.user_not_verified()
                
            if not user.is_customer:
                AuthException.unauthorized_customer()
                
            if user.customer_status != "active":
                AuthException.customer_account_disabled()
                
            user_payload = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "id": str(user.id),
                "customer_status": user.customer_status
            }
            
            access_token = create_access_token(
                user_data=user_payload,
                role="customer"
            )

            refresh_token = create_access_token(
                user_data=user_payload,
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                role="customer"
            )
            
            await user_repository.update_user_some_field(
                condition, 
                {'updated_at': datetime.now()}, 
                session
            )
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Đăng nhập thành công",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": {
                            "id": str(user.id),
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "customer_status": user.customer_status
                        }
                    }
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            AuthException.login_failed()
            
