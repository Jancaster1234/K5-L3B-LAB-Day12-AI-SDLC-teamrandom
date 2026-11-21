# Chuẩn bị và chạy trên Windows

Mở PowerShell tại thư mục repo. Starter chỉ dùng thư viện chuẩn Python;
không cần pip install, Node.js hay API key.

```powershell
powershell -ExecutionPolicy Bypass -File .\lab.ps1 setup
powershell -ExecutionPolicy Bypass -File .\lab.ps1 test
powershell -ExecutionPolicy Bypass -File .\lab.ps1 play
```

Mở http://127.0.0.1:8000/ để chơi thử. WASD/mũi tên để di chuyển,
E tương tác, Space bắt cá, R chơi lại. Nhấn Ctrl+C trong terminal để dừng.

```powershell
# Chế độ quán
powershell -ExecutionPolicy Bypass -File .\lab.ps1 play -Mode quan
# Chạy không giao diện, kết quả trong .local/gather.jsonl
powershell -ExecutionPolicy Bypass -File .\lab.ps1 headless -Mode gather -Ticks 600
```

Script tạo `.venv`, thêm tên lệnh `python3.exe` trong môi trường riêng để
test gọi đúng lệnh trong contract, và đặt PYTHONPATH theo cú pháp Windows.
Không cần kích hoạt venv; các thiết lập môi trường được phục hồi khi script kết thúc.
Script dùng UTF-8 cho đầu ra Python để thông báo tiếng Việt chạy được trên Windows.
`ExecutionPolicy Bypass` chỉ áp dụng cho tiến trình PowerShell đang chạy lệnh.

Trong VS Code, dùng **Python: Select Interpreter** và chọn
`.venv\Scripts\python.exe` nếu cần.

Trước khi làm bài, đọc README.md, AGENTS.md và docs/STARTER.md.
Yêu cầu mỗi phase nằm ở lab board được liên kết trong README.
Luật chơi còn các TODO dành cho nhóm trong chonoi/sim/gather.py và
chonoi/sim/quan.py. Môi trường chạy được không đồng nghĩa đã hoàn thành các phase.
