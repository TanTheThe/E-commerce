from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid
from src.schemas.material import ProductMaterialCreateModel
from src.schemas.product_variant import ProductVariantCreateModel, ProductVariantUpdateModel
from enum import Enum


class ProductCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên sản phẩm")
    images: List[str] = Field(...)
    description: Optional[str] = Field(None, max_length=5000)
    short_description: Optional[str] = Field(None, max_length=500)
    categories_id: List[str] = Field(...)
    product_variant: List[ProductVariantCreateModel] = Field(...)
    brand_id: Optional[str] = None
    materials: Optional[List[ProductMaterialCreateModel]] = None
    tags_id: Optional[List[str]] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Tên sản phẩm không được để trống")
        return ' '.join(v.split())

    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        if len(v) < 1 or len(v) > 10:
            raise ValueError("Chỉ được cung cấp từ 1 đến 10 ảnh")

        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        for img in v:
            if not img.startswith('https://'):
                raise ValueError("Image URL phải bắt đầu bằng https://")
            if not any(img.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError("Image phải có định dạng: jpg, jpeg, png, webp hoặc gif")

        return v

    @field_validator('categories_id')
    @classmethod
    def validate_categories(cls, v):
        if len(v) < 1 or len(v) > 10:
            raise ValueError("Chỉ được cung cấp từ 1 đến 10 category")
        if len(v) != len(set(v)):
            raise ValueError("Danh sách categories có ID trùng lặp")
        return v

    @field_validator('tags_id')
    @classmethod
    def validate_tags(cls, v):
        if v:
            if len(v) > 20:
                raise ValueError("Chỉ được cung cấp tối đa 20 tags")
            if len(v) != len(set(v)):
                raise ValueError("Danh sách tags có ID trùng lặp")
        return v

    @field_validator('materials')
    @classmethod
    def validate_materials(cls, v):
        if v:
            if len(v) > 20:
                raise ValueError("Chỉ được cung cấp tối đa 20 vật liệu")

            total = sum(m.percentage for m in v)
            if total > 100:
                raise ValueError(f"Tổng phần trăm vật liệu vượt quá 100% (hiện tại: {total}%)")

            material_ids = [m.material_id for m in v]
            if len(material_ids) != len(set(material_ids)):
                raise ValueError("Có vật liệu bị trùng lặp")
        return v

    @field_validator('product_variant')
    @classmethod
    def validate_product_variant(cls, v):
        if len(v) < 1:
            raise ValueError("Phải cung cấp ít nhất 1 biến thể")
        return v

class MaterialUpdateModel(BaseModel):
    material_id: str = Field(..., description="ID của chất liệu")
    percentage: float = Field(..., ge=0.01, le=100, description="Phần trăm chất liệu (0.01-100)")

    @field_validator('percentage')
    @classmethod
    def validate_percentage(cls, v):
        if round(v, 2) != v:
            raise ValueError('Phần trăm chỉ được phép tối đa 2 chữ số thập phân')
        return v

class ProductUpdateModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên sản phẩm")
    images: Optional[List[str]] = Field(None, description="Danh sách URL ảnh sản phẩm (1-10 ảnh)")
    description: Optional[str] = Field(None, max_length=10000, description="Mô tả chi tiết sản phẩm")
    short_description: Optional[str] = Field(None, max_length=500, description="Mô tả ngắn gọn")
    status: Optional[str] = Field(None, description="Trạng thái sản phẩm")
    categories_id: Optional[List[str]] = Field(None, description="Danh sách ID danh mục (1-5 danh mục)")
    brand_id: Optional[str] = Field(None, description="ID thương hiệu")
    materials: Optional[List[MaterialUpdateModel]] = Field(None, description="Danh sách chất liệu (1-10 chất liệu)")
    tags_id: Optional[List[str]] = Field(None, description="Danh sách ID tags (tối đa 20 tags)")
    product_variant: Optional[List[ProductVariantUpdateModel]] = Field(None, description="Danh sách variants (1-50 variants)")
    deleted_variant_ids: Optional[List[str]] = Field(None, description="Danh sách ID variants cần xóa")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v:
            v = v.strip()
            if not v:
                raise ValueError('Tên sản phẩm không được để trống')

            dangerous_chars = ['<', '>', '{', '}', '\\', ';']
            if any(char in v for char in dangerous_chars):
                raise ValueError('Tên sản phẩm chứa ký tự không hợp lệ')
        return v

    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        if v:
            if len(v) < 1:
                raise ValueError('Phải có ít nhất 1 ảnh')
            if len(v) > 10:
                raise ValueError('Tối đa 10 ảnh')

            valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
            for idx, url in enumerate(v):
                url = url.strip()
                if not url:
                    raise ValueError(f'URL ảnh thứ {idx + 1} không được để trống')
                if not url.startswith(('http://', 'https://', '/')):
                    raise ValueError(f'URL ảnh thứ {idx + 1} không hợp lệ')
                if not any(url.lower().endswith(ext) for ext in valid_extensions):
                    raise ValueError(
                        f'Ảnh thứ {idx + 1} phải có định dạng: {", ".join(valid_extensions)}'
                    )

            if len(v) != len(set(v)):
                raise ValueError('Danh sách ảnh có URL trùng lặp')

        return v

    @field_validator('description', 'short_description')
    @classmethod
    def validate_description(cls, v):
        if v:
            v = v.strip()
            dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
            v_lower = v.lower()
            if any(pattern in v_lower for pattern in dangerous_patterns):
                raise ValueError('Mô tả chứa nội dung không hợp lệ')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v:
            v = v.strip().lower()
            valid_statuses = ['active', 'inactive', 'draft', 'out_of_stock']
            if v not in valid_statuses:
                raise ValueError(
                    f'Trạng thái không hợp lệ. Chỉ chấp nhận: {", ".join(valid_statuses)}'
                )
        return v

    @field_validator('categories_id')
    @classmethod
    def validate_categories(cls, v):
        if v:
            if len(v) < 1:
                raise ValueError('Phải có ít nhất 1 danh mục')
            if len(v) > 5:
                raise ValueError('Tối đa 5 danh mục')
            if len(v) != len(set(v)):
                raise ValueError('Danh sách danh mục có ID trùng lặp')
        return v

    @field_validator('tags_id')
    @classmethod
    def validate_tags(cls, v):
        if v:
            if len(v) > 20:
                raise ValueError('Tối đa 20 tags')
            if len(v) != len(set(v)):
                raise ValueError('Danh sách tags có ID trùng lặp')
        return v

    @field_validator('materials')
    @classmethod
    def validate_materials(cls, v):
        if v:
            if len(v) < 1:
                raise ValueError('Phải có ít nhất 1 chất liệu')
            if len(v) > 10:
                raise ValueError('Tối đa 10 chất liệu')

            material_ids = [m.material_id for m in v]
            if len(material_ids) != len(set(material_ids)):
                raise ValueError('Danh sách chất liệu có ID trùng lặp')

            total_percentage = sum(m.percentage for m in v)
            if abs(total_percentage - 100) > 0.01:
                raise ValueError(
                    f'Tổng phần trăm chất liệu phải bằng 100% (hiện tại: {total_percentage}%)'
                )
        return v

    @field_validator('product_variant')
    @classmethod
    def validate_variants(cls, v):
        if v:
            if len(v) < 1:
                raise ValueError('Phải có ít nhất 1 variant')
            if len(v) > 50:
                raise ValueError('Tối đa 50 variants')

            skus = [var.sku for var in v if var.sku]
            if len(skus) != len(set(skus)):
                raise ValueError('Danh sách variants có SKU trùng lặp')

            combinations = []
            for var in v:
                color_key = str(var.color_id) if var.color_id else f"{var.color_name}_{var.color_code}"
                combo = f"{var.size}_{color_key}"
                if combo in combinations:
                    raise ValueError(
                        f'Variant với size "{var.size}" và màu này đã tồn tại'
                    )
                combinations.append(combo)

        return v

    @field_validator('deleted_variant_ids')
    @classmethod
    def validate_deleted_ids(cls, v):
        if v:
            if len(v) != len(set(v)):
                raise ValueError('Danh sách ID variants cần xóa có giá trị trùng lặp')
        return v

class DeleteMultipleProductModel(BaseModel):
    product_ids: List[str]

class SortBy(str, Enum):
    newest = "newest"
    oldest = "oldest"
    price_asc = "price_asc"
    price_desc = "price_desc"
    name_asc = "name_asc"
    name_desc = "name_desc"
    best_seller = "best_seller"
    sale_desc = "sale_desc"
    rating_desc = "rating_desc"

class ProductFilterModel(BaseModel):
    search: Optional[str] = Field(None, max_length=200, description="Tìm kiếm theo tên sản phẩm")
    category_ids: Optional[List[str]] = None
    category_slugs: Optional[List[str]] = None
    min_price: Optional[int] = Field(None, ge=0, description="Giá tối thiểu >= 0")
    max_price: Optional[int] = Field(None, ge=0, description="Giá tối đa >= 0")
    sort_by: Optional[SortBy] = None
    colors: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    rating: Optional[List[int]] = None
    brand_id: Optional[str] = None
    material_ids: Optional[List[str]] = None

    @field_validator('search')
    @classmethod
    def validate_search(cls, v):
        if v:
            cleaned = ' '.join(v.split())
            if len(cleaned) < 2:
                raise ValueError("Từ khóa tìm kiếm phải có ít nhất 2 ký tự")
            return cleaned
        return v

    @field_validator('min_price', 'max_price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("Giá không được âm")
        return v

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v:
            if len(v) > 5:
                raise ValueError("Chỉ được cung cấp tối đa 5 rating")
            for r in v:
                if r < 1 or r > 5:
                    raise ValueError("Rating phải từ 1-5")
        return v

    @field_validator('category_ids')
    @classmethod
    def validate_category_ids(cls, v):
        if v:
            if len(v) > 20:
                raise ValueError("Chỉ được cung cấp tối đa 20 category IDs")
            if len(v) != len(set(v)):
                raise ValueError("Danh sách categories có ID trùng lặp")
        return v

    @field_validator('category_slugs')
    @classmethod
    def validate_category_slugs(cls, v):
        if v:
            if len(v) > 20:
                raise ValueError("Chỉ được cung cấp tối đa 20 category slugs")
            if len(v) != len(set(v)):
                raise ValueError("Danh sách category slugs có giá trị trùng lặp")
        return v

    @field_validator('material_ids')
    @classmethod
    def validate_material_ids(cls, v):
        if v:
            if len(v) > 20:
                raise ValueError("Chỉ được cung cấp tối đa 20 material IDs")
            if len(v) != len(set(v)):
                raise ValueError("Danh sách material_ids có ID trùng lặp")
        return v

    @field_validator('colors')
    @classmethod
    def validate_colors(cls, v):
        if v:
            if len(v) > 50:
                raise ValueError("Chỉ được cung cấp tối đa 50 colors")
            if len(v) != len(set(v)):
                raise ValueError("Danh sách colors có giá trị trùng lặp")
        return v

    @field_validator('sizes')
    @classmethod
    def validate_sizes(cls, v):
        if v:
            if len(v) > 20:
                raise ValueError("Chỉ được cung cấp tối đa 20 sizes")
            if len(v) != len(set(v)):
                raise ValueError("Danh sách sizes có giá trị trùng lặp")
        return v

    @model_validator(mode='after')
    def validate_price_range(self):
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError("min_price không được lớn hơn max_price")
        return self
            

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class ProductStatusUpdateModel(BaseModel):
    status: ProductStatus

class BulkUpdateStatusModel(BaseModel):
    product_ids: List[str]
    status: ProductStatus

    @field_validator('product_ids')
    @classmethod
    def validate_product_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Danh sách sản phẩm không được rỗng")

        if len(v) > 1000:
            raise ValueError("Không thể cập nhật quá 1000 sản phẩm cùng lúc")

        unique_ids = list(set(v))
        if len(unique_ids) != len(v):
            raise ValueError("Danh sách sản phẩm có ID trùng lặp")

        return unique_ids