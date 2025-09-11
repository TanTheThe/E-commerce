from src.crud.vnpay.utils import hmacsha512
from src.config import Config
from datetime import datetime
import httpx

class PaymentRefundService:
    async def refund_transaction(self, TransactionType: str, order_id: str, amount: str, order_desc: str, trans_date: str, ipaddr: str):
        vnp_TmnCode = Config.VNPAY_TMN_CODE
        vnp_RequestId = "req_" + datetime.now().strftime("%Y%m%d%H%M%S")
        vnp_Version = "2.1.0"
        vnp_Command = "refund"
        vnp_TransactionNo = "0"
        vnp_CreateDate = datetime.now().strftime("%Y%m%d%H%M%S")
        vnp_CreateBy = "user01"

        hash_data = "|".join([
            vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, TransactionType, order_id,
            amount, vnp_TransactionNo, trans_date, vnp_CreateBy, vnp_CreateDate, ipaddr, order_desc
        ])
        secure_hash = hmacsha512(Config.VNPAY_HASH_SECRET_KEY, hash_data)

        data = {
            "vnp_RequestId": vnp_RequestId,
            "vnp_TmnCode": vnp_TmnCode,
            "vnp_Command": vnp_Command,
            "vnp_TxnRef": order_id,
            "vnp_Amount": amount,
            "vnp_OrderInfo": order_desc,
            "vnp_TransactionDate": trans_date,
            "vnp_CreateDate": vnp_CreateDate,
            "vnp_IpAddr": ipaddr,
            "vnp_TransactionType": TransactionType,
            "vnp_TransactionNo": vnp_TransactionNo,
            "vnp_CreateBy": vnp_CreateBy,
            "vnp_Version": vnp_Version,
            "vnp_SecureHash": secure_hash,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(Config.VNPAY_API_URL, json=data)
        return response.json() if response.status_code == 200 else {"error": f"Request failed {response.status_code}"}
