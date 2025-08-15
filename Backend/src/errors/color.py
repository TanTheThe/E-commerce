from fastapi import HTTPException, status


class ColorException:
    @staticmethod
    def color_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy màu sắc đã chọn",
                "error_code": "color_001",
            },
        )

    @staticmethod
    def color_not_exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Màu đã chọn không tồn tại",
                "error_code": "color_002",
            },
        )

    @staticmethod
    def invalid_color_format():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Chỉ được chọn 1 trong 2 kiểu chọn màu",
                "error_code": "color_002",
            },
        )