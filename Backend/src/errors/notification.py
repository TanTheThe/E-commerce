from fastapi import HTTPException, status


class NotificationException:
    @staticmethod
    def notification_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy thông báo",
                "error_code": "noti_001",
            },
        )

    @staticmethod
    def notification_not_require_process():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Thông báo này không yêu cầu xử lý",
                "error_code": "noti_001",
            },
        )

    @staticmethod
    def notification_previously_processed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Thông báo đã được xử lý trước đó",
                "error_code": "noti_001",
            },
        )

    @staticmethod
    def invalid_date_filter():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "from_date phải nhỏ hơn hoặc bằng to_date",
                "error_code": "noti_001",
            },
        )

    @staticmethod
    def notification_type_invalid(valid_types):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"notification_type không hợp lệ. Chọn từ: {', '.join(valid_types)}",
                "error_code": "noti_001",
            },
        )

    @staticmethod
    def sender_type_invalid(valid_types):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"sender_type không hợp lệ. Chọn từ: {', '.join(valid_types)}",
                "error_code": "noti_001",
            },
        )

    @staticmethod
    def order_cancellation_sent_recently():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Thông báo hủy đơn hàng đã được gửi gần đây",
                "error_code": "noti_001",
            },
        )

    @staticmethod
    def return_order_sent_recently():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Yêu cầu hoàn trả đã được gửi gần đây",
                "error_code": "noti_001",
            },
        )