from fastapi import HTTPException, status

class SpecialOfferException:
    @staticmethod
    def not_found_to_delete():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy voucher để xóa",
                "error_code": "voucher_001"
            }
        )

    @staticmethod
    def not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy voucher",
                "error_code": "voucher_002"
            }
        )

    @staticmethod
    def empty_list():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy bất cứ voucher nào",
                "error_code": "voucher_003"
            }
        )

    @staticmethod
    def not_update_fields():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Voucher đã được sử dụng, chỉ được phép cập nhật 'name' và 'end_time'",
                "error_code": "voucher_004"
            }
        )

    @staticmethod
    def end_after_start_time():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Thời gian kết thúc phải sau thời gian bắt đầu",
                "error_code": "voucher_005"
            }
        )

    @staticmethod
    def total_greater_used():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tổng số lượng phải lớn hơn hoặc bằng số lượng đã sử dụng",
                "error_code": "voucher_006"
            }
        )

    @staticmethod
    def invalid_condition():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Điều kiện phải lớn hơn hoặc bằng 0",
                "error_code": "voucher_007"
            }
        )

    @staticmethod
    def invalid_scope_for_product():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ cho phép gán offer product",
                "error_code": "voucher_008"
            }
        )

    @staticmethod
    def expired_or_not_started():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Voucher đã hết hạn, không thể gắn cho sản phẩm",
                "error_code": "voucher_009"
            }
        )
