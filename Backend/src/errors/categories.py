from typing import List
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
    def categories_not_exist(missing_ids: List):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Các danh mục này {missing_ids} không tồn tại",
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

    @staticmethod
    def slug_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Danh mục với tên này đã tồn tại",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def skip_cant_be_negative():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Skip không được là số âm",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def limit_must_be_1_to_100():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Limit phải từ 1 đến 100",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def type_size_not_exist():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Type size không tồn tại",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def no_fields_update():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không có trường nào được cập nhật",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def error_loop_category():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể tạo vòng lặp trong cây danh mục",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def category_tree_so_deep():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cây danh mục quá sâu (tối đa 10 cấp)",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def cant_set_child_to_parent():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể đặt danh mục con làm danh mục cha",
                "error_code": "cate_006"
            }
        )

    @staticmethod
    def list_exceed_max_length(max_length: int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Danh sách vượt quá độ dài tối đa cho phép là {max_length}",
                "error_code": "cate_007"
            }
        )
        
    @staticmethod
    def duplicate_ids_in_list():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Danh sách chứa các ID trùng lặp",
                "error_code": "cate_008"
            }
        )
