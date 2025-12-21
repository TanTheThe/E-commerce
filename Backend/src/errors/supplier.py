from fastapi import HTTPException, status


class SupplierException:
    @staticmethod
    def supplier_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy thông tin về NCC trên",
                "error_code": "supp_001",
            },
        )

    @staticmethod
    def supplier_not_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Đã không còn hợp tác với NCC này nữa",
                "error_code": "supp_002",
            },
        )

    @staticmethod
    def name_supplier_already_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Tên của nhà cung cấp này đã tồn tại",
                "error_code": "supp_002",
            },
        )

    @staticmethod
    def credit_cant_negative():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Hạn mức công nợ không được âm",
                "error_code": "supp_002",
            },
        )

    @staticmethod
    def cant_delete_supplier_with_pending_orders():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa nhà cung cấp đang có đơn hàng chưa hoàn tất",
                "error_code": "supp_002",
            },
        )

    @staticmethod
    def cant_delete_supplier_outstanding_debt():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa nhà cung cấp đang có công nợ",
                "error_code": "supp_002",
            },
        )

    @staticmethod
    def error_while_delete_supplier():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi xóa nhà cung cấp",
                "error_code": "supp_002",
            },
        )

    @staticmethod
    def supplier_not_match_with_po():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Nhà cung cấp không khớp với đơn đặt hàng",
                "error_code": "supp_002",
            },
        )

    @staticmethod
    def cant_find_link():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy liên kết giữa supplier và các products",
                "error_code": "supp_002",
            },
        )
        
    @staticmethod
    def products_not_linked_to_supplier(product_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Các sản phẩm: {product_ids} không được liên kết với nhà cung cấp",
                "error_code": "supp_002",
            },
        )
        
    @staticmethod
    def only_admin_can_permanent_delete():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có admin mới có thể xóa vĩnh viễn",
                "error_code": "supp_002",
            },
        )
        
    @staticmethod
    def cannot_delete_supplier(reasons):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa nhà cung cấp do các lý do sau: {', '.join(reasons)}",
                "error_code": "supp_002",
            },
        )

