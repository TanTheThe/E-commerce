from fastapi import HTTPException, status


class CartException:
    @staticmethod
    def cart_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy giỏ hàng",
                "error_code": "cart_001",
            },
        )

    @staticmethod
    def cart_items_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy bất cứ sản phẩm nào trong giỏ hàng",
                "error_code": "cart_002",
            },
        )

    @staticmethod
    def invalid_color_format():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Chỉ được chọn 1 trong 2 kiểu chọn màu",
                "error_code": "cart_003",
            },
        )

    @staticmethod
    def fail_create_cart():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Có lỗi xảy ra trong quá trình thêm vào giỏ hàng",
                "error_code": "cart_004",
            },
        )
        
    @staticmethod
    def database_constraint_violation():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Vi phạm ràng buộc tạo một lúc 2 giỏ hàng",
                "error_code": "cart_001",
            },
        )
        
    @staticmethod
    def cart_items_limit_exceeded(MAX_CART_ITEMS):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Số lượng sản phẩm trong giỏ hàng đã vượt mức {MAX_CART_ITEMS}",
                "error_code": "cart_001",
            },
        )
        
    @staticmethod
    def cart_value_exceeded(MAX_CART_ITEMS):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Số lượng sản phẩm trong giỏ hàng đã vượt mức {MAX_CART_ITEMS}",
                "error_code": "cart_001",
            },
        )
        
    @staticmethod
    def deletion_failed():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Thất bại khi xóa sản phẩm khỏi giỏ hàng",
                "error_code": "cart_001",
            },
        )