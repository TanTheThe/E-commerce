from fastapi import HTTPException, status


class ImageException:
    @staticmethod
    def file_too_large(max_size_mb: int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"File quá lớn. Kích thước tối đa: {max_size_mb}MB",
                "error_code": "img_001",
            },
        )

    @staticmethod
    def invalid_file_type(allowed_types: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Định dạng file không hợp lệ. Chỉ chấp nhận: {allowed_types}",
                "error_code": "img_001",
            },
        )

    @staticmethod
    def file_already_exists(filename: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"File đã tồn tại: {filename}",
                "error_code": "img_001",
            },
        )

    @staticmethod
    def upload_failed(error: str):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Lỗi khi upload ảnh: {error}",
                "error_code": "img_001",
            },
        )

    @staticmethod
    def delete_failed(error: str):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Lỗi khi xóa ảnh: {error}",
                "error_code": "img_001",
            },
        )

    @staticmethod
    def file_not_found(file_path: str):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy file: {file_path}",
                "error_code": "img_001",
            },
        )
