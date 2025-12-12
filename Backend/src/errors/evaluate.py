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

    @staticmethod
    def already_reply():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đơn hàng này đã được phản hồi trước đó",
                "error_code": "eval_007"
            }
        )

    @staticmethod
    def order_not_delivered():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể đánh giá đơn hàng chưa được giao",
                "error_code": "eval_008"
            }
        )

    @staticmethod
    def product_may_deleted():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Sản phẩm không tồn tại hoặc đã bị xóa",
                "error_code": "eval_008"
            }
        )

    @staticmethod
    def evaluate_period_has_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đã quá thời hạn đánh giá (30 ngày kể từ khi giao hàng)",
                "error_code": "eval_008"
            }
        )

    @staticmethod
    def skip_cant_be_negative():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Skip không được là số âm",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def limit_must_be_1_to_100():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Limit phải từ 1 đến 100",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def supplement_time_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ được đánh giá bổ sung sau 7 ngày kể từ đánh giá đầu tiên",
                "error_code": "cate_006"
            }
        )