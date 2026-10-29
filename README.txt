Bản sửa nút thẩm định v14

Chỉ chép đè ui_pages/review.py vào đúng thư mục dự án đang chạy, rồi khởi động lại app.
Hồ sơ confirmed: bỏ nút Xác nhận vi phạm, hai nút còn lại chia đều hai cột.
Hồ sơ pending và false_positive: giữ nguyên các nút/callback trước đây.
Không thay logic AI, dữ liệu, phân luồng hoặc chống trùng v13.
Đã kiểm tra cú pháp và thực thi nhánh nút cho cả ba trạng thái bằng UI giả lập.
