---
name: ui-screenshot-check
description: Kiểm giao diện cửa sổ chơi (chonoi.live) bằng ảnh chụp thật — chơi trọn một Ngày bằng bot, bấm phím thật qua Edge DevTools, chụp Menu, DayIntro, Buổi tối, Kết quả Ngày, Shop, Tổng kết và chế độ tương phản cao. Dùng sau mọi thay đổi ở chonoi/web/ hoặc live.py, trước khi gộp/tag.
---

# Kiểm giao diện bằng ảnh chụp

Test tự động không thấy chữ đè nhau, sprite không tải, emoji thành ô vuông, màn phủ không đóng.
Skill này chơi thật một Ngày và chụp từng màn để người (hoặc agent) **đọc ảnh** rồi mới kết luận.

## Cần có
- Windows có Microsoft Edge; Node ≥ 22 (có `WebSocket` sẵn); venv của `lab.ps1 setup`.
- Chạy từ gốc repo. Ảnh ghi ra thư mục tạm, chỉ chép ảnh đã đọc vào `docs/proof/<phase>/ui/`.

## Chạy

```powershell
$env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'
# Terminal 1: một Ngày, cổng riêng (8000 có thể bị Windows chặn — WinError 10013)
.\.venv\Scripts\python.exe -m chonoi.live --mode day --days 1 --seed 1 --port 8790
# Terminal 2: bot + chụp (≈ 7 phút: 3 phút lặn + 3 phút quán + Shop)
node .agents/skills/ui-screenshot-check/scripts/playday.mjs 8790 .local/ui "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe" .local/edge-profile
```

Script mở trang trong Edge headless (`--remote-debugging-port`), bấm **Enter / H / 1** bằng
`Input.dispatchKeyEvent`, còn di chuyển nhân vật bằng `POST /input` (cùng API trang web dùng):
hái bông súng N3/N4 ở mặt nước, về bến cất đồ, tối nấu → bưng → phục vụ, vào Shop bấm `1`, đóng Shop.

Ảnh tạo ra: `01-menu`, `02-dayintro`, `03-evening`, `04-day-result`, `05-shop`, `06-summary`, `07-high-contrast` (.png).

## Đọc kết quả
- Mở **từng ảnh** và kiểm: chữ không đè, số liệu khớp `/state` (script in `history`, điểm cuối), cảnh báo/thông báo đúng.
- Ảnh cảnh báo riêng lẻ (thủy quái, oxy, khách giận): xem cách chụp trong [docs/proof/phase-4/ui/README.md](../../../docs/proof/phase-4/ui/README.md).
- Ghi vào bằng chứng: commit nền, lệnh, ảnh nào chụp từ live thật, ảnh nào từ snapshot dựng sẵn (nếu có). Không ghi "đạt" cho màn chưa thấy trong ảnh.
- Lỗi do bot (đi kẹt, hết giờ chờ) ≠ lỗi giao diện: chạy lại hoặc sửa bot, đừng sửa luật để bot qua.
