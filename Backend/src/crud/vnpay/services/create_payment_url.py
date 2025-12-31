from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Dict, Any
from src.crud.cash.repositories import CashRepository
from src.crud.order.services.create_order.create_order import CreateOrderService
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.vnpay.utils import hmacsha512
from src.config import Config
from datetime import datetime
from src.crud.order.repositories import OrderRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.errors.order import OrderException
from src.database.models import Order
from src.schemas.order import PaymentStatusOrderType
import urllib.parse

order_repository = OrderRepository()
vnpay_repository = VNPayRepository()
special_offer_repository = SpecialOfferRepository()
create_order_service = CreateOrderService()
cash_repository = CashRepository()


class CreatePaymentURLService:
    def build_query_string(self, data: Dict[str, Any]) -> str:
        input_data = sorted(data.items())
        return "&".join(
            f"{key}={urllib.parse.quote_plus(str(val))}"
            for key, val in input_data
        )


    def get_payment_url(self, vnpay_payment_url: str, secret_key: str, request_data: Dict[str, Any]) -> str:
        query_string = self.build_query_string(request_data)
        hash_value = hmacsha512(secret_key, query_string)
        return f"{vnpay_payment_url}?{query_string}&vnp_SecureHash={hash_value}"


    async def create_payment_url(self, request, order_type: str, order_code: str, amount: int, order_desc: str,
                                 bank_code: str, language: str, ipaddr: str, session: AsyncSession) -> str:
        conditions = [Order.code == order_code, Order.deleted_at.is_(None)]
        order = await order_repository.get_order(session=session, where_conditions=conditions)

        if not order:
            OrderException.not_found()

        if order.payment_status == PaymentStatusOrderType.SUCCESS:
            OrderException.order_already_paid()

        request_data: Dict[str, Any] = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": Config.VNPAY_TMN_CODE,
            "vnp_Amount": amount * 100,
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": order_code,
            "vnp_OrderInfo": order_desc[:255],
            "vnp_OrderType": order_type,
            "vnp_Locale": language,
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
            "vnp_IpAddr": ipaddr,
            "vnp_ReturnUrl": Config.VNPAY_RETURN_URL,
        }

        if bank_code:
            request_data["vnp_BankCode"] = bank_code

        return self.get_payment_url(
            Config.VNPAY_PAYMENT_URL, Config.VNPAY_HASH_SECRET_KEY, request_data
        )

