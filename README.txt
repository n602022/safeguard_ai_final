BẢN V8 — ĐỌC TRƯỚC KHI CÀI
Đây là sửa thuật toán suy luận và lưu hồ sơ, KHÔNG phải model best.pt đã huấn luyện lại.
Cài cả core_logic.py và ui_pages/scanner.py cùng nhau. Gói là bản vá cộng dồn.
Giữ nguyên model, database, assets/style.css và bố cục hiện tại.

Thay đổi thực tế:
- Bỏ ngưỡng 75% ngầm loại dự đoán thiếu áo/khẩu trang trước khi vào chờ duyệt.
  Độ nhạy phát hiện vẫn là ngưỡng tối thiểu, mặc định 50%.
- Dự đoán có PPE yếu hơn không tự động phủ quyết dự đoán thiếu PPE mạnh hơn.
- Khi có dự đoán NO-* yếu, chạy đối chiếu ở imgsz=960. Chỉ đối chiếu cùng lớp,
  cùng vùng ảnh; không suy diễn không phát hiện mũ thành chắc chắn không mũ.
- Dự đoán vi phạm dưới 75% được kiểm tra trên crop của đúng công nhân.
  Bằng chứng có PPE rõ trên crop có thể loại một báo nhầm thiếu PPE.
- Hồ sơ AI chờ duyệt được nâng lên đã xác nhận khi frame sau của cùng công nhân/
  loại vi phạm đạt ngưỡng. Cập nhật cùng ID, ảnh/điểm bằng chứng mới, bộ đếm và
  nhật ký; giữ ảnh trước nâng cấp. Không ghi đè quyết định người duyệt.
- Phân luồng lưu DB: >=75% đã xác nhận; dưới75% chờ duyệt với ngưỡng mặc định.
  Nếu chỉnh thanh ngưỡng, sử dụng đúng giá trị đã chọn. Model vẫn có thể sai
  dù điểm cao; 75% là điểm model, chưa được hiệu chuẩn thành xác suất đúng.

KIỂM CHỨNG V8
python validation/test_rules.py
python validation/test_status_policy.py
python validation/test_event_upgrade.py
python validation/test_clock.py
Các kiểm thử dùng dữ liệu tạm, không sửa database của người dùng.
Báo cáo validation/frame_comparison_v8.json: 4 ảnh gốc + 20 frame từ5video.
Đây là so sánh đầu ra, không phải đánh giá precision/recall hoặc chứng nhận an toàn.
Chuỗi sample4 frame65: thiếu mũ78.86%, đã xác nhận.
Chuỗi sample5 frame85: thiếu áo71.75%, chờ duyệt; frame95 lên79.26%,
nâng cùng hồ sơ lên đã xác nhận. Model chạy trên video thật; cơ chế lưu SQLite
được kiểm tra riêng bằng test_event_upgrade.py. Chưa chạy end-to-end trình duyệt.
Test1: phục hồi thiếu khẩu trang70.04%, chờ duyệt khi bật kiểm tra khẩu trang.
Test4: phục hồi thiếu mũ66.74%, chờ duyệt; trước đây bị bỏ sót.
Test3: vẫn còn báo thiếu áo sai56.23% ở người bên trái; cần duyệt.
Test2: vẫn bỏ sót thiếu áo. Sample5 frame425: vẫn không phát hiện được thiếu mũ.
Không tuyên bố sửa được hai trường hợp này bằng cách đổi tên nhãn.
Thử tăng độ phân giải640/960/1280 và augment ở sample5 không khắc phục thiếu mũ;
chi tiết validation/sample5_multiscale_probe.json.
Suy luận bổ sung có chi phí xử lý; không phải tối ưu tốc độ quét/upload mới.
Muốn cải thiện model cần bộ ảnh gán nhãn đúng, gồm mẫu khó và mẫu không vi phạm,
chia train/test theo nguồn video; không lấy nhãn dự đoán của model làm đáp án chuẩn.
Chưa huấn luyện/thay best.pt, chưa đủ dữ liệu kiểm thử độc lập để cam kết mọi video.

--- GHI CHÚ CÁC BẢN TRƯỚC (V8 ƯU TIÊN KHI CÓ KHÁC BIỆT) ---

SAFEGUARD AI — Bản vá v8: sửa bộ lọc PPE và nâng cấp hồ sơ theo bằng chứng mới

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

CẬP NHẬT V7
Cài thêm ui_transition.py và assets/ui_transition.js (giữ assets/style.css cũ).
Mũ: bbox quá lớn so với người được kiểm tra lại trên crop. Nếu không có mũ đối chứng,
nhãn xanh đổi sang MŨ: CẦN KIỂM TRA, không suy diễn thành vi phạm thiếu mũ.
Đã kiểm tra thực tế sample5 frame425: nhãn Hardhat79% bị loại, chưa phát hiện NO-Hardhat.
Không thay đổi thuật toán nhận diện áo của v6.
Giao diện: vùng nội dung có key riêng từng trang; giữ bản sao DOM hiện tại trong
lớp phủ khi bấm nút/thay đổi trường nhập, bỏ lớp phủ khi Streamlit hết chạy và DOM ổn định.
Quét trực tiếp không bị giữ hình. Có thời hạn 10 giây tự gỡ để không khóa giao diện.
Cơ chế cần iframe truy cập DOM trang cha; có thể không hoạt động nếu CSP/deployment chặn.
Không biến Streamlit thành frontend cập nhật nguyên tử, không bảo đảm thời gian tức thì.
Đã kiểm tra JS syntax, Python syntax và điều hướng 5 trang bằng Streamlit AppTest.
Chưa kiểm thử trực quan trình duyệt vì tải Chromium thất bại. Đây là bản cần xác minh
trên môi trường triển khai; chưa khẳng định đã khắc phục triệt để lỗi nhấp nháy/bố cục.
