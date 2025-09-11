from fastapi import HTTPException, status


class PaymentException:
    @staticmethod
    def payment_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy thanh toán",
                "error_code": "payment_001",
            },
        )
