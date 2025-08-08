from fastapi import HTTPException, status


class UserException:
    @staticmethod
    def email_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Email đã tồn tại",
                "error_code": "user_001",
            },
        )