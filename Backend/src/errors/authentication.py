from fastapi import HTTPException, status


class AuthException:
    @staticmethod
    def invalid_account():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Sai thông tin tài khoản hoặc mật khẩu",
                "error_code": "auth_001",
            },
        )

    @staticmethod
    def user_not_verified():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tài khoản người dùng chưa được xác thực",
                "error_code": "auth_002",
            },
        )

    @staticmethod
    def unauthorized():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không có quyền",
                "error_code": "auth_003",
            },
        )

    @staticmethod
    def user_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy người dùng",
                "error_code": "auth_004",
            },
        )

    @staticmethod
    def otp_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cần nhập OTP để đăng nhập",
                "error_code": "auth_005",
            },
        )

    @staticmethod
    def invalid_otp():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "OTP không chính xác",
                "error_code": "auth_006",
            },
        )

    @staticmethod
    def invalid_check_option():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Lựa chọn phương thức email hoặc otp",
                "error_code": "auth_007",
            },
        )

    @staticmethod
    def password_mismatch():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu không khớp",
                "error_code": "auth_008",
            },
        )

    @staticmethod
    def token_missing():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Thiếu token xác thực",
                "error_code": "auth_009",
            },
        )

    @staticmethod
    def token_invalid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Token không hợp lệ hoặc đã hết hạn",
                "error_code": "auth_010",
            },
        )

    @staticmethod
    def otp_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "OTP đã hết hạn",
                "error_code": "auth_011",
            },
        )

    @staticmethod
    def authentication_error():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Có lỗi xảy ra trong quá trình xác thực",
                "error_code": "auth_012",
            },
        )

    @staticmethod
    def invalid_password():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu cũ không đúng",
                "error_code": "auth_013",
            },
        )