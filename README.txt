SAFEGUARD — V10: khôi phục nhãn gốc, điều chỉnh xử lý bằng chứng
Cài vào dự án đã cập nhật v8/v9: chỉ chép đè core_logic.py rồi khởi động lại app.
Không thay app.py, CSS, bố cục, scanner.py hay model best.pt.
Đoạn vẽ tên nhãn, màu, font và phần trăm được sao chép nguyên văn từ code gốc.
Bỏ nhãn cam, nhãn nghi ngờ và cơ chế tạo NO-Hardhat từ Hardhat chưa xác minh.
Nhãn trên ảnh bằng chứng đã lưu là pixel cũ: không tự thay đổi. Hãy quét phiên mới.

Logic thay đổi:
- Nhãn PPE an toàn chỉ qua khi đạt ngưỡng độ nhạy đã chọn.
- Thiếu áo: khi toàn cảnh và crop cùng phát hiện đúng vùng thiếu áo, dùng điểm
  thấp hơn trong hai dự đoán (nếu crop đạt ngưỡng phát hiện). Lưu hai điểm gốc.
  Đây là điểm bằng chứng thận trọng, không phải xác suất đã được hiệu chuẩn.
- Thiếu mũ/khẩu trang giữ điểm nhận diện, tránh làm giảm điểm đúng do crop.
- Giữ đối chiếu crop, theo dõi nhiều frame và cập nhật hồ sơ của v9.
  Bằng chứng mâu thuẫn vẫn chờ duyệt theo v9; không ép phần trăm về74%.

Kiểm tra thực tế (model best.pt hiện có, CPU, video resize720px, bước5frame):
- Sample2: chạy từ đầu tới hết, phát sinh1 sự kiện thiếu áo64.65% ở frame155,
  chờ duyệt. Có mô phỏng nhận ID sau lưu để kiểm tra nhánh nâng cấp sau đó.
  Code gốc phát sinh4 sự kiện thiếu áo trong cùng lần chạy; đây là số đầu ra,
  không phải phép đo precision/recall. Model vẫn có thể báo thiếu áo sai.
- Sample4: frame0..99, phát hiện thiếu mũ85.2% ở frame35, không có lý do chờ duyệt.
- Sample5: đoạn375..431 chưa khắc phục bỏ sót thiếu mũ. Bỏ nhãn nghi ngờ không
  đồng nghĩa khắc phục model; dự đoán Hardhat sai có thể còn hiển thị nhãn gốc.
- Kiểm tra quy tắc, SQLite phân luồng, nâng cấp69->85 cùng hồ sơ và đoạn vẽ gốc: PASS.
- Không có video ngoài5sample do người dùng cung cấp để đánh giá độc lập.
  Chưa có cơ sở khẳng định AI tổng thể tốt hơn bản gốc, chưa huấn luyện lại model.
