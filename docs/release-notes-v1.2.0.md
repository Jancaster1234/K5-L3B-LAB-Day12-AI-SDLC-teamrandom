# Release Notes — v1.2.0 (teamrandom)

Bản hoàn thiện cửa sổ chơi của **Quán Ăn Chợ Nổi** sau v1.1.0. Luật chơi, Test Contract (vẫn **v1.3**) và output headless **không đổi**.

## 1. Điểm mới

### Màn phủ trên cửa sổ chơi (AC-P2-08)
* **Menu** khi vào game: chế độ chơi, bảng phím, công thức điểm.
* **DayIntro** mỗi Ngày: thực đơn tối nay, nguyên liệu cần lấy, trang bị (oxy, Máu).
* **Buổi tối** khi sang quán: kho mang về (kèm số hàng ươn), thực đơn, lưu ý cháy món / khách bỏ đi.
* **Kết quả Ngày** khi sang Shop: sao đánh giá, khách phục vụ / bỏ đi, thu trong ca, boa, uy tín, điểm, món đã bán.
* **Tổng kết** khi xong mọi Ngày: bảng từng Ngày và "Điểm cuối = tổng thu + 100 × uy tín".
* Màn phủ mở thì game tự tạm dừng (gửi cùng nút `pause` như `Esc`/`P`), `Enter` đi tiếp; `R` chơi lại.
* `http://…/?hc=1` mở thẳng chế độ tương phản cao.

### Sửa lỗi
* Cảnh báo oxy dùng emoji 🫧 (Unicode 14) hiện thành ô vuông trên Windows 10 → đổi sang ⚠️ / 💨.

### Kỹ thuật và harness AI
* `chonoi/live.py`: `/state` ở chế độ `day` có thêm `history` từng Ngày và `days_total` (chỉ cửa sổ chơi; headless không đổi) + test.
* Skill mới [`ui-screenshot-check`](../.agents/skills/ui-screenshot-check/SKILL.md): bot chơi trọn một Ngày, bấm phím thật qua Edge DevTools, chụp từng màn để đọc lại trước khi kết luận.
* `AGENTS.md` cập nhật: lệnh `day`/soak/bench, quy ước asset, kiểm giao diện bằng ảnh, quy trình phát hành.

## 2. Bằng chứng
* [Ảnh lượt chơi thật 1 Ngày](proof/phase-4/ui/README.md): Menu, DayIntro, tương phản cao (phím `H` thật), Buổi tối, Kết quả Ngày, **Shop thật** (`buy_failed` → "Không đủ tiền"), Tổng kết `386 = 86 + 100 × 3`; ảnh 3 cảnh báo.
* [Clone sạch](proof/phase-4/qa/clean-clone.txt) trên **Linux** (Ubuntu / WSL2) và Windows; suite chạy lại tại mọi tag `phase-1…4`, `v1.1.0`.
* 151 test OK.

## 3. Cách chạy

```bash
git clone https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom.git
cd K5-L3B-LAB-Day12-AI-SDLC-teamrandom
python3 -m chonoi.live --mode day
```
Mở địa chỉ in ra → Menu → `Enter`. Windows: `powershell -ExecutionPolicy Bypass -File .\lab.ps1 setup` rồi `.\.venv\Scripts\python.exe -m chonoi.live --mode day`; cổng 8000 bị chặn thì thêm `--port 8765`.

## 4. Giới hạn đã biết
* Chưa thử macOS. Shop chỉ thao tác bàn phím.
* Mở rộng P3 (dòng lũ, khách đặt trước) chưa làm; mở rộng P2 chỉ có `burn`.
* Cảnh lặn vector, cảnh quán / Shop pixel art; log sự kiện góc phải dưới có thể đè ở cửa sổ nhỏ.
* `docs/clarify.md` #12–#13 (giả định bench) chờ PO đối chiếu PRD-0.
