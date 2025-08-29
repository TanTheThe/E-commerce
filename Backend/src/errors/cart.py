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
                "error_code": "color_002",
            },
        )