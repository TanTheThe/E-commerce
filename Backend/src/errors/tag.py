from typing import List, Optional
from fastapi import HTTPException, status


class TagException:
    @staticmethod
    def tag_name_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đã tồn tại tên của tag này",
                "error_code": "tag_001",
            },
        )
        
    @staticmethod
    def tag_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy thông tin về tag này",
                "error_code": "tag_002",
            },
        )
        
    @staticmethod
    def tags_not_found(missing_tag_ids: List):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy thông tin về tag: {missing_tag_ids}",
                "error_code": "tag_002",
            },
        )

    @staticmethod
    def some_tags_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Có một vài tags không tồn tại",
                "error_code": "tag_003",
            },
        )
        
    @staticmethod
    def cant_create_unique_slug():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không thể tạo slug duy nhất",
                "error_code": "tag_003",
            },
        )
