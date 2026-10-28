SAFEGUARD AI - Bản vá v3: tự xác nhận có kiểm chứng

Cài đặt: giải nén, chép đè đúng thư mục trong dự án, khởi động lại Streamlit.
Bản này bao gồm bản vá v2. Giữ nguyên best.pt, database và evidence hiện có.
Không đổi bố cục. Chỉ cập nhật nội dung giải thích quy tắc ngay trong khung hiện có.

TỰ XÁC NHẬN VIDEO
- Ít nhất 8 lần quan sát liên tiếp cùng người, cùng loại lỗi.
- Chuỗi kéo dài ít nhất 0,6 giây theo FPS video. Mất một lần quan sát hoặc có PPE đối chứng thì bắt đầu lại.
- Mỗi khoảng cách quan sát không quá 30 frame nguồn.
- Tất cả quan sát phải đủ sáng, không lóa/mờ, người đủ lớn và không chạm biên ảnh.
- Điểm Person >=65%; từng điểm vi phạm >=85%, riêng NO-Mask >=90%.
- Điểm thấp nhất trong chuỗi còn phải đạt ngưỡng người dùng chọn (75% là ngưỡng tối thiểu do người dùng đặt, không phải điều kiện duy nhất).
- Thiếu bất kỳ điều kiện kiểm chứng nào: pending; đủ điều kiện: confirmed.
- Ảnh tĩnh luôn pending do chưa có bằng chứng thời gian.
- Đây là điểm mô hình chưa được hiệu chuẩn, không phải xác suất đúng đã đo.

LƯU VẾT
JSON evidence ghi verification_policy, verification_score, support_frames,
support_seconds, verification_reason, auto_confirm_threshold và auto_triaged.
Người giám sát có thể sửa lại sự kiện tự xác nhận bằng giao diện hiện có.
Không sửa ngược trạng thái các sự kiện đã lưu từ trước.

KIỂM TRA
python validation/test_rules.py
Kiểm tra bằng dự đoán giả lập: tự xác nhận đủ điều kiện; thiếu điểm vẫn pending;
ảnh tĩnh pending; mờ/thiếu sáng chặn tự xác nhận; có PPE hoặc mất một khung thì reset;
chống ghi trùng và kiểm tra trạng thái thực tế qua hàm lưu sự kiện.
validation/frame_comparison.json là kiểm tra 24 đầu vào của bản v2 trước đó,
không phải kết quả đo precision/recall cho v3. temporal_v3.json là mẫu chuỗi của v3.
Không có bộ nhãn chuẩn, không công bố tỷ lệ chính xác hay cam kết 100%.
Chưa huấn luyện lại model. Lỗi bỏ sót ảnh người cúi và người không mũ ở xa còn tồn tại.
Cần đánh giá trên dữ liệu công trường đã gán nhãn trước khi sử dụng quyết định tự động.

Mẫu chuỗi v3: 24 khung/video, bước 5, đoạn frame 0..115, kiểm tra với analysis_fps mặc định 30. Đây là smoke test; app truyền FPS thật.
