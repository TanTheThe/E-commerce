import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import LoginAttempt

logger = logging.getLogger(__name__)


class AttemptLoggerService:
    async def log_failed_attempt(self, email: str, ip_address: str, session: AsyncSession):
        try:
            login_attempt = LoginAttempt(
                email=email,
                ip_address=ip_address,
                is_successful=False,
                attempted_at=datetime.now()
            )
            session.add(login_attempt)
            await session.commit()
            
            logger.info(f"Logged failed attempt: {email} from {ip_address}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to log failed attempt to database: {str(e)}")
            
        
    async def log_successful_attempt(self, email: str, ip_address: str, session: AsyncSession):
        try:
            login_attempt = LoginAttempt(
                email=email,
                ip_address=ip_address,
                is_successful=True,
                attempted_at=datetime.now()
            )
            session.add(login_attempt)
            await session.commit()
            
            logger.info(f"Logged successful attempt: {email} from {ip_address}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to log successful attempt to database: {str(e)}")