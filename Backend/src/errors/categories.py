from fastapi import HTTPException, status

class CategoriesException:
    @staticmethod
    def not_found_to_delete():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy danh mục để xóa",
                "error_code": "cate_001"
            }
        )

    @staticmethod
    def empty_list():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy bất cứ danh mục nào",
                "error_code": "cate_002"
            }
        )

    @staticmethod
    def not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy danh mục",
                "error_code": "cate_003"
            }
        )

    @staticmethod
    def categories_not_exist():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Một hoặc nhiều danh mục không tồn tại",
                "error_code": "cate_004"
            }
        )

    @staticmethod
    def invalid_parent():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Danh mục này không phải là danh mục cha",
                "error_code": "cate_005"
            }
        )

    @staticmethod
    def parent_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Danh mục cha đã chọn không tồn tại",
                "error_code": "cate_006"
            }
        )


