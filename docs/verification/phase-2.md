# Ma trận truy vết Phase 2 (Ticket-02, Test Contract v1.1)

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P2-01 — `contract_version:"1.1"`, số chuẩn, 6 nguyên liệu, 6 món theo dữ liệu | `chonoi/contract.py` kiểm manifest khi chạy; `test_smoke_p1` đọc số từ preset | [game.contract.json](../../game.contract.json), [Log 123 test](../proof/phase-2/test-output.txt) | Đạt |
| AC-P2-02 — Cá bơi/sinh | 8 test `FishSwim`/`FishSpawn` (tốc độ, phản xạ mép, đổi hướng bước 120, dải độ sâu, sinh tick 360, trần 12, tất định) | [tests/test_gather_v11.py](../../tests/test_gather_v11.py) | Đạt |
| AC-P2-03 — Cá Sấu, Máu, ngất | 9 test `Crocodile` + mã 2 cho `monsters[]` sai | [tests/test_gather_v11.py](../../tests/test_gather_v11.py) | Đạt |
| AC-P2-04 — 2 bếp / 4 bàn | Khách lấy bàn trống id nhỏ nhất; kín 4 bàn thì bỏ lượt | [tests/test_quan_lat3.py](../../tests/test_quan_lat3.py), [tests/test_day.py](../../tests/test_day.py) | Đạt |
| AC-P2-05 — `--mode day` công bố D1–D5, chốt Ngày khi Shop đóng | Smoke `day --days 1`; test chuỗi pha, kế hoạch, món theo kế hoạch | [Bằng chứng P2 #2](../proof/phase-2/README.md), [day1.jsonl](../proof/phase-2/day1.jsonl) | Đạt (22.200 tick trong 713 ms) |
| AC-P2-06 — Áp cấp oxygen/hp từ Ngày kế | 3 Ngày: mua cấp 1 cả hai, Ngày 2 `oxygen_max_ticks 2700`, `hp_max 4` | [Bằng chứng P2 #3](../proof/phase-2/README.md), [upgrades.jsonl](../proof/phase-2/upgrades.jsonl) | Đạt |
| AC-P2-07 — Pause dừng mọi timer (cả Shop) | `Pause.test_pause_dung_moi_timer`, `test_pause_o_mode_gather` | [tests/test_day.py](../../tests/test_day.py) | Đạt |
| AC-P2-08 — Menu, pause, HUD trên cửa sổ chơi | `python3 -m chonoi.live --mode day`: chạy thử qua HTTP cập bến → quán → Shop (mua, Enter đóng) → Ngày 2; Esc/P tạm dừng làm `sim_tick` đứng yên | [chonoi/web/index.html](../../chonoi/web/index.html), [chonoi/live.py](../../chonoi/live.py) | **Một phần**: chơi trọn vòng ngày, pause, Shop, HUD (Ngày, cần lấy/đã lấy, cảnh báo). Chưa có menu chính, DayIntro/EveningIntro/DayResult/Summary |
| AC-P2-09 — Smoke tích hợp có bằng chứng | `gather --inventory-out` → `quan --inventory`, so `stock` tick 0 | [integration-*](../proof/phase-2/README.md) | Đạt |
| AC-P2-10 — Regression P1 đạt với số chuẩn, test đổi có lý do | Toàn suite; lý do đổi test trong commit `3f4dd66`, `d7cdf6d` | [Log 123 test](../proof/phase-2/test-output.txt) | Đạt |
| AC-P2-11 — Mở rộng (nhóm 5 người ≥ 1) có test | `burn`: 4 test | [tests/test_ext_burn.py](../../tests/test_ext_burn.py) | Đạt |
| AC-P2-12 — Ghi chép làm rõ, nhật ký AI, retro | `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md` | — | Một phần tại tag `phase-2` (retro P2 chờ Quang Hải). *Cập nhật P4:* retro P2 đã có trong [retro.md](../retro.md) (Quang Hải, nhánh `haivq-p4-docs`) |

## Đánh giá ngắn
- Lõi Test Contract v1.1 đạt trên test tự động (127 test kể cả `burn`). Chưa đạt: menu/intro/Shop/HUD trên cửa sổ chơi.
- *Cập nhật sau (P4 / v1.1.0, không đổi kết quả tại tag `phase-2`):* cửa sổ chơi đã có pause, Shop đồ họa, HUD, 3 cảnh báo, **Menu, DayIntro, Buổi tối, Kết quả Ngày, Tổng kết** — ảnh chụp khi bot chơi trọn một Ngày trên live thật ([ảnh](../proof/phase-4/ui/README.md)). Nếu chấm lại sau P4 thì AC-P2-08 đạt.
- Tag `phase-2` gắn trễ so với mốc 1:55 (nhóm làm lại Phase 1 theo PRD-0 trước); ghi trung thực.
