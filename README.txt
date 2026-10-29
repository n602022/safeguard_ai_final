SAFEGUARD — Sửa phân luồng & chống trùng v13
Áp dụng trên v11/v12. Chỉ thay core_logic.py; giữ nguyên mọi file còn lại.
Không thay model, điều kiện phát hiện, điểm tin cậy, nhãn và giao diện.

Cài đặt:
1. Dừng app, chép đè core_logic.py vào đúng thư mục dự án đang chạy.
2. Để sửa hồ sơ cũ (ví dụ 83%, 76% đang chờ): chép repair_pending_status.py
   cạnh database.py rồi chạy tại thư mục dự án:
   python repair_pending_status.py
   Công cụ sao lưu DB và JSON liên quan vào routing_backup_... trước khi sửa.
   Chỉ chuyển hồ sơ pending do AI tạo bởi quy tắc cũ, điểm >=75%.
   Không sửa hồ sơ duyệt tay/đã loại bỏ/không có metadata xác định nguồn gốc.
   Không đổi thời điểm phát hiện, ảnh bằng chứng hay điểm nhận diện.
3. Khởi động lại app; lần quét tiếp theo dùng logic mới.

Quy tắc: confidence >= ngưỡng thanh trượt => confirmed; thấp hơn => pending.
Với ngưỡng 75%, các điểm 75%, 76%, 83% đều confirmed. Các lý do kiểm tra phụ
chỉ lưu để tham khảo, không được ép hồ sơ vượt ngưỡng thành pending nữa.

Chống trùng:
- Cùng worker_id + loại vi phạm trong một lượt quét giữ khóa ghi nhận.
- Cập nhật pending lên confirmed trên cùng event_id khi vượt ngưỡng.
- Lưu lại cùng event_ref không tạo thêm hồ sơ, không ghi đè duyệt tay.
- Khôi phục ID sau mất dấu ngắn nếu chỉ có một track phù hợp, IoU >=0.60;
  tối đa 4 lần max_inactive_frames (mặc định 360 frame nguồn).
- Không gộp tất cả người cùng loại lỗi; không gộp giữa các lần bấm quét độc lập.
- Mất dấu lâu/che khuất, đổi vị trí nhiều vẫn có thể tạo ID mới: chưa có model
  tái định danh người nên không cam kết chống trùng tuyệt đối trong mọi cảnh.
- Không xóa/gộp lịch sử #223/#220 từ ảnh: hai mã trong ảnh là hai bối cảnh khác nhau.

Kiểm tra: python validation/test_routing_dedup.py
Kiểm thử với SQLite tạm, không cần model. Đã đạt: ngưỡng và các lý do kiểm tra,
không lặp khi lưu, nâng trạng thái cùng ID, mất dấu ngắn, tách công nhân,
bảo vệ duyệt tay, sửa dữ liệu cũ và sao lưu. Chưa chạy video trên app thực tế.
