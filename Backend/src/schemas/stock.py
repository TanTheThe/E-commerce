from enum import Enum


class StockStatus(str, Enum):
    AVAILABLE = "available"   # Có sẵn
    RESERVED = "reserved"     # Đã đặt trước
    DAMAGED = "damaged"       # Hỏng
    EXPIRED = "expired"       # Hết hạn
    QUARANTINE = "quarantine" # Cách ly
    
class TransactionType(str, Enum):
    INBOUND = "inbound"      # Nhập kho
    OUTBOUND = "outbound"    # Xuất kho
    ADJUSTMENT = "adjustment" # Điều chỉnh tồn kho
    TRANSFER = "transfer"     # Chuyển kho
    RETURN = "return"         # Trả hàng
    DAMAGED = "damaged"       # Hàng hỏng
    EXPIRED = "expired"       # Hàng hết hạn
    
class StockTransferStatus(str, Enum):
    PENDING = "pending"      
    SHIPPING = "shipping"    
    RECEIVED = "received" 
    CANCELLED = "cancelled"     
    
class StockAdjustmentStatus(str, Enum):
    DRAFT = "draft"         # mới tạo, chưa duyệt
    APPROVED = "approved"   # đã được duyệt
    APPLIED = "applied"     # đã áp dụng, hệ thống cập nhật tồn kho thực tế
    
class StockReservationStatus(str, Enum):
    ACTIVE = "active"         # đang giữ hàng
    FULFILLED = "fulfilled"   # đã được xử lý (xuất kho / đơn hàng đã thanh toán)
    CANCELLED = "cancelled"   # đã hủy (khách không mua nữa)
    EXPIRED = "expired"       # hết hạn tự động (khách không thanh toán trong thời gian cho phép)
