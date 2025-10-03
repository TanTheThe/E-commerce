from fastapi import HTTPException, status


class StockException:
    @staticmethod
    def min_must_less_than_max():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng tối thiểu phải nhỏ hơn hoặc bằng số lượng tối đa",
                "error_code": "stock_001",
            },
        )

    @staticmethod
    def min_must_greater_than_0():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng tối thiểu phải nhỏ lơn hơn bằng 0",
                "error_code": "stock_002",
            },
        )

