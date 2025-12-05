from fastapi import HTTPException, status


class BrandException:
    @staticmethod
    def brand_name_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đã tồn tại tên của brand này",
                "error_code": "brand_001",
            },
        )
        
    @staticmethod
    def brand_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy thông tin về brand này",
                "error_code": "brand_002",
            },
        )

    @staticmethod
    def some_brands_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Có một vài thương hiệu không tồn tại",
                "error_code": "brand_003",
            },
        )

    @staticmethod
    def invalid_brand_name():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tên của brand không hợp lệ",
                "error_code": "brand_001",
            },
        )

    @staticmethod
    def name_too_long():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tên của brand quá dài",
                "error_code": "brand_001",
            },
        )

    @staticmethod
    def invalid_logo_url():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Logo của brand không hợp lệ",
                "error_code": "brand_001",
            },
        )

    @staticmethod
    def cant_generate_unique_slug():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Xảy ra lỗi trong quá trình tạo ra slug mới",
                "error_code": "brand_001",
            },
        )

    @staticmethod
    def brand_update_failed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Xảy ra lỗi trong quá trình cập nhật brand",
                "error_code": "brand_001",
            },
        )