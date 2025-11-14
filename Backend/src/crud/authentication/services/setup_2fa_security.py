from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.models import LoginAttempt, Setup2FAAttempt
import logging

logger = logging.getLogger(__name__)

class Setup2FASecurityService:
    async def check_rate_limit_setup_2fa(self, user_id: str, session: AsyncSession):
        try:
            window_start = datetime.now() - timedelta(hours=1)

            stmt = select(func.count(Setup2FAAttempt.id)).where(
                and_(
                    Setup2FAAttempt.user_id == user_id,
                    LoginAttempt.attempted_at >= window_start,
                )
            )

            result = await session.exec(stmt)
            failed_count = result.one_or_none() or 0

            if failed_count >= 3:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Bạn đã thiết lập 2FA quá nhiều lần. Vui lòng thử lại sau 1 giờ."
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking setup 2FA rate limit: {str(e)}")


    async def log_setup_2fa_attempt(self, user_id: str, session: AsyncSession):
        try:
            attempt = Setup2FAAttempt(
                user_id=user_id,
                attempted_at=datetime.now(),
            )
            session.add(attempt)
            await session.flush()

        except Exception as e:
            logger.error(f"Failed to log setup 2FA attempt: {str(e)}")
