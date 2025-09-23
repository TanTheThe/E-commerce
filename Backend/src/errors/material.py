from fastapi import HTTPException, status


class MaterialException:
    @staticmethod
    def material_name_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đã tồn tại tên của chất liệu này",
                "error_code": "mate_001",
            },
        )

    @staticmethod
    def material_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy thông tin về chất liệu này",
                "error_code": "mate_002",
            },
        )

    @staticmethod
    def some_materials_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Có một vài chất liệu không tồn tại",
                "error_code": "mate_003",
            },
        )

    @staticmethod
    def percentage_exceeds_100():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tỉ lệ phân chia chất liệu vượt ngưỡng 100%",
                "error_code": "mate_004",
            },
        )
