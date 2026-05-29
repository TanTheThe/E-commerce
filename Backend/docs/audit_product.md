NHIỆM VỤ: Đọc và hiểu toàn bộ source code liên quan đến Product trước khi audit.

Bối cảnh:
Đây là dự án E-commerce backend sử dụng:
- FastAPI
- SQLModel
- PostgreSQL
- AsyncSession
- Service layer
- Repository layer
- Router tách riêng
- Response schema/Pydantic model

YÊU CẦU QUAN TRỌNG:
- KHÔNG bắt đầu audit ngay.
- KHÔNG kết luận quá sớm.
- KHÔNG sửa code.
- KHÔNG refactor.
- Trước tiên phải đọc và hiểu đầy đủ toàn bộ luồng Product để xây dựng context hoàn chỉnh.

MỤC TIÊU:
Tôi muốn bạn đọc tất cả phần liên quan đến Product để hiểu:
- kiến trúc
- luồng dữ liệu
- dependency
- response contract
- logic nghiệp vụ

Sau khi hiểu đủ context mới chuyển sang audit.

==================================================
PHẠM VI CẦN ĐỌC
==================================================

1. DOMAIN MODEL

Đọc toàn bộ model liên quan:

- Product
- ProductVariant / Product_Variant
- Categories / Categories_Product
- Special_Offer hoặc logic giảm giá liên quan product

Hiểu:
- relationship
- foreign key
- UUID
- cascade
- selectin / joined relationship
- active/inactive
- soft delete nếu có

--------------------------------------------------

2. API / ROUTER

Đọc toàn bộ endpoint liên quan Product:

Admin:
- create product
- update product
- delete product
- get product detail
- get product list
- filter
- search

Customer:
- product listing
- product detail
- search/filter

Trace đầy đủ flow:
request
→ router
→ service
→ repository
→ database
→ response

--------------------------------------------------

3. SERVICE LAYER

Đọc tất cả service liên quan:

- create product
- update product
- delete product
- get detail
- get list
- category handling
- image handling
- variant handling
- validation
- pagination/filter
- response builder

Đặc biệt phải hiểu kỹ:

A. Create Product Flow
- validate gì
- insert gì trước/sau
- transaction flow

B. Update Product Flow
- update field nào
- variant update như thế nào
- category sync như thế nào
- image update như thế nào
- giữ consistency ra sao

C. Product Variant Lifecycle
- create/update/delete variant
- validation stock
- duplicate prevention
- relation consistency

--------------------------------------------------

4. REPOSITORY LAYER

Đọc toàn bộ repository method liên quan product.

Hiểu:

- joins
- selectinload
- joinedload
- query optimization
- filtering logic
- pagination logic
- sorting logic
- eager loading strategy

Xác định:
- nơi query detail
- nơi query list
- nơi update database
- nơi transaction diễn ra

--------------------------------------------------

5. SCHEMA / DTO / RESPONSE MODEL

Đọc toàn bộ schema:

Input:
- create
- update
- filter

Output:
- detail response
- list response
- variant response

Hiểu rõ:
- response contract
- field mapping
- backward compatibility

LƯU Ý:
Không được đề xuất thay đổi response contract một cách tùy tiện vì frontend đang phụ thuộc vào response hiện tại.

--------------------------------------------------

6. DEPENDENCIES

Đọc thêm những phần phụ thuộc Product:

- cache
- redis invalidation
- helper function
- validator
- middleware/permission nếu có
- role restriction
- upload image logic nếu có

==================================================
CÁCH LÀM VIỆC
==================================================

Bước 1:
Map toàn bộ kiến trúc Product domain.

Bước 2:
Lập dependency graph:
file nào gọi file nào.

Bước 3:
Trace đầy đủ luồng:

request
→ validation
→ business logic
→ repository
→ database
→ response

Bước 4:
Hiểu kỹ update flow vì đây thường là nơi dễ có bug nhất.

Bước 5:
Xác định các khu vực có khả năng rủi ro nhưng CHƯA audit sâu.

QUAN TRỌNG:
Không được đoán.
Nếu chưa hiểu dependency thì tiếp tục đọc cho đến khi rõ.

==================================================
KẾT QUẢ MONG MUỐN (CHỈ PHASE 1)
==================================================

Sau khi đọc xong, hãy trả về:

1. Tóm tắt kiến trúc Product
- Product flow end-to-end

2. Dependency Map
- danh sách file/module liên quan Product
- ai gọi ai

3. Data Flow
Giải thích luồng:
request → validation → business logic → DB → response

4. Product Update Flow
Giải thích cực kỳ chi tiết luồng update product.

5. Risk Area sơ bộ
Những chỗ “có vẻ đáng nghi”
NHƯNG chưa audit sâu.

DỪNG LẠI SAU KHI HOÀN TẤT PHASE 1.

Chờ tôi xác nhận rồi mới audit.