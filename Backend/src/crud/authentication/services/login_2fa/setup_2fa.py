from datetime import datetime
from qrcode.main import QRCode
from io import BytesIO
from PIL import Image
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Request
from src.cache.cache_service import CacheService
from src.crud.authentication.services.login_2fa.setup_2fa_security import Setup2FASecurityService
from src.crud.authentication.services.logout.token_blacklist_service import TokenBlacklistService
from src.crud.authentication.utils import decode_url_safe_token
from src.crud.user.repositories import UserRepository
from src.database.models import User
from src.errors.authentication import AuthException
from src.schemas.user import AdminStaffRole, Setup2FA
import pyotp
import logging
import base64

user_repository = UserRepository()
token_blacklist_service = TokenBlacklistService()
setup_2fa_security_service = Setup2FASecurityService()
cache_service = CacheService()

logger = logging.getLogger(__name__)

class Setup2FAService:
    async def setup_2fa(self, user_data: Setup2FA, role: AdminStaffRole, request: Request, session: AsyncSession):
        token = user_data.token

        is_blacklisted = await token_blacklist_service.token_in_blocklist(
            token=token,
            role=role.value,
            purpose="first_class_login"
        )

        if is_blacklisted:
            AuthException.token_already_used()

        token_data = decode_url_safe_token(
            token=token,
            role=str(role.value),
            purpose="first_class_login"
        )

        user_id = token_data.get('id')
        if not user_id:
            AuthException.token_invalid()

        await setup_2fa_security_service.check_rate_limit_setup_2fa(user_id, session)

        await setup_2fa_security_service.log_setup_2fa_attempt(user_id, session)

        condition = [User.id == user_id, User.deleted_at.is_(None)]
        user = await user_repository.get_user(session=session, where_conditions=condition)
        if not user:
            AuthException.invalid_account()

        token_email = token_data.get('email')
        if not token_email or token_email != user.email:
            AuthException.token_invalid()

        if not user.is_verified:
            AuthException.user_not_verified()

        if role == AdminStaffRole.ADMIN and not user.is_admin:
            AuthException.unauthorized_admin()
        elif role == AdminStaffRole.STAFF:
            if not user.is_staff:
                AuthException.unauthorized_staff()
            if user.staff_status != "active":
                AuthException.staff_account_disabled()

        if user.two_fa_secret and user.two_fa_enabled:
            AuthException.two_fa_already_setup()

        secret = pyotp.random_base32()

        try:
            update_data = {
                'two_fa_secret': secret,
                'two_fa_enabled': True,
                'updated_at': datetime.now()
            }

            await user_repository.update_user(where_conditions=condition, update_data=update_data, session=session)

            await session.commit()

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to setup 2FA for user {user_id}: {str(e)}")
            raise

        role_display = "Admin" if role == AdminStaffRole.ADMIN else "Staff"
        issuer = f"E-Commerce {role_display}"
        account_name = f"{user.first_name} {user.last_name} ({user.email})"
        
        qr_cache_key = f"2fa:qr_code:{user_id}"
        await cache_service.delete(qr_cache_key)

        await user_repository.update_user(where_conditions=condition, update_data=update_data, session=session)
        await session.commit()

        otp_url = pyotp.totp.TOTP(secret).provisioning_uri(
            name=account_name,
            issuer_name=issuer
        )

        try:
            qr = QRCode(version=1, box_size=10, border=5)
            qr.add_data(otp_url)
            qr.make(fit=True)

            qr_img: Image.Image = qr.make_image(fill_color="black", back_color="white")

            buffered = BytesIO()
            qr_img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            await cache_service.set(qr_cache_key, qr_base64, ttl=600)
            
        except Exception as e:
            logger.error(f"Failed to generate QR code: {str(e)}")
            qr_base64 = None
        
        await setup_2fa_security_service.reset_setup_attempts(user_id)
            
        role_display_vn = "quản trị viên" if role == AdminStaffRole.ADMIN else "nhân viên"

        return {
            "message": f"Thiết lập 2FA cho {role_display_vn} thành công! Vui lòng quét QR code bằng Google Authenticator",
            "data": {
                "qr_code_base64": qr_base64,
                "account_name": account_name,
                "role": role.value
            }
        }