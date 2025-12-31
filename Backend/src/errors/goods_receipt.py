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

    @staticmethod
    def circular_gr_error():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Phát hiện lỗi khi gán GR cha cho GR này",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def return_quantity_greater_than_remaining_qty():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng hoàn vượt quá số lỗi cho phép",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def total_returned_greater_than_accepted_quantity():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Tổng số lượng trả vượt quá số lượng accepted",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def total_returned_greater_than_rejected_quantity():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Tổng số lượng trả vượt quá số lượng rejected",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def po_detail_not_exist_in_parent_receipt():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"PO Detail không tồn tại trong parent receipt",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def ordered_quantity_greater_than_available(expected_qty):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"ordered_quantity lớn hơn số lượng {expected_qty}",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def accept_greater_than_ordered():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"accepted_quantity không được vượt quá ordered_quantity",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def duplicate_po_detail_in_items():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có po_detail_id bị trùng lặp trong danh sách items",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def rejection_reason_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Lý do từ chối là bắt buộc khi có số lượng từ chối lớn hơn 0",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def received_greater_than_ordered():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng nhận không được lớn hơn số lượng đặt",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def ordered_quantity_must_equal_expected_qty(expected_qty):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng đặt phải bằng {expected_qty}",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def invalid_parent_status():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ có thể tạo phiếu con từ phiếu cha đã được phê duyệt",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def no_items_available_for_child_receipt():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không còn hàng bị từ chối nào để tạo phiếu nhập con",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def gr_has_no_items():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Phiếu nhập kho không có sản phẩm nào",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def gr_has_no_accepted_items():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Phiếu nhập kho không có sản phẩm nào được chấp nhận (accepted_quantity > 0)",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def can_only_update_pending():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ có thể cập nhật phiếu nhập kho ở trạng thái 'pending'",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def cant_delete_stock_updated_gr():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể xóa phiếu nhập kho đã được dùng để cập nhật tồn kho",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def cant_delete_gr_of_completed_po():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể xóa phiếu nhập kho của đơn hàng đã hoàn tất (PO completed)",
                "error_code": "gr_001",
            },
        )

    @staticmethod
    def can_only_delete_pending(current_status: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể xóa phiếu nhập kho ở trạng thái 'pending'. Trạng thái hiện tại: '{current_status}'",
                "error_code": "gr_001",
            },
        )
