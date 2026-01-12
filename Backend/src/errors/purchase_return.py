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
    def only_admin_can_delete_pr():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": f"Chỉ admin mới có quyền xóa phiếu hoàn trả",
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
    def cant_delete_approved_return():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xóa phiếu trả hàng khi đơn hàng đã được duyệt",
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
        
    @staticmethod
    def error_while_create_pr():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi tạo phiếu hoàn trả",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def error_while_update_pr():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi chỉnh sửa phiếu hoàn trả",
                "error_code": "gr_001",
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
        
    @staticmethod
    def error_while_approve_pr():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi duyệt phiếu hoàn trả",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def error_while_confirm_pr():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi xác nhận nhận hàng hoàn trả",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def error_while_send_pr():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi gửi email hoàn trả",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def error_while_complete_pr():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có lỗi xảy ra khi hoàn tất đơn hoàn trả",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def total_returned_exceeds_amount_received(total_returned, accepted_quantity):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng hoàn trả ({total_returned}) vượt quá số lượng đã nhận ({accepted_quantity}) ",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def cant_update_return_shipped():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể cập nhật phiếu hoàn trả đã gửi hàng",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def cant_update_return_approved():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể cập nhật phiếu hoàn trả đã được duyệt",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def refund_amount_exceed_total_return(refund_amount, total_return_amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số tiền hoàn lại ({refund_amount}) không được lớn hơn tổng giá trị hoàn trả ({total_return_amount})",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def number_refunds_exceed_refund_available(return_quantity, max_returnable, already_returned, accepted_quantity):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng hoàn trả ({return_quantity}) vượt quá số lượng có thể hoàn trả "
                f"({max_returnable}). Đã hoàn trả: {already_returned}/{accepted_quantity}",
                "error_code": "gr_001",
            },
        )
        
    @staticmethod
    def refund_amount_exceeds_new_total_refund(refund_amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số tiền hoàn lại ({refund_amount}) vượt quá tổng giá trị hoàn trả mới",
                "error_code": "gr_001",
            },
        )
