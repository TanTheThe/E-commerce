from enum import Enum


class StockStatus(str, Enum):
    PENDING = "pending"               # Mới tạo, chờ xác nhận nhận hàng
    INSPECTING = "inspecting"         # Đang kiểm hàng
    APPROVED = "approved"             # Đã kiểm và duyệt
    REJECTED = "rejected"             # Bị từ chối (hàng lỗi, sai khác...).
    COMPLETED = "completed"           # Hoàn tất nhập kho

class QualityStatus(str, Enum):
    PENDING = "pending"   # chưa kiểm hàng
    PASS = "pass"         # đạt chất lượng
    FAIL = "fail"         # không đạt
    PARTIAL = "partial"   # đạt một phần (một phần bị loại)