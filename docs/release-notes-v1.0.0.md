# Release Notes — v1.0.0 (teamrandom)

Phiên bản phát hành chính thức **v1.0.0** của game **Quán Ăn Chợ Nổi**, xây dựng theo quy trình AI SDLC qua 4 phase tại lab Day 12.

---

## 1. Điểm mới theo CHANGELOG.md

### Phase 3 — Test Contract v1.2: Độ tươi & Kho cá thể
* **Breaking Change: Chuyển đổi kho đếm sang kho cá thể**:
  - File kho, giỏ lặn (`gather.hold`), kho quán (`quan.stock`), và bàn giao ca (`gather_end.inventory`) chuyển sang định dạng cá thể: `{"items": [{"id": ..., "kind": ..., "fresh": ...}]}`. Cấu trúc kho đếm cũ bị từ chối với mã lỗi 2 (xem chi tiết tại [ADR-0001](file:///d:/AI20K/Lab12/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/docs/adr/0001-kho-ca-the-v12.md)).
  - Các trường liên quan (`reserved`, `cook_started.items`, `monster_hit.lost`, `faint.lost`) đồng bộ sử dụng danh sách cá thể.
  - Giá món ăn chốt lúc bắt đầu nấu phụ thuộc vào độ tươi: `base_price = floor(giá niêm yết × trung bình fresh / 100)`.
* **Cơ chế độ tươi (`chonoi/fresh.py`)**:
  - Tỷ lệ giảm độ tươi: hao 0.5/s khi ở trong giỏ lặn của người chơi, hao 0.25/s khi lưu trong kho quán.
  - Ngưỡng ươn/hỏng: Nguyên liệu giảm xuống dưới 30 sẽ bị ươn, phát sự kiện `spoiled` và không thể dùng để nấu ăn.
  - Giữ chỗ thông minh: Tự động ưu tiên giữ chỗ các nguyên liệu tươi nhất (fresh cao nhất) cho khách; khi nguyên liệu đang giữ bị ươn sẽ tự động thử giữ lại nguyên liệu tươi khác.
  - HUD giao diện: Hiển thị thanh độ tươi trực quan cho từng nguyên liệu trong giỏ và kho.

### Phase 2 — Test Contract v1.1: Quy mô & Chế độ chơi đầy đủ
* **Số chuẩn Ticket-02**:
  - 6 loại nguyên liệu: `ca_loc`, `ca_tre`, `tom_cang`, `ca_keo`, `bong_dien_dien`, `bong_sung`.
  - 6 món ăn đặc sản miền Tây: `ca_loc_nuong_trui`, `canh_chua_ca_loc`, `ca_kho_to`, `tom_nuong_muoi_ot`, `ca_keo_kho_rau_dang`, `goi_bong_sung`.
  - Thiết bị quán: 2 bếp (`B1`, `B2`) và 4 bàn ăn (`T1`, `T2`, `T3`, `T4`).
  - Hệ sinh thái: 8 đàn cá bơi lội và tái sinh theo lịch trình.
* **Quái vật Cá Sấu Năm Chèo**:
  - Xuất hiện trong ca lặn với cơ chế tuần tra (patrol), truy đuổi người chơi (chase), tấn công gây mất máu (`monster_hit`), và trạng thái hồi giật (recoil). Cá Sấu bất tử và tạo thử thách sinh tồn cao.
* **Chế độ chơi cả ngày (`--mode day`)**:
  - Vòng lặp trọn vẹn 5 ngày chơi (D1–D5), tự động chuyển đổi giữa ca lặn ban ngày và ca quán buổi tối.
  - Cửa hàng Shop giữa ngày: Nâng cấp bình oxy (tăng dung lượng và giảm tốc độ tiêu hao) và thanh máu (tối đa hp). Hỗ trợ tùy chọn `--days 1..5`.
* **Cơ chế Pause**:
  - Hỗ trợ tạm dừng và tiếp tục trên cả 3 chế độ (`gather`, `quan`, `day`), dừng toàn bộ bộ đếm thời gian (ticks).
* **Mở rộng `burn`**:
  - Món chín trên bếp quá 20 giây (1200 tick) không lấy sẽ bị cháy (`dish_burnt`).

### Phase 1 — PRD-0: Cơ chế mô phỏng cốt lõi
* **Ca lặn (`sim/gather`)**:
  - Di chuyển, bơi lội, tiêu hao và hồi phục bình oxy, cơ chế ngạt thở (`choke`), kiệt sức ngất xỉu (`faint`) và rơi vật phẩm.
  - Bắt cá trong vùng tương tác, hái bông súng/điên điển, hồi sinh cây sau thời gian quy định, cơ chế giỏ đầy (`hold_full`).
* **Ca quán (`sim/quan`)**:
  - Khách đến quán theo khung giờ, chiếm bàn, cơ chế kiên nhẫn và tự rời đi khi hết thời gian chờ (`customer_left`).
  - Tự động giữ chỗ nguyên liệu theo công thức món ăn (`reserved` / `unfulfillable`).
  - Tương tác bếp nấu (`cook_started`, `dish_ready`), bưng bê và phục vụ bàn (`served`).
  - Khách ăn xong trả tiền (`paid`), thưởng tiền boa (`tip`) khi được phục vụ lúc kiên nhẫn $\ge 50\%$, cộng điểm uy tín (`reputation` $+0.2$).
  - Thuật toán xử lý va chạm và ưu tiên tương tác (tie-break theo khoảng cách Euclid gần nhất, ưu tiên bếp trước bàn, id nhỏ hơn).

---

## 2. Cách chạy game

### Chạy từ clone sạch (tối đa 3 lệnh trên macOS/Linux)
```bash
git clone https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom.git
cd K5-L3B-LAB-Day12-AI-SDLC-teamrandom
python3 -m chonoi.live --mode gather
```
* **Yêu cầu môi trường:** Python 3.10+, không cần cài thêm (chỉ dùng thư viện chuẩn Python).
* **Các chế độ live khác:**
  - Chơi ca quán: `python3 -m chonoi.live --mode quan`
  - Chơi cả ngày (D1–D5): `python3 -m chonoi.live --mode day`

### Điều khiển
* **Di chuyển:** `WASD` hoặc cụm phím mũi tên.
* **Tương tác:** `E` (hái cây, bỏ đồ vào bếp nấu, lấy món ăn chín, dọn lên bàn khách).
* **Bắt cá:** `Space` (khi bơi cạnh cá).
* **Tạm dừng / Tiếp tục:** `Esc` hoặc `P`.

### Công thức tính điểm
$$\text{điểm} = \text{earned} + 100 \times \lfloor\text{reputation}\rfloor$$
(hoặc: `điểm = earned + 100 × floor(reputation)`).

### Lệnh chạy kiểm thử (Unit tests)
```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

### Chạy mô phỏng Headless (Tất định)
```bash
python3 -m chonoi.headless --mode gather|quan|day --seed 1 --ticks 600 --out out.jsonl
```
*(Thêm `--days 1..5` khi chạy `--mode day`)*.

### Chạy Benchmark hiệu năng
```bash
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json
```

### Chạy Soak test kiểm tra ổn định dài hạn
```bash
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
```

---

## 3. Mở rộng đã làm
* **`burn` (Món cháy):** Khi món ăn nấu chín trên bếp để quá 20 giây (1200 tick) mà người chơi không đến lấy thì sẽ phát sinh sự kiện `dish_burnt`, món ăn bị cháy hỏng và bếp trở về trạng thái rảnh `idle`. Đơn hàng của khách nếu kho còn nguyên liệu tươi sẽ tự động được giữ chỗ lại (`reserved`), nếu thiếu sẽ chuyển sang `unfulfillable` trong khi khách vẫn tiếp tục chờ.
  * Bộ test xác thực: `tests/test_ext_burn.py`.

---

## 4. Sáng tạo của nhóm
* **Chưa có:** Nhóm tập trung tối đa nguồn lực vào việc hoàn thiện chính xác 100% hợp đồng kỹ thuật (PRD-0, Test Contract v1.0, v1.1, v1.2), bảo đảm tính tất định và tối ưu hiệu năng/độ ổn định qua toàn bộ các Phase.

---

## 5. Giới hạn đã biết (Known Limitations)
* **Giao diện đồ họa Live:** Cửa sổ chơi trên trình duyệt (`chonoi/live.py`) chạy trực tiếp vào gameplay mô phỏng Canvas 2D, chưa có màn hình Menu chính (Start Menu), DayIntro / EveningIntro / DayResult / Summary. Shop có màn hình dùng bàn phím (`1`/`2` mua, `Enter` đóng), chưa có thao tác chuột. Đồ họa là hình khối 2D tạm.
* **Benchmark:** `bench_cmd` vẽ phần mềm vào framebuffer 1280×720 trong tiến trình, không mở cửa sổ thật; số FPS chỉ dùng để báo cáo.
* **Mở rộng P3** (dòng lũ, khách đặt trước) và các mở rộng P2 khác ngoài `burn`: không làm.
* **Mở rộng Phase 3:** Nhóm không làm phần mở rộng tùy chọn của Phase 3 nhằm bảo đảm tính tương thích tuyệt đối của cơ chế chuyển đổi kho cá thể và độ tươi theo Test Contract v1.2.
