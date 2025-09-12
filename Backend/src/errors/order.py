from fastapi import HTTPException, status

class OrderException:
    @staticmethod
    def not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy đơn hàng",
                "error_code": "order_001",
            },
        )

    @staticmethod
    def unauthorized_order():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không có quyền truy cập đơn hàng này.",
                "error_code": "order_002"
            }
        )

    @staticmethod
    def fail_get_total_sales():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không thể tính tổng doanh số",
                "error_code": "order_003",
            },
        )

    @staticmethod
    def fail_get_total_revenue():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không thể tính tổng doanh thu",
                "error_code": "order_004",
            },
        )
    
    @staticmethod
    def order_already_paid():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Đơn hàng đã được thanh toán trước đó",
                "error_code": "order_005",
            },
        )
    
    @staticmethod
    def order_not_match():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Tổng tiền trong order không khớp với tiền sau khi thanh toán",
                "error_code": "order_006",
            },
        )

    @staticmethod
    def order_already_cancelled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Đơn hàng này đã được hủy trước đó",
                "error_code": "order_007",
            },
        )

    @staticmethod
    def order_cant_cancelled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không thể hủy đơn hàng",
                "error_code": "order_008",
            },
        )

    @staticmethod
    def error_cancelled():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Có lỗi xảy ra trong quá trình hủy đơn hàng",
                "error_code": "order_009",
            },
        )

    @staticmethod
    def not_request_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đơn hàng không có yêu cầu hủy",
                "error_code": "order_010",
            },
        )

    @staticmethod
    def not_accept_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể chấp nhận hủy đơn hàng",
                "error_code": "order_011",
            },
        )

    @staticmethod
    def reason_reject_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cần cung cấp lý do từ chối",
                "error_code": "order_012",
            },
        )

    @staticmethod
    def action_invalid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Action không hợp lệ",
                "error_code": "order_013",
            },
        )

    @staticmethod
    def already_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đơn hàng đã được gửi yêu cầu hủy trước đó",
                "error_code": "order_014",
            },
        )

    @staticmethod
    def cant_update_cancel_order():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không được thay đổi trạng thái đơn hàng đang có yêu cầu hủy",
                "error_code": "order_015",
            },
        )

    @staticmethod
    def cant_reverse_cancel_order():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không được phép thay đổi trạng thái đơn hàng đã hủy",
                "error_code": "order_016",
            },
        )