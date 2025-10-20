from fastapi import HTTPException, status


class GoodsReceiptException:
    @staticmethod
    def received_quantity_does_not_match():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng thực tế cộng với số lượng từ chối không bằng số lượng thực nhận",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def reject_need_reason():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Phải cung cấp lý do khi có hàng bị từ chối",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def gr_parent_not_exist():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Phiếu nhập cha không tồn tại",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def gr_parent_not_has_issue():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể tạo GR con từ GR cha có trạng thái has_issue",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def gr_child_must_same_po_with_parent():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"GR con phải cùng PO với GR cha",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def gr_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Phiếu nhập kho không tồn tại",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def gr_detail_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy chi tiết nhập hàng",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def only_approved_when_pending():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể duyệt phiếu đang ở trạng thái pending",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def only_preview_pending():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể preview phiếu đang ở trạng thái pending",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def only_update_delete_when_draft():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể cập nhật/xóa phiếu ở trạng thái draft",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def cant_delete_receipt_have_child():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa phiếu nhập này vì có phiếu nhập con liên quan",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def cant_delete_receipt_have_returns():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa phiếu nhập này vì đã có phiếu trả hàng liên quan",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def error_while_delete_gr():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi xóa phiếu nhập kho",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def gr_parent_must_have_discrepancy():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Phiếu nhập kho cha phải đang có vấn đề",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def invalid_quantity_calculation():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Tổng số lượng chấp nhận và từ chối không bằng số lượng nhập",
                "error_code": "gr_001",
            },
        )

