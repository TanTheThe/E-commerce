import logging
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.authentication.services.login_security.account_lockout import AccountLockoutService
from src.crud.authentication.services.login_security.login_attempt_logger import AttemptLoggerService
from src.crud.authentication.services.login_security.rate_limit import RateLimiterService

logger = logging.getLogger(__name__)

rate_limit_service = RateLimiterService()
account_lockout_service = AccountLockoutService()
attempt_logger_service = AttemptLoggerService()

class LoginSecurityService:
    async def check_rate_limit(self, email: str, request: Request, session: AsyncSession):
        try:
            await account_lockout_service.check_account_lockout(email)
            ip_address = rate_limit_service.get_client_ip(request)
            await rate_limit_service.check_ip_rate_limit(ip_address)
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            
            
    async def handle_failed_login(self, email: str, request: Request, session: AsyncSession):
        try:
            ip_address = rate_limit_service.get_client_ip(request)
            await account_lockout_service.increment_failed_attempts(email)
            await attempt_logger_service.log_failed_attempt(email, ip_address, session)
        except Exception as e:
            logger.error(f"Error handling failed login: {str(e)}")
            
            
    async def handle_successful_login(self, email: str, request: Request, session: AsyncSession):
        try:
            ip_address = rate_limit_service.get_client_ip(request)
            await account_lockout_service.clear_failed_attempts(email)
            await attempt_logger_service.log_successful_attempt(email, ip_address, session)
            
        except Exception as e:
            logger.error(f"Error handling successful login: {str(e)}")
            
    
    