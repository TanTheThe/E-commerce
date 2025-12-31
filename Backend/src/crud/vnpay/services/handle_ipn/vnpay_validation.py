from typing import Dict, Any
from src.crud.vnpay.utils import hmacsha512
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)


class VNPayValidationService:
    def validate_signature(self, secret_key: str, response_data: Dict[str, Any]) -> bool:
        vnp_secure_hash = response_data.get("vnp_SecureHash")
        if not vnp_secure_hash:
            return False

        data_copy = {k: v for k, v in response_data.items()
                     if k not in ("vnp_SecureHash", "vnp_SecureHashType") and k.startswith("vnp_")}

        hash_data = self.build_query_string(data_copy)
        hash_value = hmacsha512(secret_key, hash_data)

        logger.debug(f"Signature validation - Expected: {hash_value}, Received: {vnp_secure_hash}")

        return vnp_secure_hash == hash_value

    def validate_transaction_time(self, vnp_pay_date: str, max_hours: int = 24) -> bool:
        try:
            pay_date = datetime.strptime(vnp_pay_date, "%Y%m%d%H%M%S")
            time_diff = datetime.now() - pay_date
            return time_diff <= timedelta(hours=max_hours)
        except (ValueError, TypeError):
            return False

    def validate_amount(self, order_amount: int, vnpay_amount: int) -> bool:
        return order_amount == vnpay_amount // 100

    def build_query_string(self, data: Dict[str, Any]) -> str:
        sorted_data = sorted(data.items())
        return "&".join(f"{k}={v}" for k, v in sorted_data)
