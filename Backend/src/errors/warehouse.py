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

