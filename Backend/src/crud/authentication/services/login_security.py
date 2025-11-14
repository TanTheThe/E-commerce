from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from sqlalchemy import func
from sqlmodel import select, and_, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import LoginAttempt, Setup2FAAttempt
from src.errors.authentication import AuthException
import logging

MAX_FAILED_ATTEMPTS = 5  # Số lần thử tối đa
LOCKOUT_DURATION_MINUTES = 15  # Khóa trong 15 phút
ATTEMPT_WINDOW_MINUTES = 60  # Đếm attempts trong 60 phút

logger = logging.getLogger(__name__)

class LoginSecurityService:
    async def check_rate_limit(self, email: str, session: AsyncSession):
        try:
            window_start = datetime.now() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)

            stmt = select(func.count(LoginAttempt.id)).where(
                and_(
                    LoginAttempt.email == email,
                    LoginAttempt.attempted_at >= window_start,
                    LoginAttempt.is_successful == False
                )
            )

            result = await session.exec(stmt)
            failed_count = result.one_or_none() or 0

            if failed_count >= MAX_FAILED_ATTEMPTS:
                last_attempt_stmt = select(LoginAttempt.attempted_at).where(
                    and_(
                        LoginAttempt.email == email,
                        LoginAttempt.is_successful == False
                    )
                ).order_by(desc(LoginAttempt.attempted_at)).limit(1)

                last_attempt_result = await session.exec(last_attempt_stmt)
                last_attempt_time = last_attempt_result.first()

                if last_attempt_time:
                    lock_until = last_attempt_time + timedelta(minutes=LOCKOUT_DURATION_MINUTES)

                    if datetime.now() < lock_until:
                        remaining_minutes = int((lock_until - datetime.now()).total_seconds() / 60)

                        AuthException.time_lock_remaining(remaining_minutes)


        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking login rate limit: {str(e)}")


    async def log_failed_login_attempt(self, email: str, request: Request, session: AsyncSession):
        try:
            ip_address_attempt = request.client.host if request.client else None

            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                ip_address_attempt = forwarded_for.split(",")[0].strip()

            login_attempt = LoginAttempt(
                email=email,
                ip_address=ip_address_attempt,
                is_successful=False,
                attempted_at=datetime.now()
            )

            session.add(login_attempt)

            await session.commit()

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to log failed login attempt: {str(e)}")


    async def log_successful_login(self, email: str, request: Request, session: AsyncSession):
        try:
            ip_address_attempt = request.client.host if request.client else None

            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                ip_address_attempt = forwarded_for.split(",")[0].strip()

            login_attempt = LoginAttempt(
                email=email,
                ip_address=ip_address_attempt,
                is_successful=True,
                attempted_at=datetime.now()
            )

            session.add(login_attempt)

            await session.commit()

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to log success login attempt: {str(e)}")
