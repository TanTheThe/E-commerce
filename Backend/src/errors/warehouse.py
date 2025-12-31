from fastapi import HTTPException, status


class WareHouseException:
    @staticmethod
    def warehouse_already_exist():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Tên kho này đã tồn tại trong hệ thống",
                "error_code": "warehouse_001",
            },
        )

    @staticmethod
    def warehouse_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy kho",
                "error_code": "warehouse_002",
            },
        )

    @staticmethod
    def cant_disable_default_warehouse():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể vô hiệu hóa kho mặc định. Vui lòng đặt kho khác làm mặc định trước",
                "error_code": "warehouse_003",
            },
        )

    @staticmethod
    def default_must_be_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể đặt kho không hoạt động làm mặc định",
                "error_code": "warehouse_004",
            },
        )

    @staticmethod
    def warehouse_already_default():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Kho này đã là kho mặc định",
                "error_code": "warehouse_005",
            },
        )

    @staticmethod
    def warehouse_already_inactive():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Kho này đã bị vô hiệu hóa trước đó",
                "error_code": "warehouse_006",
            },
        )

    @staticmethod
    def inactive_must_be_not_default():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể vô hiệu hóa kho mặc định. Vui lòng chọn kho mặc định khác trước",
                "error_code": "warehouse_007",
            },
        )

    @staticmethod
    def check_date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Ngày bắt đầu phải nhỏ hơn ngày kết thúc",
                "error_code": "warehouse_008",
            },
        )

    @staticmethod
    def cant_assign_to_inactive_warehouse():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể phân công nhân viên vào kho không hoạt động",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def default_must_is_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể gán mặc định cho kho không được kích hoạt",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def warehouse_not_match_with_po():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Kho nhận hàng không khớp với đơn đặt hàng",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def email_already_use_in_another_warehouse():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Email này đã được sử dụng cho kho khác",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def phone_already_use_in_another_warehouse():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số điện thoại này đã được sử dụng cho kho khác",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def manager_was_at_warehouse(existing_managed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Người quản lý này đã đang quản lý kho '{existing_managed.name}'",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def some_staff_invalid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Một số nhân viên không hợp lệ",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def no_fields_updated():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không có thông tin nào được cập nhật",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def cant_disable_warehouse_with_remaining_inventory():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể vô hiệu hóa kho còn hàng tồn kho. Vui lòng chuyển hết hàng trước khi deactivate",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def managing_different_warehouse(other_warehouse):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Người này đang quản lý kho '{other_warehouse.name}'",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def already_managed_this_warehouse():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Người này đã là quản lý kho này rồi",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def webhook_processed_previously():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Webhook đã được xử lý trước đó",
                "error_code": "warehouse_009",
            },
        )

    @staticmethod
    def order_processed_by_different_webhook():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Đơn hàng đang được xử lý bởi webhook khác",
                "error_code": "warehouse_009",
            },
        )

