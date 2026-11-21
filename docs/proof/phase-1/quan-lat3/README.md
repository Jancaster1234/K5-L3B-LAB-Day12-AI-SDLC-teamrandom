# Bằng chứng — Quán lát 3 (khách theo lịch, chọn món, giữ chỗ, kiên nhẫn, bỏ đi, no_dish)

- **Code:** commit `e50cabd`, hàm `_spawn_customers`, `_tick_patience`, `_available`, `_release`, `_cookable_dishes`, `_init_customers` trong `chonoi/sim/quan.py` và kiểm scenario trong `chonoi/scenario.py` · **Người làm:** Vũ Quang Hải (`HaiVuQ`, xem `docs/ai-usage-log.md`)
- **Môi trường:** Python 3.10, Windows 10 · **Ngày:** 2026-11-21
- **Số liệu** (từ `game.contract.json`): `first_customer_tick` 120 · `customer_interval_s` 15 (900 tick) · `patience_s` 60 (3600 tick) · `left_reputation_delta` −0.5 · `reputation_initial` 3.0 · `reputation_min` 0 · `reputation_max` 5

Chạy lại từ thư mục gốc repo (trên Windows dùng `PYTHONPATH="tests;."`):

```bash
H="python3 -m chonoi.headless --mode quan --seed 1 --snapshot-every 1000"
P=docs/proof/phase-1/quan-lat3
$H --ticks 125 --scenario $P/01-spawn-reserve.scenario.json   --out $P/01-spawn-reserve.out.jsonl
$H --ticks 125 --scenario $P/02-no-dish.scenario.json         --out $P/02-no-dish.out.jsonl
$H --ticks 5   --scenario $P/03-patience-leave.scenario.json  --out $P/03-patience-leave.out.jsonl
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

## Kết quả

| # | Luật | Kịch bản | Kết quả quan sát | Đạt? |
|---|---|---|---|---|
| 1 | Khách đến đúng `first_customer_tick` (120), chọn món nấu được từ kho khả dụng, giữ chỗ `reserved` | `01-spawn-reserve`: kho `{"ca_loc": 1}`, chạy 125 tick | `customer_arrived {customer_id:"C1", table_id:"T1", dish_id:"ca_loc_nuong_trui"}` ở tick 120; tick 125: `C1` ở `waiting`, `reserved: {"ca_loc": 1}`, `patience_ticks_left: 3595` | ✅ |
| 2 | Có bàn trống nhưng không món nào trong menu đủ nguyên liệu khả dụng → `no_dish` | `02-no-dish`: kho `{"bong_sung": 1}` (gỏi bông súng cần 2), chạy 125 tick | `no_dish {}` ở tick 120; không có khách nào ngồi bàn (`customers: []`) | ✅ |
| 3 | Giảm kiên nhẫn −1/tick khi `waiting`; về 0 → `customer_left`, nhả giữ chỗ, trừ uy tín `left_reputation_delta` (−0.5), rời bàn | `03-patience-leave`: khách `C1` `waiting`, `patience_ticks_left: 3`, chạy 5 tick | `customer_left {customer_id:"C1", table_id:"T1"}` ở tick 3; tick 5: `customers: []`, bàn `T1` trống, `reputation: 2.5` | ✅ |
| 4 | Khách cũ hết kiên nhẫn ở bước 2 nhả bàn và giữ chỗ kịp cho khách mới đến ở bước 7 cùng tick (tick 120 + 3600 = 3720) | `PatienceAndLeave.test_khach_cu_bo_di_nha_ban_va_kho_kip_cho_khach_moi_cung_tick` | Tick 3720 phát `customer_left` (`C1`) rồi `customer_arrived` (`C2`) | ✅ |
| 5 | Kiểm mâu thuẫn mức luật trong scenario (`khách giữ chỗ quá kho` → mã thoát 2 trước khi ghi output) | `ScenarioValidationAndHeadless.test_khach_waiting_giu_cho_qua_kho_exit_2` | Mã thoát 2, file `--out` không được tạo | ✅ |
| 6 | Tất định: cùng seed → output giống từng byte; toàn bộ bộ test xanh | `tests/test_quan_lat3.py` + toàn bộ suite (`test-output.txt`) | `Ran 70 tests … OK` | ✅ |
