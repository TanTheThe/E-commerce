from enum import Enum


class StockStatus(str, Enum):
    DRAFT = "draft"                             # Mới tạo, chưa gửi
    SENT = "sent"                               # Đã gửi cho NCC
    CONFIRMED = "confirmed"                     # NCC đã xác nhận
    PARTIALLY_RECEIVED = "partially_received"   # Đã nhận một phần hàng
    COMPLETED = "completed"                     # Đã nhận đủ hàng
    CANCELLED = "cancelled"                     # Đơn bị hủy


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"                   # Chưa thanh toán.
    PARTIALLY_PAID = "partially_paid"   # Đã thanh toán một phần.
    PAID = "paid"                       # Thanh toán đủ.
