from fastapi import HTTPException, status


class EvaluateException:
    @staticmethod
    def review_not_found_to_delete():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy đánh giá để xóa",
                "error_code": "eval_001",
            },
        )

    @staticmethod
    def order_detail_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy chi tiết đơn hàng",
                "error_code": "eval_002",
            }
        )

    @staticmethod
    def user_not_allowed_to_review():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không được phép đánh giá đơn hàng này",
                "error_code": "eval_003",
            },
        )

    @staticmethod
    def review_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy đánh giá",
                "error_code": "eval_004"
            }
        )

    @staticmethod
    def already_reviewed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đơn hàng này đã được đánh giá trước đó",
                "error_code": "eval_005"
            }
        )

    @staticmethod
    def already_supplemented():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đơn hàng này đã được đánh giá bổ sung trước đó",
                "error_code": "eval_006"
            }
        )