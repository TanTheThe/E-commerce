import logging
import secrets
from src.errors.authentication import AuthException
from datetime import datetime
from typing import Tuple, Optional
from src.cache import cache_service, CacheKeys
from src.crud.authentication.utils import generate_password_hash, verify_password

logger = logging.getLogger(__name__)

MAX_FORGOT_PASSWORD_REQUESTS = 3    # Max 3 requests trong window
FORGOT_PASSWORD_WINDOW_MINUTES = 15 # 15 phút
FORGOT_PASSWORD_WINDOW_SECONDS = FORGOT_PASSWORD_WINDOW_MINUTES * 60

MAX_OTP_ATTEMPTS = 5                # Max 5 lần nhập OTP
OTP_TTL_SECONDS = 300               # OTP hết hạn sau 5 phút
OTP_LENGTH = 6                      # OTP 6 chữ số


class ForgotPasswordSecurityService:
    async def check_forgot_password_rate_limit(self, email: str):
        try:
            rate_key = CacheKeys.forgot_password_rate_limit(email)
            
            attempts = await cache_service.get(rate_key, default=0)
            
            if isinstance(attempts, str):
                attempts = int(attempts)
                
            if attempts >= MAX_FORGOT_PASSWORD_REQUESTS:
                ttl = await cache_service.ttl(rate_key)
                remaining_minutes = max(1, int(ttl / 60))
                
                logger.warning(
                    f"Đã vượt qua số lần quên mật khẩu cho email: {email}, "
                    f"số lần: {attempts}"
                )
                
                AuthException.too_many_password_reset(remaining_minutes)
            
            new_attempts = await cache_service.increment(rate_key)
            
            if new_attempts == 1:
                await cache_service.expire(rate_key, FORGOT_PASSWORD_WINDOW_SECONDS)

        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra forgot password rate limit: {str(e)}")
            
    
    # Lưu vào cache thay vì DB
    async def generate_and_store_otp(self, user_id: str, email: str):
        try:
            otp = ''.join([str(secrets.randbelow(10)) for _ in range(OTP_LENGTH)])
            
            otp_hash = generate_password_hash(otp)
            
            otp_key = CacheKeys.otp(user_id)
            
            otp_data = {
                "otp_hash": otp_hash,
                "email": email,
                "created_at": datetime.now().isoformat(),
                "attempts": 0
            }
            
            await cache_service.set(
                otp_key,
                otp_data,
                ttl=OTP_TTL_SECONDS
            )
            
            return otp
        
        except Exception as e:
            logger.error(f"Lỗi khi tạo OTP: {str(e)}")
            raise
        
    
    async def verify_otp(self, user_id: str, otp: str) -> Tuple[bool, Optional[str]]:
        try:
            otp_key = CacheKeys.otp(user_id)
            
            otp_data = await cache_service.get(otp_key)
            
            if not otp_data:
                logger.warning(f"OTP không tìm thấy hoặc đã hết hạn với người dùng: {user_id}")
                return False, "OTP không tìm thấy hoặc đã hết hạn"
            
            attempts = otp_data.get("attempts", 0)
            
            if attempts >= MAX_OTP_ATTEMPTS:
                logger.warning(f"Số lượng OTP đã vượt max cho user: {user_id}")
                await cache_service.delete(otp_key)
                return False, f"Số lượng {MAX_OTP_ATTEMPTS} đã vượt max"
            
            otp_hash = otp_data.get("otp_hash")
            
            if not verify_password(otp, otp_hash):
                otp_data["attempts"] = attempts + 1
                
                ttl = await cache_service.ttl(otp_key)
                await cache_service.set(otp_key, otp_data, ttl=ttl if ttl > 0 else 60)
                
                attempts_left = MAX_OTP_ATTEMPTS - attempts - 1
                logger.warning(
                    f"OTP không phù hợp cho user: {user_id}, "
                    f"số lần còn lại: {attempts_left}"
                )
                
                return False, f"OTP không hợp lệ. {attempts_left} số lần còn lại"
            
            await cache_service.delete(otp_key)
            
            logger.info(f"OTP verify thành công cho user: {user_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Lỗi khi verify OTP: {str(e)}")
            return False, "OTP verify thất bại"

