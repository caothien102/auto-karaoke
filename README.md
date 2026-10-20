# 🎤 Auto Karaoke Generator

Hệ thống tự động chuyển đổi bài hát từ YouTube thành video Karaoke chuyên nghiệp sử dụng AI.

## 🚀 Tính năng nổi bật
1. **Download YouTube chất lượng cao**: Tải trực tiếp video & audio gốc thông qua `yt-dlp`.
2. **AI Tách Beat (Vocal Separation)**: Sử dụng mô hình `Demucs` của Meta AI để bóc tách giọng hát, giữ lại beat nhạc sạch, không tạp âm.
3. **AI Bắt nhịp từng từ (Word-Level Timing)**: Sử dụng `OpenAI Whisper` với cơ chế tính mốc thời gian chi tiết đến từng từ.
4. **Hiệu ứng chữ chạy Karaoke mượt mà**: Sinh file phụ đề `.ass` với thẻ `\kf` tạo hiệu ứng đổi màu chữ quét dần theo nhịp hát.
5. **Render Video tự động**: Ghép beat sạch, video nền và chữ karaoke thành file MP4 hoàn chỉnh bằng `ffmpeg`.
6. **Giao diện Web Trực Quan (Streamlit)**: Giao diện web hiện đại, xem trước video và nghe thử beat trực tiếp trên trình duyệt.

## 🛠️ Cài đặt & Khởi động

Dự án đã được cấu hình sẵn môi trường ảo tại `.venv/`.

### 1. Kích hoạt môi trường ảo:
```bash
cd auto-karaoke
source .venv/bin/activate
```

### 2. Chạy Giao diện Web (Khuyên dùng):
```bash
streamlit run web_app.py
```
*Trình duyệt sẽ tự động mở tại `http://localhost:8501`, bạn chỉ cần dán link YouTube và bấm nút.*

### 3. Hoặc chạy qua dòng lệnh (CLI):
```bash
python main.py --url "https://www.youtube.com/watch?v=..." --lang vi
```

### Các tùy chọn tham số CLI:
- `--url`, `-u`: Đường dẫn YouTube cần xử lý (bắt buộc).
- `--output`, `-o`: Thư mục lưu kết quả (mặc định: `output/`).
- `--whisper-model`, `-w`: Kích thước mô hình Whisper (`tiny`, `base`, `small`, `medium`, `large`). Mặc định: `base`.
- `--lang`, `-l`: Ngôn ngữ bài hát (`vi` cho tiếng Việt, `en` cho tiếng Anh, hoặc `auto`).
