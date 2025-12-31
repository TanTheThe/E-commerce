from fastapi import HTTPException, status


class PurchaseOrderException:
    @staticmethod
    def po_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy đơn đặt hàng trên",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def only_draft_can_update():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ cho phép cập nhật đơn đặt hàng khi trạng thái là draft",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def only_sent_can_update():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ cho phép cập nhật đơn đặt hàng khi trạng thái là sent",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def only_draft_can_delete():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ cho phép xóa đơn đặt hàng khi trạng thái là draft",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def cant_delete_po_has_goods_receipts():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa đơn đặt hàng đã có phiếu nhập kho",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def cant_delete_po_has_payment():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa đơn đặt hàng đã có thanh toán",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def error_while_delete_po():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi xóa đơn đặt hàng",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def only_sent_when_draft():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể gửi PO khi trạng thái là draft",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def only_sent_when_approved():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể gửi PO khi trạng thái là approved",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def cant_approve_po_with_no_details():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể duyệt PO khi chưa có sản phẩm nào",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def cant_sent_po_with_no_details():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể gửi PO khi chưa có sản phẩm nào",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def supplier_email_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy email của nhà cung cấp. Vui lòng cung cấp email trong request",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def need_invoice_to_update_po():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Cần phải có bill/hóa đơn từ nhà cung cấp để tiến hành cập nhật thông tin hoàn chỉnh",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def cant_confirm_po_without_details():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể confirm đơn đặt hàng không có bất kì món hàng nào",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def cant_confirm_po_without_invoice():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể confirm đơn đặt hàng khi không có bill/hóa đơn từ nhà cung cấp",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def invalid_status_for_receipt():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Trạng thái đơn đặt hàng không hợp lệ cho việc nhập kho",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def po_detail_not_exist():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chi tiết đơn đặt hàng trên không tồn tại",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def variant_not_match():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Product variant không khớp với PO detail",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def order_quantity_not_equal_po_detail():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng đặt không khớp với PO",
                "error_code": "po_001",
            },
        )

    @staticmethod
    def from_date_greater_than_to_date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "from_date không được lớn hơn to_date",
                "error_code": "po_002",
            },
        )

    @staticmethod
    def invalid_po_status(invalid_statuses: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Trạng thái không hợp lệ: " + invalid_statuses,
                "error_code": "po_003",
            },
        )

    @staticmethod
    def total_amount_negative():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tổng tiền đơn đặt hàng không được âm",
                "error_code": "po_004",
            },
        )

    @staticmethod
    def error_while_send_email():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Có lỗi xảy ra khi gửi email đơn đặt hàng",
                "error_code": "po_004",
            },
        )

    @staticmethod
    def supplier_not_match_with_po():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Nhà cung cấp không khớp với đơn đặt hàng",
                "error_code": "po_004",
            },
        )

