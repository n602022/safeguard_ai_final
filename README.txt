SAFEGUARD AI — BẢN ĐỒNG BỘ V11

CÀI ĐẶT
1. Dừng tiến trình Streamlit đang chạy.
2. Chép các file trong gói vào đúng thư mục chứa app.py mà bạn chạy.
   Nếu triển khai từ deploy/app.py thì chép vào deploy/, giữ cấu trúc ui_pages/assets.
   Chép cả runtime_loader.py, ui_transition.py, app_clock.py và assets/ui_transition.js.
3. Giữ model best.pt, SQLite, evidence, chatbot, ui_components, documents và style.css.
   Gói không chứa hoặc xóa các dữ liệu này.
4. Khởi động lại Streamlit. Nếu chạy cloud, cập nhật đúng thư mục repo được triển khai
   rồi khởi động lại ứng dụng. Tải lại tab trình duyệt để bỏ script giữ hình phiên cũ.
5. Quét phiên mới. Ảnh evidence cũ có chữ vàng đã được vẽ vào pixel, không tự đổi màu.
Log khởi động có dòng SafeGuard active core với đường dẫn và mã nguồn đang nạp.

NGUYÊN NHÂN NHÃN VÀNG
core_logic(2).py người dùng gửi giống hệt v10, không còn chuỗi nhãn vàng.
app(1).py import các trang bằng from-import. Python có thể giữ hàm của phiên bản
module cũ. Chưa chứng minh đây là nguyên nhân duy nhất trên máy của người dùng.
V11 theo dõi mã nguồn và đồng bộ lại module phụ thuộc trước khi import các trang,
kể cả các tham chiếu from-import; kiểm thử tái hiện hàm cũ đã qua.
Đoạn vẽ nhãn giống nguyên văn code gốc: xanh An toan, đỏ VI PHAM; không thêm nhãn.

THAY ĐỔI TRONG PHẠM VI YÊU CẦU
- video_processor: grab mọi frame nhưng chỉ retrieve/resize frame cần quét; giữ nguyên
  chỉ số và nội dung frame. Không bỏ thêm frame so với lựa chọn tốc độ hiện có.
- detector: nạp YOLO/best.pt khi bắt đầu nhận diện; bảo vệ lệnh predict dùng chung
  giữa các phiên. Lần quét đầu vẫn phải nạp model.
- core_logic: dùng lại kết quả crop trùng trong cùng frame, không cache qua frame mới.
  Giữ thuật toán v10, không đổi trọng số model và không gán điểm dưới75 giả.
- scanner: fragment giới hạn dựng lại khi thao tác trong trang quét; dùng bộ đệm upload,
  khôi phục tệp tạm nếu bị mất; tránh sao chép byte ảnh không cần thiết; preview không chạyAI.
- giao diện: bỏ CSS ép hiện phần tử cũ; giữ hình cho đến khi có dấu hoàn tất dựng trang.
  Cơ chế giữ hình có giới hạn10giây và phụ thuộc DOM/iframe; không biến Streamlit thànhSPA.
- app_clock + dashboard/review/assistant: giữ đồng bộ giờUTC+7 từ các bản trước.
Không thay chatbot, tài liệu pháp lý, database schema, ui_components hay bố cục.

KẾT QUẢ KIỂM TRA
- 5video: frame đầu ra giống bản đọc cũ đến từngpixel với bước5 và rộng720.
  Thời gian đọc/chuẩn bị frame trong một lần đo local (chưa gồmAI):
  sample1 2.974->1.878s; sample2 .874->.694s; sample3 11.882->4.118s;
  sample4 2.479->1.741s; sample5 4.959->4.176s.
- 24ảnh/frame: nhãn/bbox/điểm đầu ra giống core_logic(2).py đã tải lên.
- SQLite phân luồng, chuyển pending69% thành confirmed85% cùng ID,
  bảo vệ quyết định người duyệt, UTC+7 và đồng bộ hàm import: PASS.
- Streamlit AppTest dựng5trang: PASS. Chưa kiểm thử trực quan vì tảiChromium lỗi.
- Ghi tệp mẫu trênmáy kiểmthử .002-.016s; đọc frame đầu .037-.816s.
  Không phải thời gian upload từ trình duyệt; chưa chứng minh hết lỗi tải5phút.

GIỚI HẠN CẦN BIẾT
Model vẫn bỏ sót thiếu mũ ở sample5, có thể báo sai dù điểm cao. Chưa fine-tune best.pt.
Chưa có đánh giá trên tập video ngoài độc lập để khẳng định AI tốt hơn bản gốc.
Quy tắc v10: >=ngưỡng được xác nhận khi vượt đối chiếu; bằng chứng mâu thuẫn vẫn
pending dù điểm thô cao. Điểm thiếu áo có thể là min của hai dự đoán cùng vùng,
không phải xác suất hiệu chuẩn. Trường hợp không phát hiện không tạo vi phạm giả.
Không cam kết chuyển trang tức thì, không còn mọi rerun, hoặc tốc độ mọi máy giống đo.
Gói này đồng bộ và sửa các điểm cụ thể; không phải tuyên bố mọi lỗi đã được giải quyết.
