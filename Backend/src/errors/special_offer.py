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
                "message": "Special offer này không áp dụng cho sản phẩm (scope phải là 'product')",
                "error_code": "voucher_008"
            }
        )

    @staticmethod
    def invalid_scope_for_order(special_offer):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Special offer này có scope = '{special_offer.scope}', "
                f"chỉ có thể gán offer với scope = 'order' cho users",
                "error_code": "voucher_008"
            }
        )

    @staticmethod
    def offer_not_started_yet():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Special offer chưa bắt đầu",
                "error_code": "voucher_009"
            }
        )

    @staticmethod
    def offer_has_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Special offer đã hết hạn",
                "error_code": "voucher_009"
            }
        )

    @staticmethod
    def exists_user_special_offer():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tồn tại khách hàng đã được gắn voucher này rồi",
                "error_code": "voucher_010"
            }
        )

    @staticmethod
    def invalid_scope_for_user():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ cho phép gán offer cho khách hàng",
                "error_code": "voucher_011"
            }
        )

    @staticmethod
    def insufficient_quantity():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Số lượng offer không đủ",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def offer_has_not_started(code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Mã giảm giá {code} chưa bắt đầu",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def offer_remaining_is_insufficient(code, remaining_quantity, quantity_needed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Mã giảm giá sản phẩm '{code}', "
                           f"chỉ còn {remaining_quantity} lượt, không đủ cho {quantity_needed} sản phẩm",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def min_must_less_than_max():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"discount_min phải nhỏ hơn hoặc bằng discount_max",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def no_valid_products():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy sản phẩm hợp lệ nào",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def some_products_already_active_offers(conflict_codes, conflicts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Một số sản phẩm đã có offer khác đang active: {conflict_codes}"
                + (" ..." if len(conflicts) > 5 else ""),
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def no_data_available():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không có dữ liệu để cập nhật",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def fields_not_allowed_to_be_updated(allowed_fields, not_allowed_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Voucher đã được sử dụng, chỉ được phép cập nhật: {', '.join(allowed_fields)}. "
                f"Không được cập nhật: {', '.join(not_allowed_fields)}",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def dont_change_start_time_to_past_time():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không được đổi start_time thành thời gian trong quá khứ",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def total_must_less_than_used_quantity(update_dict, special_offer):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng tối đa ({update_dict['total_quantity']}) không được nhỏ hơn "
                    f"số lượng đã sử dụng ({special_offer.used_quantity})",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def cant_change_scope_product_to_order():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể đổi scope từ 'product' sang 'order' vì đã có sản phẩm được gắn offer này. "
                    "Vui lòng gỡ offer khỏi tất cả sản phẩm trước.",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def cant_change_scope_order_to_product():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể đổi scope từ 'order' sang 'product' vì offer đã được sử dụng trong đơn hàng",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def no_valid_user_to_assign():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không có user hợp lệ nào để gán offer",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def all_users_already_assigned():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tất cả users đã được gán offer này rồi",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def insufficient_number_of_offers(required_quantity, available_quantity):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không đủ số lượng voucher. Cần: {required_quantity}, "
                f"còn lại: {available_quantity}",
                "error_code": "voucher_012"
            }
        )

    @staticmethod
    def cant_delete_offer(deletion_check):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa offer này. Lý do: {', '.join(deletion_check['blockers'])}",
                "error_code": "voucher_012"
            }
        )