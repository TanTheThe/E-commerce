from fastapi import HTTPException, status


class SizeException:
    @staticmethod
    def size_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy size đã chọn",
                "error_code": "size_001",
            },
        )

    @staticmethod
    def size_not_exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Size đã chọn không tồn tại",
                "error_code": "size_002",
            },
        )