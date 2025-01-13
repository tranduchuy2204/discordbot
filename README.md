# 🤖 Discord Music Bot

## 🌟 Giới Thiệu

Đây là một Discord Bot đa chức năng được phát triển bằng Python, sử dụng thư viện `discord.py` và `wavelink`. Bot cung cấp các tính năng phát nhạc, quản lý server và nhiều tiện ích khác.

## ✨ Tính Năng

### 🎵 Chức Năng Âm Nhạc

-   Phát nhạc từ YouTube
-   Chọn bài hát từ danh sách kết quả
-   Điều khiển phát nhạc (pause/resume, skip, stop)
-   Điều chỉnh âm lượng
-   Chế độ lặp bài hát
-   Hiển thị danh sách phát

### 👥 Quản Lý Server

-   Chào mừng thành viên mới
-   Thông báo khi thành viên rời server
-   Xử lý lỗi và thông báo chi tiết

## 🚀 Yêu Cầu Hệ Thống

-   Python 3.8+
-   discord.py
-   wavelink
-   Lavalink server

## 🔧 Cài Đặt

1. Clone repository:

```bash
git clone https://github.com/tranduchuy2204/discordbot.git
```

2. Tạo môi trường ảo:
   Linux:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

4. Cấu hình bot:

-   Điền token bot vào `config.py`
-   Cấu hình Lavalink server

## 🖥️ Chạy Bot

```bash
python main.py
```

## 📝 Cấu hình

Chỉnh sửa file `config.py` để cấu hình:

-   Token Discord Bot
-   Thông tin kết nối Lavalink
-   API key Gemini
-   Prefix lệnh

## 📝 Lệnh Sử Dụng

### 📝 Lệnh Slash

-   `/play`: Phát nhạc từ YouTube
-   `/queue`: Xem danh sách phát
-   `/volume`: Điều chỉnh âm lượng
-   `/stop`: Dừng phát nhạc
-   `/pay`: Tạo mã QR thanh toán
-   `/userinfo`: Xem thông tin người dùng
-   `/avatar`: Xem avatar người dùng
-   `/server`: Xem thông tin server
-   `/chat`: Chat với AI
-   `/clear`: Xóa tin nhắn

## 🛠️ Yêu cầu

-   Python 3.8+
-   discord.py
-   wavelink
-   youtube-dl
-   PyNaCl
-   google-generativeai

## 📄 Giấy Phép

Được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm chi tiết.

## 👨‍💻 Tác Giả

Trần Đức Huy

## 🙏 Lời Cảm Ơn

-   [discord.py](https://discordpy.readthedocs.io/)
-   [wavelink](https://wavelink.dev/)
-   Cộng đồng open-source
