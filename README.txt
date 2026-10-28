SAFEGUARD AI — Bản vá v6: giờ Việt Nam và phân luồng theo ngưỡng

CÀI ĐẶT
Giải nén, chép đè đúng cấu trúc thư mục rồi khởi động lại Streamlit.
Bản này bao gồm các sửa đổi trước. Không thay best.pt hay database/evidence.
Cần chép cả app_clock.py mới và các file ui_pages đi kèm.

THỜI GIAN
Toàn ứng dụng dùng UTC+7, không phụ thuộc giờ hệ điều hành/máy chủ.
Đã đồng bộ thời điểm ghi sự kiện, nhật ký duyệt, lệnh loa/dừng khẩn cấp,
chat, ngày bộ lọc dashboard, tên báo cáo và định dạng CSV.
Sự kiện mới lưu detected_at có +07:00 và timestamp_timezone trong JSON.
Timestamp có offset được đổi sang giờ Việt Nam trước khi hiển thị.
Dữ liệu cũ không có múi giờ giữ nguyên: không tự cộng 7 giờ vì có thể đã là giờ VN.

TRẠNG THÁI (CHÍNH SÁCH V6 THAY THẾ CÁC CỔNG V3–V5)
Sau khi sự kiện vượt qua bộ lọc nhận diện và được ghi nhận:
confidence >= ngưỡng người dùng chọn => confirmed;
confidence < ngưỡng người dùng chọn => pending.
Ngưỡng 75%: 69% pending, 75/85/88% confirmed.
Bỏ các cổng phụ chặn tự xác nhận theo chất lượng/kích thước/crop mâu thuẫn.
Ngưỡng không còn bị tự nâng theo độ nhạy phát hiện.
Quy tắc này áp dụng cả ảnh tĩnh; confidence cao vẫn có thể nhận nhầm.
Lọc nhận diện, kiểm tra crop, chống trùng và hỗ trợ nhiều khung video vẫn còn.
Các chỉ số temporal_quality_pass/verification_score chỉ là thông tin kiểm chứng,
không thay đổi quy tắc trạng thái theo ngưỡng.

LƯU VẾT VÀ LỊCH SỬ
JSON lưu initial_status, current_status, status_origin, triage_rule và ngưỡng.
Giám sát viên sửa trạng thái sẽ có origin human và decision_history.
Rê chuột lên huy hiệu trạng thái ở trang Duyệt để xem nguồn quyết định.
Sự kiện cũ chưa có nhật ký sẽ hiện nguồn không xác định; không suy đoán đó là AI.
Không tự phân loại lại dữ liệu lịch sử hoặc thay đổi quyết định duyệt cũ.

KIỂM TRA
python validation/test_clock.py
python validation/test_status_policy.py
python validation/test_rules.py
Đã kiểm tra UTC+7/ngày qua nửa đêm; 12 ca phân luồng thật qua SQLite tạm;
ranh giới 75%, ngưỡng cấu hình, nguồn quyết định thủ công và quy tắc nhận diện.
Các báo cáo frame_comparison/temporal_v3/verification_v4 là lịch sử kiểm thử các bản trước,
không phải đánh giá precision/recall hay kiểm thử end-to-end giao diện v6.
