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
                "message": "OTP không chính xác, ",
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
        
    @staticmethod
    def creation_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tạo tài khoản không thành công",
                "error_code": "auth_014",
            },
        )
        
    @staticmethod
    def verification_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Xác thực tài khoản không thành công",
                "error_code": "auth_015",
            },
        )
        
    @staticmethod
    def unauthorized_admin():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tài khoản chưa xác thực quyền admin",
                "error_code": "auth_016",
            },
        )
        
    @staticmethod
    def unauthorized_staff():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tài khoản chưa xác thực quyền staff",
                "error_code": "auth_017",
            },
        )
        
    @staticmethod
    def staff_account_disabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tài khoản staff chưa được kích hoạt",
                "error_code": "auth_018",
            },
        )
        
    @staticmethod
    def login_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đăng nhập thất bại",
                "error_code": "auth_019",
            },
        )
        
    @staticmethod
    def two_fa_already_setup():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tài khoản đã cài đặt xác thực 2 bước rồi",
                "error_code": "auth_020",
            },
        )
        
    @staticmethod
    def setup_2fa_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cài đặt xác thực 2 bước không thành công",
                "error_code": "auth_021",
            },
        )
        
    @staticmethod
    def two_fa_not_setup():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tài khoản chưa được cài đặt xác thực 2 bước",
                "error_code": "auth_022",
            },
        )
        
    @staticmethod
    def login_verification_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Xác thực đăng nhập thất bại",
                "error_code": "auth_023",
            },
        )
        
    @staticmethod
    def email_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Vui lòng cung cấp email khi đăng nhập",
                "error_code": "auth_024",
            },
        )
        
    @staticmethod
    def password_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Vui lòng cung cấp mật khẩu khi đăng nhập",
                "error_code": "auth_025",
            },
        )
        
    @staticmethod
    def unauthorized_customer():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tài khoản chưa xác thực quyền customer",
                "error_code": "auth_026",
            },
        )
        
    @staticmethod
    def customer_account_disabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tài khoản customer chưa được kích hoạt",
                "error_code": "auth_027",
            },
        )
        
    @staticmethod
    def invalid_reset_method():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Phương thức đặt lại mật khẩu không hợp lệ",
                "error_code": "auth_028",
            },
        )
        
    @staticmethod
    def forgot_password_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Lỗi trong quá trình đặt lại mật khẩu",
                "error_code": "auth_029",
            },
        )
        
    @staticmethod
    def email_send_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Gửi email không thành công",
                "error_code": "auth_030",
            },
        )
        
    @staticmethod
    def otp_send_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Gửi otp không thành công",
                "error_code": "auth_031",
            },
        )
        
    @staticmethod
    def same_password_error():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu mới giống y chang mật khẩu cũ",
                "error_code": "auth_032",
            },
        )
        
    @staticmethod
    def otp_and_email_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Email và OTP là bắt buộc",
                "error_code": "auth_033",
            },
        )
        
    @staticmethod
    def otp_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không tìm thấy OTP. Vui lòng yêu cầu gửi lại",
                "error_code": "auth_034",
            },
        )
        
    @staticmethod
    def otp_verification_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Xác thực bằng OTP thất bại",
                "error_code": "auth_035",
            },
        )
        
    @staticmethod
    def password_too_short():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu quá ngắn",
                "error_code": "auth_036",
            },
        )
        
    @staticmethod
    def password_too_long():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu quá dài",
                "error_code": "auth_037",
            },
        )
        
    @staticmethod
    def password_too_weak():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu quá yếu",
                "error_code": "auth_038",
            },
        )

    @staticmethod
    def password_missing_uppercase():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu thiếu chữ cái in hoa",
                "error_code": "auth_038",
            },
        )

    @staticmethod
    def password_missing_lowercase():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu thiếu chữ cái viết thường",
                "error_code": "auth_038",
            },
        )

    @staticmethod
    def password_missing_digit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu thiếu số",
                "error_code": "auth_038",
            },
        )

    @staticmethod
    def password_missing_special_char():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu thiếu ký tự đặc biệt",
                "error_code": "auth_038",
            },
        )

    @staticmethod
    def password_contains_common_pattern():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu nằm trong danh sách các mật khẩu quá đơn giản",
                "error_code": "auth_038",
            },
        )

    @staticmethod
    def password_too_repetitive():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu có quá nhiều ký tự lặp lại liên tục",
                "error_code": "auth_038",
            },
        )
        
    @staticmethod
    def account_deleted():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tài khoản đã bị xóa",
                "error_code": "auth_039",
            },
        )

    @staticmethod
    def password_change_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Thay đổi mật khẩu thất bại",
                "error_code": "auth_040",
            },
        )

    @staticmethod
    def invalid_user_id():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "ID người dùng không hợp lệ",
                "error_code": "auth_041",
            },
        )

    @staticmethod
    def old_password_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu hiện tại là bắt buộc",
                "error_code": "auth_042",
            },
        )

    @staticmethod
    def new_password_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu mới là bắt buộc",
                "error_code": "auth_043",
            },
        )

    @staticmethod
    def confirm_password_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Xác nhận mật khẩu mới là bắt buộc",
                "error_code": "auth_044",
            },
        )

    @staticmethod
    def password_needs_letters():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu phải chứa ít nhất 1 chữ cái",
                "error_code": "auth_044",
            },
        )

    @staticmethod
    def password_needs_numbers():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Mật khẩu phải chứa ít nhất 1 chữ số",
                "error_code": "auth_044",
            },
        )

    @staticmethod
    def email_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Email không tồn tại trong hệ thống",
                "error_code": "auth_045",
            },
        )

    @staticmethod
    def invalid_email_format():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Format của email không hợp lệ",
                "error_code": "auth_045",
            },
        )

    @staticmethod
    def time_lock_remaining(remaining_minutes):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Tài khoản tạm thời bị khóa do đăng nhập sai quá nhiều. Vui lòng thử lại sau {remaining_minutes} phút.",
                "error_code": "auth_045",
            },
        )

    @staticmethod
    def token_already_used():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Token này đã được sử dụng rồi",
                "error_code": "auth_045",
            },
        )

    @staticmethod
    def invalid_otp_or_email():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"OTP hoặc email không hợp lệ",
                "error_code": "auth_045",
            },
        )

    @staticmethod
    def otp_max_attempts_exceeded():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Số lần nhập OTP đã vượt quá số lượng cho phép",
                "error_code": "auth_045",
            },
        )

    @staticmethod
    def invalid_otp_attempts(attempts_left):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"OTP vừa nhập không đúng - số lần thử lại còn: {attempts_left}",
                "error_code": "auth_045",
            },
        )

    @staticmethod
    def email_already_registered():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Email này đã được tạo trước đó",
                "error_code": "auth_045",
            },
        )

    @staticmethod
    def cant_logout():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không thể đăng xuất. Vui lòng thử lại",
                "error_code": "auth_045",
            },
        )