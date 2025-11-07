from datetime import datetime, timedelta
from ipaddress import ip_address

from fastapi import Request
from sqlalchemy import func
from sqlmodel import select, and_, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import LoginAttempt
from src.errors.authentication import AuthException

MAX_FAILED_ATTEMPTS = 5  # Số lần thử tối đa
LOCKOUT_DURATION_MINUTES = 15  # Khóa trong 15 phút
ATTEMPT_WINDOW_MINUTES = 60  # Đếm attempts trong 60 phút

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
            failed_count = result.one_or_none()

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

        except Exception as e:
            raise


    async def log_failed_login_attempt(self, email: str, reason: str, request: Request, session: AsyncSession):
        try:
            ip_address_attempt = request.client.host if request.client else None

            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                ip_address_attempt = forwarded_for.split(",")[0].strip()

            login_attempt = LoginAttempt(
                email=email,
                ip_address=ip_address_attempt,
                is_successful=False,
                failure_reason=reason,
                attempted_at=datetime.now()
            )

            session.add(login_attempt)

            await session.commit()

        except Exception as e:
            await session.rollback()


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
                failure_reason=None,
                attempted_at=datetime.now()
            )

            session.add(login_attempt)

            await session.commit()

        except Exception as e:
            await session.rollback()
