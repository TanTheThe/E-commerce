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