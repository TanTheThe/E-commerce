from typing import List

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
    def materials_not_found(missing_material_ids: List):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy thông tin về các chất liệu: {missing_material_ids}",
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

    @staticmethod
    def materials_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sản phẩm phải có thông tin chất liệu"
        )

    @staticmethod
    def invalid_material_percentage(total: float):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tổng phần trăm chất liệu phải bằng 100 (hiện tại: {total})"
        )

    @staticmethod
    def material_id_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material ID là bắt buộc"
        )

    @staticmethod
    def duplicate_material(material_id: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chất liệu bị trùng lặp: {material_id}"
        )

    @staticmethod
    def invalid_percentage(material_id: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Phần trăm không hợp lệ cho chất liệu {material_id} (phải từ 0-100)"
        )
