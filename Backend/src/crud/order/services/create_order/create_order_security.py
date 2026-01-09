import logging
from fastapi import Request
from src.cache import cache_service
from src.errors.order import OrderException

logger = logging.getLogger(__name__)

MAX_SIGNUP_REQUESTS = 10  # Max 10 từ cùng IP
SIGNUP_WINDOW_MINUTES = 60  # Trong 1 giờ
SIGNUP_WINDOW_SECONDS = SIGNUP_WINDOW_MINUTES * 60


class CreateOrderSecurityService:
    async def check_create_order_rate_limit(self, ip_address: str):
        try:
            rate_key = f"rate_limit:order:create:user:{ip_address}"

            attempts = await cache_service.get(rate_key, default=0)

            if isinstance(attempts, str):
                attempts = int(attempts)

            if attempts >= MAX_SIGNUP_REQUESTS:
                ttl = await cache_service.ttl(rate_key)
                remaining_minutes = max(1, int(ttl / 60))

                logger.warning(
                    f"Signup rate limit exceeded for IP: {ip_address}, "
                    f"attempts: {attempts}"
                )

                OrderException.too_many_create_order(remaining_minutes)

            new_attempts = await cache_service.increment(rate_key)

            if new_attempts == 1:
                await cache_service.expire(rate_key, SIGNUP_WINDOW_SECONDS)

        except Exception as e:
            logger.error(f"Error checking signup rate limit: {str(e)}")


    @staticmethod
    def get_client_ip(request: Request):
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.client.host if request.client else "unknown"








