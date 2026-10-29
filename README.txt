Bản điều chỉnh nhãn trên nền v9.
Chép đè core_logic.py vào dự án đã cập nhật v9, rồi khởi động lại app.
Bỏ nhãn cam: trường hợp mũ chưa xác minh dùng khung đỏ NGHI NGỜ: KHÔNG MŨ
[CHỜ DUYỆT], vẫn tạo hồ sơ pending. Trường hợp PPE mâu thuẫn cũng hiển thị
NGHI NGỜ và CHỜ DUYỆT thay vì khẳng định VI PHẠM.
Không tạo trạng thái mới; không thay bố cục.
Không gán 74% giả cho trường hợp model chưa dự đoán thiếu mũ.
Giữ nguyên thuật toán v9; chưa huấn luyện lại model, chưa chạy model/video
trong lần điều chỉnh này. Không khẳng định cải thiện độ chính xác nhận diện.
Ngưỡng75% vẫn có ngoại lệ cần duyệt khi bằng chứng mâu thuẫn như v9.
