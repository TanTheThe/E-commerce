from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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

class WarehouseRole(str, Enum):
    MANAGER = "manager"  # Quản lý kho
    WAREHOUSE_KEEPER = "warehouse_keeper"  # Thủ kho
    STOCK_CLERK = "stock_clerk"  # Nhân viên kho
    PICKER = "picker"  # Nhân viên lấy hàng
    PACKER = "packer"  # Nhân viên đóng gói

class StockStatusFilter(str, Enum):
    AVAILABLE = "available"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    OVERSTOCKED = "overstocked"

class StockFilterParams(BaseModel):
    status: Optional[StockStatusFilter] = Field(None, description="Lọc theo trạng thái")
    min_quantity: Optional[int] = Field(None, ge=0, description="Số lượng tối thiểu")
    max_quantity: Optional[int] = Field(None, ge=0, description="Số lượng tối đa")
    low_stock_only: bool = Field(False, description="Chỉ hiện sản phẩm sắp hết")
    out_of_stock_only: bool = Field(False, description="Chỉ hiện sản phẩm hết hàng")

class TotalInventoryFilterParams(BaseModel):
    brand_id: Optional[str] = Field(None, description="Lọc theo thương hiệu")
    material_id: Optional[str] = Field(None, description="Lọc theo chất liệu")
    tag_id: Optional[str] = Field(None, description="Lọc theo tag")
    status: Optional[StockStatusFilter] = Field(None, description="Lọc theo trạng thái")
    min_quantity: Optional[int] = Field(None, ge=0, description="Số lượng tối thiểu")
    max_quantity: Optional[int] = Field(None, ge=0, description="Số lượng tối đa")
    search: Optional[str] = Field(None, description="Tìm kiếm theo tên/SKU sản phẩm")
