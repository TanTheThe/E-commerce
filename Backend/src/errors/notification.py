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