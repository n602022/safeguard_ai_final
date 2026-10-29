SAFEGUARD AI — Bản sửa chuyển trang v12 (áp dụng trên bản đồng bộ v11)

Chỉ thay 3 file, giữ đúng đường dẫn:
  app.py
  ui_transition.py
  assets/ui_transition.js
Không thay core_logic.py, model, dữ liệu, nhãn AI, màu sắc hoặc bố cục.

Cài đặt:
1. Dừng tiến trình Streamlit (hoặc Reboot app nếu triển khai trên Streamlit Cloud).
2. Chép đè 3 file trên vào dự án đang chạy.
3. Khởi động lại, rồi tải lại toàn bộ tab trình duyệt (Ctrl+Shift+R).
   Bước này gỡ các listener/lớp phủ JavaScript của bản cũ khỏi tab đang mở.

Sửa lỗi:
- Bỏ hoàn toàn clone DOM và Shadow DOM: bản cũ có thể mất stylesheet động,
  nhân đôi iframe/sidebar và giữ giao diện lỗi tới 10 giây.
- Dùng snapshot do trình duyệt tạo qua View Transition API, không nhân bản UI.
- Hết chờ khi trang hoàn tất; tự bỏ chuyển cảnh sau tối đa 1,5 giây nếu máy chủ chậm.
- Không giữ màn hình khi quét video, upload/download hoặc thay đổi input.
- Giữ một container nội dung có key cố định khi chuyển trang.
- Trình duyệt không hỗ trợ API dùng cơ chế hiển thị Streamlit bình thường.

Kiểm tra đã thực hiện:
- Python compileall, JavaScript syntax: đạt.
- Kiểm tra điều khiển JS bằng Node: hoàn tất, timeout, fallback, loại trừ quét/tải,
  tab ẩn, hủy listener và cài đặt một lần: đạt.
- Chưa kiểm tra trực quan trên trình duyệt chạy bản triển khai thực tế.

Giới hạn:
Không thể cam kết lần mở trang đầu tiên hoặc máy chủ xử lý chậm sẽ hiển thị tức thì.
Bản này loại bỏ nguyên nhân lớp phủ bị sai bố cục; Streamlit vẫn có quá trình rerun.
Không có thay đổi hoặc kết luận mới về chất lượng nhận diện/tốc độ AI.
