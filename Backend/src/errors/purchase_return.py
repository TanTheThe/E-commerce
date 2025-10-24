from fastapi import HTTPException, status


class PurchaseReturnException:
    @staticmethod
    def pr_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Phiếu hoàn trả không tồn tại",
                "error_code": "pr_001",
            },
        )

    @staticmethod
    def no_return_details_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chi tiết phiếu hoàn trả không tồn tại",
                "error_code": "pr_001",
            },
        )

    @staticmethod
    def pr_must_be_in_confirmed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Phiếu hoàn trả phải đang ở trạng thái confirmed",
                "error_code": "pr_001",
            },
        )
        
    @staticmethod
    def required_to_create():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể tạo phiếu hoàn trả từ phiếu nhập đã được duyệt",
                "error_code": "pr_001",
            },
        )
        
    @staticmethod
    def return_quantity_must_greater_than_0():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng trả phải lớn hơn 0",
                "error_code": "pr_001",
            },
        )
        
    @staticmethod
    def return_quantity_greater_than_max_returnable():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng trả vượt quá số lượng có thể trả",
                "error_code": "pr_001",
            },
        )
        
    @staticmethod
    def only_approved_when_draft():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể duyệt phiếu ở trạng thái draft",
                "error_code": "pr_001",
            },
        )

    @staticmethod
    def only_confirmed_when_sent():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể nhận đơn hàng khi trước đó là sent",
                "error_code": "pr_001",
            },
        )
        
    @staticmethod
    def only_send_mail_when_approved():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể gửi email với phiếu đã được duyệt",
                "error_code": "pr_001",
            },
        )
        
    @staticmethod
    def supplier_email_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy email nhà cung cấp",
                "error_code": "pr_001",
            },
        )

    @staticmethod
    def only_complete_when_confirmed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể hoàn tất phiếu đang ở trạng thái confirmed",
                "error_code": "pr_001",
            },
        )

    @staticmethod
    def only_update_when_draft():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể cập nhật phiếu đang ở trạng thái draft",
                "error_code": "pr_001",
            },
        )

    @staticmethod
    def cant_delete_shipped_return():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa phiếu trả hàng khi đơn hàng đã được gửi trả",
                "error_code": "pr_001",
            },
        )

    @staticmethod
    def only_delete_when_draft():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Chỉ có thể xóa phiếu đang ở trạng thái draft",
                "error_code": "pr_001",
            },
        )

    @staticmethod
    def error_while_delete_pr():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi xóa phiếu hoàn trả",
                "error_code": "gr_001",
            },
        )
