from datetime import datetime
import logging

from src.database.models import Payment

logger = logging.getLogger(__name__)


class PaymentDataService:
    def extract_vnpay_data(self, input_data: dict) -> dict:
        vnp_pay_date_raw = input_data.get("vnp_PayDate")
        vnp_pay_date = None
        if vnp_pay_date_raw:
            try:
                vnp_pay_date = datetime.strptime(vnp_pay_date_raw, "%Y%m%d%H%M%S")
            except ValueError:
                logger.warning(f"Invalid pay date format: {vnp_pay_date_raw}")

        return {
            "order_code": input_data.get("vnp_TxnRef"),
            "amount": int(input_data.get("vnp_Amount", 0)) // 100,
            "response_code": input_data.get("vnp_ResponseCode"),
            "transaction_no": input_data.get("vnp_TransactionNo"),
            "order_desc": input_data.get("vnp_OrderInfo"),
            "txn_ref": input_data.get("vnp_TxnRef"),
            "bank_tran_no": input_data.get("vnp_BankTranNo"),
            "bank_code": input_data.get("vnp_BankCode"),
            "card_type": input_data.get("vnp_CardType"),
            "transaction_status": input_data.get("vnp_TransactionStatus"),
            "tmn_code": input_data.get("vnp_TmnCode"),
            "pay_date": vnp_pay_date,
        }

    def build_payment_response(self, payment: Payment, order_code: str, cash_transaction=None,
                               already_processed: bool = False) -> dict:
        response = {
            "order_id": str(payment.order_id),
            "order_code": order_code,
            "amount": payment.amount,
            "order_info": payment.order_info,
            "transaction_no": payment.transaction_no,
            "response_code": payment.response_code,
            "status": payment.status,
            "already_processed": already_processed
        }

        if cash_transaction:
            response["cash_transaction"] = {
                "id": str(cash_transaction.id),
                "transaction_code": cash_transaction.transaction_code,
                "amount": cash_transaction.amount
            }

        return response
