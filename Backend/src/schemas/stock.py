from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

    
class TransactionType(str, Enum):
    INBOUND = "inbound"      # Nhập kho
    OUTBOUND = "outbound"    # Xuất kho
    ADJUSTMENT = "adjustment" # Điều chỉnh tồn kho
    TRANSFER = "transfer"     # Chuyển kho
    RETURN = "return"         # Trả hàng
    DAMAGED = "damaged"       # Hàng hỏng
    EXPIRED = "expired"       # Hàng hết hạn

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

class ProductStockStatus(str, Enum):
    ALL = "all"
    AVAILABLE = "available"  # Còn hàng bình thường
    LOW = "low"              # Sắp hết (dưới min_stock_level)
    OUT = "out"              # Hết hàng

class SortBy(str, Enum):
    NAME = "name"
    TOTAL_QUANTITY = "total_quantity"
    UPDATED_AT = "updated_at"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class ProductVariantStockStatus(str, Enum):
    AVAILABLE = "available"
    LOW = "low"
    OUT = "out"

class StockSeverity(str, Enum):
    CRITICAL = "critical"  # Hết hàng (available = 0)
    HIGH = "high"          # Thiếu >= 80%
    MEDIUM = "medium"      # Thiếu >= 50%
    LOW = "low"            # Thiếu < 50%

    
class StockInboundItemCreate(BaseModel):
    product_variant_id: str
    quantity: int = Field(gt=0, description="Số lượng nhập vào phải > 0")
    unit_cost: int = Field(gt=0, description="Giá vốn đơn vị phải > 0")
    note: Optional[str] = None

class ProductsSummaryQueryParams(BaseModel):
    search: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Tìm kiếm theo tên, slug, SKU"
    )
    category_ids: Optional[List[str]] = Field(
        default=None,
        max_length=50,
        description="Danh sách category IDs để filter"
    )
    brand_ids: Optional[List[str]] = Field(
        default=None,
        max_length=50,
        description="Danh sách brand IDs để filter"
    )
    stock_status: ProductStockStatus = Field(
        default=ProductStockStatus.ALL,
        description="Lọc theo trạng thái stock"
    )
    sort_by: SortBy = Field(
        default=SortBy.NAME,
        description="Sắp xếp theo field nào"
    )
    sort_order: SortOrder = Field(
        default=SortOrder.ASC,
        description="Thứ tự sắp xếp"
    )

    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None

        v = v.strip()
        if not v:
            return None

        v = v.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

        return v


class LowStockQueryParams(BaseModel):
    warehouse_id: Optional[str] = Field(
        default=None,
        description="Lọc theo warehouse ID (UUID)"
    )
    severity: Optional[StockSeverity] = Field(
        default=None,
        description="Lọc theo mức độ nghiêm trọng"
    )


