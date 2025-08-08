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