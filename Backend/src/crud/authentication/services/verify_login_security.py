import logging
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
from sqlalchemy import func
from sqlmodel import select, and_, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.models import OTPVerificationAttempt

logger = logging.getLogger(__name__)

MAX_OTP_ATTEMPTS = 5
OTP_LOCKOUT_MINUTES = 15

class VerifyLoginSecurityService:
    async def check_otp_rate_limit(self, user_id: str, session: AsyncSession):
        try:
            window_start = datetime.now() - timedelta(minutes=OTP_LOCKOUT_MINUTES)

            stmt = select(func.count(OTPVerificationAttempt.id)).where(
                and_(
                    OTPVerificationAttempt.user_id == user_id,
                    OTPVerificationAttempt.attempted_at >= window_start,
                    OTPVerificationAttempt.is_successful == False
                )
            )

            result = await session.exec(stmt)
            failed_count = result.one_or_none() or 0

            if failed_count >= MAX_OTP_ATTEMPTS:
                last_attempt_stmt = select(OTPVerificationAttempt.attempted_at).where(
                    and_(
                        OTPVerificationAttempt.user_id == user_id,
                        OTPVerificationAttempt.is_successful == False
                    )
                ).order_by(desc(OTPVerificationAttempt.attempted_at)).limit(1)

                last_attempt_result = await session.exec(last_attempt_stmt)
                last_attempt_time = last_attempt_result.first()

                if last_attempt_time:
                    lock_until = last_attempt_time + timedelta(minutes=OTP_LOCKOUT_MINUTES)

                    if datetime.now() < lock_until:

                        remaining_minutes = int((lock_until - datetime.now()).total_seconds() / 60)

                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Bạn đã nhập sai OTP quá nhiều lần. Vui lòng thử lại sau {remaining_minutes} phút."
                        )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking login rate limit: {str(e)}")

    async def log_otp_attempt(self, user_id: str, success: bool, request: Request, session: AsyncSession):
        try:
            ip_address_attempt = request.client.host if request.client else None

            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                ip_address_attempt = forwarded_for.split(",")[0].strip()

            attempt = OTPVerificationAttempt(
                user_id=user_id,
                ip_address=ip_address_attempt,
                is_successful=success,
                attempted_at=datetime.now()
            )

            session.add(attempt)
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to log OTP attempt for user {user_id}: {str(e)}")