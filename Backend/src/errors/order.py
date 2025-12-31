from typing import List

from fastapi import HTTPException, status

class OrderException:
    @staticmethod
    def not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy đơn hàng",
                "error_code": "order_001",
            },
        )

    @staticmethod
    def unauthorized_order():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không có quyền truy cập đơn hàng này.",
                "error_code": "order_002"
            }
        )

    @staticmethod
    def fail_get_total_sales():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không thể tính tổng doanh số",
                "error_code": "order_003",
            },
        )

    @staticmethod
    def fail_get_total_revenue():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không thể tính tổng doanh thu",
                "error_code": "order_004",
            },
        )
    
    @staticmethod
    def order_already_paid():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Đơn hàng đã được thanh toán trước đó",
                "error_code": "order_005",
            },
        )
    
    @staticmethod
    def order_not_match():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Tổng tiền trong order không khớp với tiền sau khi thanh toán",
                "error_code": "order_006",
            },
        )

    @staticmethod
    def order_already_cancelled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Đơn hàng này đã được hủy trước đó",
                "error_code": "order_007",
            },
        )

    @staticmethod
    def order_cant_cancelled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không thể hủy đơn hàng",
                "error_code": "order_008",
            },
        )

    @staticmethod
    def error_cancelled():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Có lỗi xảy ra trong quá trình hủy đơn hàng",
                "error_code": "order_009",
            },
        )

    @staticmethod
    def not_request_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đơn hàng không có yêu cầu hủy",
                "error_code": "order_010",
            },
        )

    @staticmethod
    def not_accept_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể chấp nhận hủy đơn hàng",
                "error_code": "order_011",
            },
        )

    @staticmethod
    def reason_reject_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cần cung cấp lý do từ chối",
                "error_code": "order_012",
            },
        )

    @staticmethod
    def action_invalid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Action không hợp lệ",
                "error_code": "order_013",
            },
        )

    @staticmethod
    def already_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đơn hàng đã được gửi yêu cầu hủy trước đó",
                "error_code": "order_014",
            },
        )

    @staticmethod
    def cant_update_cancel_order():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không được thay đổi trạng thái đơn hàng đang có yêu cầu hủy",
                "error_code": "order_015",
            },
        )

    @staticmethod
    def cant_reverse_cancel_order():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không được phép thay đổi trạng thái đơn hàng đã hủy",
                "error_code": "order_016",
            },
        )
    
    @staticmethod
    def only_delivered_can_return():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ có thể hoàn trả đơn hàng đã giao thành công",
                "error_code": "order_017",
            },
        )
    
    @staticmethod
    def only_payment_success_can_return():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ có thể hoàn trả đơn hàng đã thanh toán thành công",
                "error_code": "order_018",
            },
        )
    
    @staticmethod
    def not_found_delivered_at():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể xác định thời gian giao hàng",
                "error_code": "order_019",
            },
        )
    
    @staticmethod
    def overdue_return_order():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Đã quá thời hạn hoàn trả (7 ngày kể từ khi giao hàng)",
                "error_code": "order_020",
            },
        )
    
    @staticmethod
    def product_not_include_order():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Sản phẩm không thuộc đơn hàng này",
                "error_code": "order_021",
            },
        )

    @staticmethod
    def invalid_current_status():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Trạng thái hiện tại không hợp lệ",
                "error_code": "order_022",
            },
        )

    @staticmethod
    def status_already_set():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể đổi sang trạng thái đã định",
                "error_code": "order_023",
            },
        )

    @staticmethod
    def invalid_status_transition(current_status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không được phép thay đổi trạng thái từ {current_status} sang {new_status}",
                "error_code": "order_024",
            },
        )

    @staticmethod
    def current_status_cant_pick_up(current_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể xác nhận nhận hàng. Đơn hàng phải ở trạng thái 'Đã giao hàng', hiện tại là '{current_status}",
                "error_code": "order_025",
            },
        )

    @staticmethod
    def already_received():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Đơn hàng đã được xác nhận nhận hàng trước đó",
                "error_code": "order_026",
            },
        )

    @staticmethod
    def already_in_this_status():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Đơn hàng đã đang ở trạng thái này rồi",
                "error_code": "order_027",
            },
        )

    @staticmethod
    def cant_change_status(old_status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không thể chuyển từ trạng thái '{old_status}' sang '{new_status}'",
                "error_code": "order_027",
            },
        )

    @staticmethod
    def only_delivered_can_received():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ có thể nhận đơn hàng đã giao thành công",
                "error_code": "order_017",
            },
        )

    @staticmethod
    def cant_received_return():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể nhận đơn hàng đang có yêu cầu hoàn trả",
                "error_code": "order_017",
            },
        )

    @staticmethod
    def invalid_price():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Lỗi tính toán: tổng tiền không hợp lệ",
                "error_code": "order_017",
            },
        )

    @staticmethod
    def invalid_status(valid_statuses: List):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Status không hợp lệ. Chỉ chấp nhận: {', '.join(valid_statuses)}",
                "error_code": "order_017",
            },
        )

    @staticmethod
    def order_amount_mismatch():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số tiền thanh toán không khớp với tổng tiền đơn hàng",
                "error_code": "order_017",
            },
        )

    @staticmethod
    def duplicate_payment():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Thông tin thanh toán đơn hàng này đã tồn tại",
                "error_code": "order_017",
            },
        )

    @staticmethod
    def payment_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy thông tin thanh toán cho đơn hàng này",
                "error_code": "order_017",
            },
        )
    
