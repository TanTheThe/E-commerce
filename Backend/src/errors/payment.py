from fastapi import HTTPException, status


class PaymentException:
    @staticmethod
    def payment_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy thông tin thanh toán",
                "error_code": "payment_001",
            },
        )

    @staticmethod
    def payment_status_invalid():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Trạng thái thanh toán không hợp lệ",
                "error_code": "payment_002",
            },
        )

    @staticmethod
    def payment_refund_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy thông tin hoàn trả thanh toán",
                "error_code": "payment_003",
            },
        )

    @staticmethod
    def only_update_failed_or_manual_required():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Chỉ có thể sử dụng khi trạng thái hoàn trả thanh toán là thất bại hoặc thủ công",
                "error_code": "payment_004",
            },
        )

    @staticmethod
    def cant_retry_refund_with_status(status_refund):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không thể thử lại yêu cầu hoàn tiền với trạng thái: {status_refund}",
                "error_code": "payment_004",
            },
        )
