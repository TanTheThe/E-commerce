Hãy audit tổng thể backend project này.

Mục tiêu KHÔNG phải sửa code ngay.

Tôi muốn bạn:

1. Tìm bug logic tiềm ẩn
2. Tìm business flow có dấu hiệu sai
3. Tìm security issue
4. Tìm performance bottleneck
5. Tìm race condition
6. Tìm query optimization issue
7. Tìm cache invalidation issue
8. Tìm transaction inconsistency
9. Tìm duplicate logic
10. Tìm dead code hoặc bad architecture

QUAN TRỌNG:
- Không được đoán bug nếu chưa đủ context.
- Nếu nghi ngờ thì đánh dấu là "Potential issue".
- Chia mức độ:
  - Critical
  - High
  - Medium
  - Low
- Với mỗi issue:
    - Vì sao nghi ngờ
    - File liên quan
    - Impact
    - Cần đọc thêm file nào để confirm

KHÔNG FIX CODE.
KHÔNG REFACTOR.
Chỉ audit tổng thể trước.