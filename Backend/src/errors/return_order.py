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

    @staticmethod
    def at_least_5_products_image():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Phải cung cấp ít nhất 5 ảnh sản phẩm",
                "error_code": "return_006",
            },
        )

    @staticmethod
    def error_return_order():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Không thể tạo hoặc xử lí yêu cầu hoàn trả",
                "error_code": "return_007",
            },
        )

    @staticmethod
    def return_doesnt_exist():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Yêu cầu hoàn trả không tồn tại",
                "error_code": "return_008",
            },
        )

    @staticmethod
    def refund_has_been_processed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Yêu cầu hoàn trả đã được xử lý trước đó",
                "error_code": "return_009",
            },
        )

    @staticmethod
    def reason_must_be_provided():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Phải cung cấp lý do từ chối",
                "error_code": "return_010",
            },
        )

    @staticmethod
    def invalid_action():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Hành động không hợp lệ",
                "error_code": "return_011",
            },
        )

    @staticmethod
    def must_be_in_completed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Return order phải ở trạng thái completed mới có thể tạo manual refund transaction",
                "error_code": "return_011",
            },
        )

    @staticmethod
    def amount_greater_than_total_refund():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Số tiền hoàn lại không được lớn hơn tổng refund amount",
                "error_code": "return_011",
            },
        )