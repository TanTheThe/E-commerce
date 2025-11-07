from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import and_
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from src.crud.cash.repositories import CashRepository
from src.crud.order.services.create_order import CreateOrderService
from src.crud.special_offer.repositories import SpecialOfferRepository
from src.crud.vnpay.utils import hmacsha512
from src.config import Config
from datetime import datetime, timedelta
from src.crud.order.repositories import OrderRepository
from src.crud.vnpay.repositories import VNPayRepository
from src.errors.order import OrderException
from src.database.models import Order, Payment, Special_Offer
from src.schemas.order import PaymentStatusOrderType
import urllib.parse
import uuid

order_repository = OrderRepository()
vnpay_repository = VNPayRepository()
special_offer_repository = SpecialOfferRepository()
create_order_service = CreateOrderService()
cash_repository = CashRepository()

class VNPayService:
    def __init__(self):
        self.payment_results_cache = {}


    def build_query_string(self, data: Dict[str, Any]) -> str:
        input_data = sorted(data.items())
        return "&".join(
            [f"{key}={urllib.parse.quote_plus(str(val))}" for key, val in input_data]
        )


    def get_payment_url(self, vnpay_payment_url: str, secret_key: str, request_data: Dict[str, Any]) -> str:
        query_string = self.build_query_string(request_data)
        hash_value = hmacsha512(secret_key, query_string)
        return f"{vnpay_payment_url}?{query_string}&vnp_SecureHash={hash_value}"


    def validate_response(self, secret_key: str, response_data: Dict[str, Any]) -> bool:
        vnp_secure_hash = response_data.get("vnp_SecureHash")
        if not vnp_secure_hash:
            return False

        data_copy = dict(response_data)
        data_copy.pop("vnp_SecureHash", None)
        data_copy.pop("vnp_SecureHashType", None)

        hash_data = self.build_query_string(
            {k: v for k, v in data_copy.items() if str(k).startswith("vnp_")}
        )
        hash_value = hmacsha512(secret_key, hash_data)

        print(
            f"Validate debug:\nHashData: {hash_data}\nHashValue: {hash_value}\nInputHash: {vnp_secure_hash}"
        )

        return vnp_secure_hash == hash_value


    def validate_transaction_time(self, vnp_pay_date: str, max_hours: int = 24) -> bool:
        try:
            pay_date = datetime.strptime(vnp_pay_date, "%Y%m%d%H%M%S")
            current_time = datetime.now()
            time_diff = current_time - pay_date
            return time_diff <= timedelta(hours=max_hours)
        except (ValueError, TypeError):
            return False


    async def create_payment_url(
        self,
        request,
        order_type: str,
        order_code: str,
        amount: int,
        order_desc: str,
        bank_code: str,
        language: str,
        ipaddr: str,
        session: AsyncSession
    ) -> str:
        condition = and_(Order.code == order_code, Order.deleted_at.is_(None))
        order = await order_repository.get_order(condition, session)

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
            "vnp_OrderInfo": order_desc,
            "vnp_OrderType": order_type,
            "vnp_Locale": language or "vn",
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
            "vnp_IpAddr": ipaddr,
            "vnp_ReturnUrl": Config.VNPAY_RETURN_URL,
        }
        if bank_code:
            request_data["vnp_BankCode"] = bank_code

        return self.get_payment_url(
            Config.VNPAY_PAYMENT_URL, Config.VNPAY_HASH_SECRET_KEY, request_data
        )

    async def process_payment_completion(self, input_data: dict, session: AsyncSession):
        order_code = input_data.get("vnp_TxnRef")
        amount = int(input_data.get("vnp_Amount", 0)) // 100
        vnp_response_code = input_data.get("vnp_ResponseCode")
        vnp_transaction_no = input_data.get("vnp_TransactionNo")
        order_desc = input_data.get("vnp_OrderInfo")

        vnp_txn_ref = input_data.get("vnp_TxnRef")
        vnp_bank_tran_no = input_data.get("vnp_BankTranNo")
        vnp_bank_code = input_data.get("vnp_BankCode")
        vnp_card_type = input_data.get("vnp_CardType")
        vnp_transaction_status = input_data.get("vnp_TransactionStatus")
        vnp_pay_date_raw = input_data.get("vnp_PayDate")
        vnp_tmn_code = input_data.get("vnp_TmnCode")

        vnp_pay_date = None
        if vnp_pay_date_raw:
            vnp_pay_date = datetime.strptime(vnp_pay_date_raw, "%Y%m%d%H%M%S")

        condition_order = and_(Order.code == order_code, Order.deleted_at.is_(None))
        joins = [selectinload(Order.order_detail), selectinload(Order.user)]
        order = await order_repository.get_order(condition_order, session, joins)

        if not order:
            raise OrderException.not_found()

        if order.total_price != amount:
            raise OrderException.order_not_match()

        condition_payment = and_(Payment.order_id == order.id)
        existing_payment = await vnpay_repository.get_payment(condition_payment, session)
        if existing_payment:
            return {
                "order_id": str(existing_payment.order_id),
                "order_code": order_code,
                "amount": existing_payment.amount,
                "order_info": existing_payment.order_info,
                "transaction_no": existing_payment.transaction_no,
                "response_code": existing_payment.response_code,
                "status": existing_payment.status,
                "already_processed": True
            }

        is_success = vnp_response_code == "00"
        payment_status = PaymentStatusOrderType.SUCCESS if is_success else PaymentStatusOrderType.FAILED

        order.payment_status = payment_status
        session.add(order)

        if is_success:
            variant_ids = {od.product_variant_id for od in order.order_detail}
            variant_map = await create_order_service.get_variants_with_product_offers(variant_ids, session)

            order_offer = None
            if order.special_offer_id:
                conditions_offer = [
                    Special_Offer.id == order.special_offer_id,
                    Special_Offer.deleted_at.is_(None)
                ]
                order_offer = await special_offer_repository.get_special_offer(session=session, where_conditions=conditions_offer)

            _, _, _, product_offers_to_update = await create_order_service.calculate_order_totals(
                order.order_detail, variant_map, session
            )

            await create_order_service.update_offers_usage(
                product_offers_to_update, order_offer, order.user_id, session
            )

            await create_order_service.update_inventory_batch(order.order_detail, variant_map, session)

            await create_order_service.update_product_stats(order.order_detail, variant_map, session)

        payment_dict = {
            "order_id": order.id,
            "payment_gateway": "vnpay",
            "txn_ref": vnp_txn_ref,
            "transaction_no": vnp_transaction_no,
            "bank_tran_no": vnp_bank_tran_no,
            "bank_code": vnp_bank_code,
            "card_type": vnp_card_type,
            "transaction_status": vnp_transaction_status,
            "tmn_code": vnp_tmn_code,
            "pay_date": vnp_pay_date,
            "amount": amount,
            "response_code": vnp_response_code,
            "order_info": order_desc,
            "status": payment_status
        }

        payment = await vnpay_repository.create_payment(payment_dict, session)

        cash_transaction = None
        if is_success:
            cash_transaction = await self.create_vnpay_revenue_transaction(
                order, payment, vnp_pay_date, session
            )

        await session.commit()

        response = {
            "order_id": str(payment.order_id),
            "order_code": order_code,
            "amount": payment.amount,
            "order_info": payment.order_info,
            "transaction_no": payment.transaction_no,
            "response_code": payment.response_code,
            "status": payment.status,
            "already_processed": False
        }

        if cash_transaction:
            response["cash_transaction"] = {
                "id": str(cash_transaction.id),
                "transaction_code": cash_transaction.transaction_code,
                "amount": cash_transaction.amount
            }

        return response


    async def create_vnpay_revenue_transaction(self, order, payment, transaction_date: datetime, session: AsyncSession):
        user = order.user
        reference_name = f"{user.first_name} {user.last_name}" if user else None

        transaction_code = f"CT{int(datetime.now().timestamp() * 1000)}"

        transaction_data = {
            'transaction_code': transaction_code,
            'transaction_type': 'inflow',
            'category': 'revenue',
            'amount': order.total_price,
            'transaction_date': transaction_date or datetime.now(),
            'reference_type': 'customer',
            'reference_id': order.user_id,
            'reference_name': reference_name,
            'payment_method': 'e_wallet',
            'notes': f"Doanh thu VNPay từ đơn hàng {order.code} - Giao dịch {payment.transaction_no}",
            'performed_by': None
        }

        cash_transaction = await cash_repository.create_cash_transaction(transaction_data, session)

        return cash_transaction



    async def handle_ipn(self, input_data: dict, session: AsyncSession):
        if not input_data:
            return JSONResponse({"RspCode": "99", "Message": "Invalid request"})

        if not self.validate_response(Config.VNPAY_HASH_SECRET_KEY, input_data):
            return JSONResponse({"RspCode": "97", "Message": "Invalid Signature"})
        
        if not self.validate_transaction_time(input_data.get("vnp_PayDate", "")):
            return JSONResponse({"RspCode": "99", "Message": "Invalid transaction time"})
        
        try:
            result = await self.process_payment_completion(input_data, session)

            vnp_response_code = input_data.get("vnp_ResponseCode")

            if vnp_response_code == "00":
                return JSONResponse({"RspCode": "00", "Message": "Confirm Success"})
            else:
                return JSONResponse({"RspCode": "00", "Message": "Payment Error"})

        except Exception as e:
            await session.rollback()
            return JSONResponse({"RspCode": "99", "Message": "Internal error"})
    

    async def handle_return(self, input_data: dict, request, session: AsyncSession):
        order_code = input_data.get("vnp_TxnRef")

        if not input_data:
            raise ValueError("Invalid request data")

        if not order_code:
            raise ValueError("Missing order code")
        
        if not self.validate_response(Config.VNPAY_HASH_SECRET_KEY, input_data):
            raise ValueError("Invalid signature")
        
        try:
            result = await self.process_payment_completion(input_data, session)

            session_id = str(uuid.uuid4())
            self.payment_results_cache[session_id] = {
                "result": result,
                "timestamp": datetime.now(),
                "expires_at": datetime.now() + timedelta(minutes=10)  # Expires in 10 minutes
            }

            self._cleanup_expired_results()

            final_result = {"session_id": session_id, **result}
            return final_result
            
        except Exception as e:
            await session.rollback()
            raise


    async def get_payment_result_by_session(self, session_id: str, session: AsyncSession) -> Optional[Dict[str, Any]]:
        if session_id not in self.payment_results_cache:
            return None

        cached_data = self.payment_results_cache[session_id]

        if datetime.now() > cached_data["expires_at"]:
            del self.payment_results_cache[session_id]
            return None

        return cached_data["result"]


    def _cleanup_expired_results(self):
        now = datetime.now()
        expired_keys = [
            key for key, value in self.payment_results_cache.items()
            if now > value["expires_at"]
        ]
        for key in expired_keys:
            del self.payment_results_cache[key]

