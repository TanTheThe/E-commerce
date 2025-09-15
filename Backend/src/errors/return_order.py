from fastapi import HTTPException, status


class ReturnOrderException:
    @staticmethod
    def already_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đơn hàng này đã có yêu cầu hoàn trả",
                "error_code": "return_001",
            },
        )
    
    @staticmethod
    def at_least_one_product_to_return():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Phải có ít nhất một sản phẩm để hoàn trả",
                "error_code": "return_002",
            },
        )
    
    @staticmethod
    def refund_amount_greater_than_0():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Số lượng hoàn trả phải lớn hơn 0",
                "error_code": "return_003",
            },
        )
    
    @staticmethod
    def refund_amount_exceed_purchase():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Số lượng hoàn trả không được vượt quá số lượng đã mua",
                "error_code": "return_004",
            },
        )
    
    @staticmethod
    def order_not_valid_for_return():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đơn hàng không hợp lệ để hoàn trả",
                "error_code": "return_005",
            },
        )