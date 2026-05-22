Bạn hãy audit toàn bộ Authentication/User module.

Source code nằm trong:

D:\python\E-Commerce\Backend\src\crud

Trước khi audit:
Bạn phải tự đọc toàn bộ file liên quan đến Authentication/User module để đủ context.

Bao gồm nhưng không giới hạn:
- router
- service
- repository
- model
- schema
- middleware
- token/jwt
- permission/role
- cache liên quan auth
- email/otp
- utils liên quan authentication

QUAN TRỌNG:
Không audit ngay khi mới đọc vài file.

Hãy tự dependency tracing:
Nếu file A import hoặc phụ thuộc file B,
hãy đọc tiếp file B để hiểu đủ context.

Mục tiêu:
Hiểu đầy đủ Authentication/User flow trước khi audit.

Audit theo tiêu chuẩn trong audit.md mà tôi đã cung cấp trước đó.

Khi audit:
- Không đoán business logic nếu chưa chắc.
- Nếu thiếu context thì nói rõ file còn thiếu.
- Đánh dấu issue theo mức độ:
    - Critical
    - High
    - Medium
    - Low
- Với mỗi issue:
    1. Vì sao là vấn đề
    2. File liên quan
    3. Impact
    4. Cách fix đề xuất
    5. Có chắc chắn hay cần confirm thêm context

Không refactor code ngay.
Không tự sửa code.

Trước tiên:
1. Liệt kê các file bạn sẽ đọc
2. Mapping Authentication/User flow
3. Sau đó mới audit.