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
    def supplier_email_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy email của nhà cung cấp. Vui lòng cung cấp email trong request",
                "error_code": "po_001",
            },
        )

