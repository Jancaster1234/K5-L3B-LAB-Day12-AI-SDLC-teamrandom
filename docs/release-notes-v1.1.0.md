# Release Notes — v1.1.0 (teamrandom)

Bản cập nhật **đồ họa** của **Quán Ăn Chợ Nổi** sau v1.0.0. Luật chơi, Test Contract (vẫn **v1.3**) và output headless **không đổi**: mọi thay đổi chỉ nằm ở client trình duyệt (`chonoi/web/`) và một route phục vụ ảnh trong `chonoi/live.py`.

## 1. Điểm mới

### Cảnh lặn
* Sprite **Kenney Fish Pack** (CC0): mỗi loại cá có hình riêng (cá linh xanh nhỏ, cá lóc xanh lá, cá kèo thân dài), cá lật theo hướng bơi.
* Đáy cát, rong đung đưa, đá, nền xa mờ, tia nắng, mặt nước gợn sóng, bọt khí từ thợ lặn.
* **Út Sen**: đội nón lá khi ở mặt nước; dưới nước bơi ngang với bình oxy, kính lặn, chân vịt.
* **Cá Sấu** được vẽ (trước đây client chỉ hiện cảnh báo): há mõm, mắt vàng khi đuổi.
* Hoa điên điển / bông súng / kèo nèo trên lá nổi, mờ khi đang mọc lại.

### Cảnh quán
* Tilesheet **Kenney Roguelike Indoors / Characters** (CC0, pixel art): bếp gang, bàn ghế, quầy bếp, cây cảnh, thảm; sàn gỗ và góc bếp lát gạch.
* Bếp có lửa khi nấu, viền xanh + "Chín! (E)" khi xong.
* Khách ngồi bàn với bong bóng gọi món **tên tiếng Việt**, trạng thái đơn ("thiếu đồ!" màu đỏ), thanh kiên nhẫn xanh → vàng → đỏ; tô món bốc khói khi khách ăn hoặc khi đang bưng.

### Shop
* "Tiệm đồ lặn chợ nổi": biển hiệu, chủ tiệm sau quầy, kệ trưng bình oxy và áo phao.
* Thẻ nâng cấp: cấp hiện có, hiệu quả hiện tại và cấp kế (đọc từ `tuning.shop.upgrades`), giá, viền xanh khi đủ tiền, "ĐÃ TỐI ĐA", "có hiệu lực từ Ngày kế".
* Thông báo khi mua được hoặc thất bại (`bought` / `buy_failed`), ví tiền và thanh đếm ngược tự đóng.

### Kỹ thuật
* `chonoi/live.py` (file khung, sửa có lý do): thêm `GET /assets/<file>` phục vụ ảnh trong `chonoi/web/assets/`; chỉ đuôi png/svg/txt, chặn thoát thư mục. Test mới trong `tests/test_live.py` (150 test).
* Ảnh chưa tải được thì client tự vẽ hình khối như v1.0.0.

## 2. Cách chạy

```bash
git clone https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom.git
cd K5-L3B-LAB-Day12-AI-SDLC-teamrandom
python3 -m chonoi.live --mode day
```
Python 3.10+, chỉ thư viện chuẩn. Windows: `powershell -ExecutionPolicy Bypass -File .\lab.ps1 setup` rồi `.\.venv\Scripts\python.exe -m chonoi.live --mode day`. Nếu cổng 8000 bị chặn, thêm `--port 8765`.

Điều khiển: `WASD`/mũi tên, `E` tương tác, `Space` bắt cá, `Esc`/`P` tạm dừng, Shop `1`/`2`/`Enter`, `H` tương phản cao, `R` chơi lại.

## 3. Asset và giấy phép
* Kenney Fish Pack 2.0, Roguelike Indoors, Roguelike Characters — www.kenney.nl, **CC0 1.0**. File license gốc đi kèm trong `chonoi/web/assets/`. Chi tiết: `CREDITS.md`.

## 4. Giới hạn đã biết
* Hai phong cách khác nhau: cảnh lặn vector cartoon, cảnh quán / Shop pixel art 16px.
* Log sự kiện góc phải dưới có thể đè lên bàn T2/T4 và thanh đếm ngược Shop ở cửa sổ nhỏ.
* Vẫn chưa có Menu chính, DayIntro / DayResult / Summary; Shop chỉ thao tác bàn phím.
* Màn Shop được kiểm bằng snapshot dựng sẵn (server giả) và chụp trình duyệt headless; cảnh lặn và quán kiểm trên `chonoi.live` thật.
* Mở rộng P3 (dòng lũ, khách đặt trước) vẫn chưa làm.
