from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
import re

class GoodsReceiptStatus(str, Enum):
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



class GoodsReceiptDetailCreate(BaseModel):
    po_detail_id: str = Field(..., description="ID của purchase order detail", min_length=1, max_length=36)
    product_variant_id: str = Field(..., description="ID của product variant", min_length=1, max_length=36)
    ordered_quantity: int = Field(..., gt=0, description="Số lượng đã đặt trong PO", le=1000000)
    received_quantity: int = Field(..., ge=0, description="Số lượng thực tế nhận được", le=1000000)
    accepted_quantity: int = Field(..., ge=0, description="Số lượng chấp nhận nhập kho", le=1000000)
    rejected_quantity: int = Field(..., ge=0, description="Số lượng từ chối", le=1000000)
    rejection_reason: Optional[str] = Field(None, description="Lý do từ chối nếu có", max_length=500)
    notes: Optional[str] = Field(None, description="Ghi chú cho item này", max_length=1000)

    @field_validator('po_detail_id', 'product_variant_id')
    @classmethod
    def validate_uuid_format(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f'{info.field_name} không được để trống')

        return v.strip()

    @field_validator('rejection_reason')
    @classmethod
    def validate_rejection_reason(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) < 3:
                raise ValueError('Lý do từ chối phải có ít nhất 3 ký tự')
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    @model_validator(mode='after')
    def validate_quantities(self):
        if self.accepted_quantity + self.rejected_quantity != self.received_quantity:
            raise ValueError(
                f'Tổng số lượng chấp nhận ({self.accepted_quantity}) và từ chối ({self.rejected_quantity}) '
                f'phải bằng số lượng nhận ({self.received_quantity})'
            )

        if self.received_quantity > self.ordered_quantity:
            raise ValueError(
                f'Số lượng nhận ({self.received_quantity}) không được lớn hơn '
                f'số lượng đặt ({self.ordered_quantity})'
            )

        if self.rejected_quantity > 0 and not self.rejection_reason:
            raise ValueError(
                'Phải cung cấp lý do từ chối (rejection_reason) khi có số lượng từ chối'
            )

        if self.rejected_quantity == 0 and self.rejection_reason:
            raise ValueError(
                'Không nên cung cấp lý do từ chối khi không có sản phẩm bị từ chối'
            )

        return self

class CreateGoodsReceiptRequest(BaseModel):
    purchase_order_id: str = Field(..., description="ID của đơn đặt hàng", min_length=1, max_length=36)
    warehouse_id: str = Field(..., description="ID kho nhận hàng", min_length=1, max_length=36)
    supplier_id: str = Field(..., description="ID nhà cung cấp", min_length=1, max_length=36)
    receipt_date: datetime = Field(default_factory=datetime.now, description="Ngày nhận hàng")
    delivery_note_number: Optional[str] = Field(None, description="Số phiếu giao hàng", max_length=50)
    parent_receipt_id: Optional[str] = Field(None, description="ID của GR cha (cho GR2, GR3...)", max_length=36)
    notes: Optional[str] = Field(None, description="Ghi chú chung", max_length=2000)
    items: List[GoodsReceiptDetailCreate] = Field(..., description="Danh sách sản phẩm nhập kho", min_length=1,
                                                  max_length=1000)

    @field_validator('purchase_order_id', 'warehouse_id', 'supplier_id', 'parent_receipt_id')
    @classmethod
    def validate_uuid_format(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            return v

        if not v.strip():
            raise ValueError(f'{info.field_name} không được để trống')

        return v.strip()

    @field_validator('receipt_date')
    @classmethod
    def validate_receipt_date(cls, v: datetime) -> datetime:
        if v is None:
            raise ValueError('Ngày nhận hàng không được để trống')

        now = datetime.now()
        if v > now.replace(hour=23, minute=59, second=59):
            raise ValueError('Ngày nhận hàng không được là ngày trong tương lai')

        one_year_ago = now.replace(year=now.year - 1)
        if v < one_year_ago:
            raise ValueError('Ngày nhận hàng không được quá 1 năm trước')

        return v

    @field_validator('delivery_note_number')
    @classmethod
    def validate_delivery_note_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) < 2:
                raise ValueError('Số phiếu giao hàng phải có ít nhất 2 ký tự')
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    @model_validator(mode='after')
    def validate_request(self):
        po_detail_ids = [item.po_detail_id for item in self.items]
        if len(po_detail_ids) != len(set(po_detail_ids)):
            duplicates = [pid for pid in po_detail_ids if po_detail_ids.count(pid) > 1]
            duplicates_unique = list(set(duplicates))
            raise ValueError(
                f'Có po_detail_id bị trùng lặp trong danh sách items: {", ".join(duplicates_unique)}'
            )

        variant_ids = [item.product_variant_id for item in self.items]
        if len(variant_ids) != len(set(variant_ids)):
            duplicates = [vid for vid in variant_ids if variant_ids.count(vid) > 1]
            duplicates_unique = list(set(duplicates))
            raise ValueError(
                f'Có product_variant_id bị trùng lặp trong danh sách items: {", ".join(duplicates_unique)}'
            )

        if hasattr(self.receipt_date, 'tzinfo') and self.receipt_date.tzinfo is not None:
            self.receipt_date = self.receipt_date.replace(tzinfo=None)

        return self




class SortBy(str, Enum):
    RECEIPT_DATE_ASC = "receipt_date_asc"
    RECEIPT_DATE_DESC = "receipt_date_desc"
    CREATED_AT_ASC = "created_at_asc"
    CREATED_AT_DESC = "created_at_desc"
    TOTAL_AMOUNT_ASC = "total_amount_asc"
    TOTAL_AMOUNT_DESC = "total_amount_desc"

class GetAllGoodsReceiptsQueryParams(BaseModel):
    warehouse_id: str = Field(..., description="ID của warehouse (bắt buộc)", min_length=1, max_length=36)
    status_gr: Optional[GoodsReceiptStatus] = Field(None, description="Trạng thái phiếu")
    purchase_order_id: Optional[str] = Field(None, description="ID đơn hàng", max_length=36)
    supplier_id: Optional[str] = Field(None, description="ID nhà cung cấp", max_length=36)
    from_date: Optional[datetime] = Field(None, description="Từ ngày")
    to_date: Optional[datetime] = Field(None, description="Đến ngày")
    search: Optional[str] = Field(None, description="Tìm kiếm theo receipt_number hoặc delivery_note_number", max_length=100)
    sort_by: Optional[SortBy] = Field(None, description="Sắp xếp theo")

    @field_validator('warehouse_id', 'purchase_order_id', 'supplier_id')
    @classmethod
    def validate_uuid_format(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            return v

        if not v.strip():
            raise ValueError(f'{info.field_name} không được để trống')

        return v.strip()

    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        v = v.strip()
        if len(v) == 0:
            return None

        if len(v) < 2:
            raise ValueError('Từ khóa tìm kiếm phải có ít nhất 2 ký tự')

        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Từ khóa tìm kiếm chỉ được chứa chữ, số, khoảng trắng, dấu gạch ngang và gạch dưới')

        return v

    @field_validator('from_date', 'to_date')
    @classmethod
    def validate_dates(cls, v: Optional[datetime], info) -> Optional[datetime]:
        if v is None:
            return v

        two_years_ago = datetime.now() - timedelta(days=730)
        if v < two_years_ago:
            raise ValueError(f'{info.field_name} không được quá 2 năm trước')

        tomorrow = datetime.now() + timedelta(days=1)
        if v > tomorrow:
            raise ValueError(f'{info.field_name} không được trong tương lai')

        if hasattr(v, 'tzinfo') and v.tzinfo is not None:
            v = v.replace(tzinfo=None)

        return v

    @model_validator(mode='after')
    def validate_date_range(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValueError('from_date không được lớn hơn to_date')

            max_range = timedelta(days=365)
            if (self.to_date - self.from_date) > max_range:
                raise ValueError('Khoảng thời gian tìm kiếm không được vượt quá 1 năm')

        return self




class ReceiptDetailUpdate(BaseModel):
    id: Optional[str] = Field(None, description="ID của detail (có = update, không có = create)", max_length=36)
    product_variant_id: str = Field(..., description="ID của product variant", min_length=1, max_length=36)
    po_detail_id: str = Field(..., description="ID của purchase order detail", min_length=1, max_length=36)
    ordered_quantity: int = Field(..., gt=0, le=1000000, description="Số lượng đặt hàng ban đầu trong PO")
    received_quantity: int = Field(..., ge=0, le=1000000, description="Số lượng thực nhận từ nhà cung cấp")
    accepted_quantity: int = Field(..., ge=0, le=1000000, description="Số lượng chấp nhận nhập kho")
    rejected_quantity: int = Field(default=0, ge=0, le=1000000, description="Số lượng từ chối")
    unit_cost: int = Field(..., gt=0, le=1000000000, description="Giá nhập trên mỗi đơn vị")
    rejection_reason: Optional[str] = Field(None, description="Lý do từ chối", max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('id', 'product_variant_id', 'po_detail_id')
    @classmethod
    def validate_uuid_format(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            return v

        if not v.strip():
            raise ValueError(f'{info.field_name} không được để trống')

        return v.strip()

    @field_validator('rejection_reason', 'notes')
    @classmethod
    def validate_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if cls.__name__ == 'rejection_reason' and len(v) < 3:
                raise ValueError('Lý do từ chối phải có ít nhất 3 ký tự')
        return v

    @model_validator(mode='after')
    def validate_quantities(self):
        if self.accepted_quantity + self.rejected_quantity != self.received_quantity:
            raise ValueError(
                f'accepted_quantity ({self.accepted_quantity}) + rejected_quantity ({self.rejected_quantity}) '
                f'phải bằng received_quantity ({self.received_quantity})'
            )

        if self.received_quantity > self.ordered_quantity:
            raise ValueError(
                f'received_quantity ({self.received_quantity}) không được lớn hơn '
                f'ordered_quantity ({self.ordered_quantity})'
            )

        if self.rejected_quantity > 0 and not self.rejection_reason:
            raise ValueError('Phải cung cấp rejection_reason khi có rejected_quantity > 0')

        if self.rejected_quantity == 0 and self.rejection_reason:
            raise ValueError('Không nên cung cấp rejection_reason khi rejected_quantity = 0')

        return self


class UpdateGoodsReceiptRequest(BaseModel):
    receipt_date: Optional[datetime] = Field(None, description="Ngày nhận hàng thực tế")
    delivery_note_number: Optional[str] = Field(None, description="Số phiếu giao hàng của NCC", max_length=50)
    has_discrepancy: Optional[bool] = Field(None, description="Có sai lệch không?")
    discrepancy_notes: Optional[str] = Field(None, description="Ghi chú về sai lệch", max_length=2000)
    notes: Optional[str] = Field(None, description="Ghi chú chung", max_length=2000)
    receipt_details: Optional[List[ReceiptDetailUpdate]] = Field(None, description="Danh sách chi tiết nhập kho",
                                                                 min_length=1, max_length=1000)

    @field_validator('receipt_date')
    @classmethod
    def validate_receipt_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v

        now = datetime.now()
        if v > now.replace(hour=23, minute=59, second=59):
            raise ValueError('receipt_date không được là ngày trong tương lai')

        one_year_ago = now - timedelta(days=365)
        if v < one_year_ago:
            raise ValueError('receipt_date không được quá 1 năm trước')

        if hasattr(v, 'tzinfo') and v.tzinfo is not None:
            v = v.replace(tzinfo=None)

        return v

    @field_validator('delivery_note_number')
    @classmethod
    def validate_delivery_note(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) < 2:
                raise ValueError('delivery_note_number phải có ít nhất 2 ký tự')

            if not re.match(r'^[a-zA-Z0-9\-_]+$', v):
                raise ValueError('delivery_note_number chỉ được chứa chữ, số, dấu gạch')
        return v

    @field_validator('discrepancy_notes', 'notes')
    @classmethod
    def validate_text_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate và trim text fields"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    @model_validator(mode='after')
    def validate_request_logic(self):
        if self.has_discrepancy is True and not self.discrepancy_notes:
            raise ValueError('Phải cung cấp discrepancy_notes khi has_discrepancy = True')

        if self.receipt_details is not None and len(self.receipt_details) == 0:
            raise ValueError('receipt_details phải có ít nhất 1 item')

        if self.receipt_details:
            po_detail_ids = [d.po_detail_id for d in self.receipt_details]
            if len(po_detail_ids) != len(set(po_detail_ids)):
                duplicates = [pid for pid in po_detail_ids if po_detail_ids.count(pid) > 1]
                raise ValueError(f'Có po_detail_id bị trùng: {list(set(duplicates))}')

            variant_ids = [d.product_variant_id for d in self.receipt_details]
            if len(variant_ids) != len(set(variant_ids)):
                duplicates = [vid for vid in variant_ids if variant_ids.count(vid) > 1]
                raise ValueError(f'Có product_variant_id bị trùng: {list(set(duplicates))}')

        return self