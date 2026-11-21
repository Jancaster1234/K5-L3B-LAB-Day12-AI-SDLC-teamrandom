# Bằng chứng — Gather lát 1 (oxy, dive/surface, ngạt, Máu, ngất)

- **Code:** commit `d150448`, hàm `_update_oxygen` trong `chonoi/sim/gather.py` · **Người làm:** Jancaster1234 (dùng Claude Code, xem `docs/ai-usage-log.md`)
- **Môi trường:** Python 3.12.0, Windows 10 · **Ngày:** 2026-11-21
- **Số liệu** (từ `game.contract.json`): `oxygen_max_s` 30 → 1800 tick · `oxygen_refill_per_tick` 6 · `choke_interval_ticks` 60 · `hp_max` 3 · `surface_depth` 0.5

Chạy lại từ thư mục gốc repo (trên Windows dùng `PYTHONPATH="tests;."`):

```bash
H="python3 -m chonoi.headless --mode gather --seed 1 --snapshot-every 1000"
P=docs/proof/phase-1/gather-lat1
$H --ticks 5   --scenario $P/01-oxy.scenario.json   --out $P/01-oxy.out.jsonl
$H --ticks 120 --scenario $P/02-choke.scenario.json --out $P/02-choke.out.jsonl
$H --ticks 10  --scenario $P/03-faint.scenario.json --out $P/03-faint.out.jsonl --inventory-out $P/03-faint.inventory.json
$H --ticks 200 --scenario $P/04-dive-surface.scenario.json --inputs $P/04-dive-surface.inputs.json --out $P/04-dive-surface.out.jsonl
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

## Kết quả

| # | Luật | Kịch bản | Kết quả quan sát | Đạt? |
|---|---|---|---|---|
| 1 | Dưới nước oxy −1/tick; `oxygen_empty` khi oxy từ dương về 0, đúng một lần | `01-oxy`: d = 10, oxy 3, chạy 5 tick | `oxygen_empty {oxygen_ticks:0}` ở tick 3, không lặp lại; tick 5: oxy 0, `zero_oxy_ticks` 3 | ✅ |
| 2 | Oxy = 0 dưới nước → đủ 60 tick thì `choke` (−1 Máu), đếm lại | `02-choke`: d = 10, oxy 1, chạy 120 tick | `oxygen_empty` tick 1 · `choke {hp:2}` tick 60 · `choke {hp:1}` tick 120 | ✅ (PRD-0 xác nhận, clarify #6) |
| 3 | Máu 0 → `faint`, mất giỏ, `gather_end` `fainted`, kho rỗng | `03-faint`: Máu 1, oxy 0, `zero_oxy_ticks` 59, giỏ `[ca_loc, bong_sung]` | tick 1: `choke {hp:0}` → `faint {cause:"choke", lost:["bong_sung","ca_loc"], hp:0}` (LIFO) → `gather_end {reason:"fainted", inventory:{items:{}}}`; dòng end `reason: fainted`; `03-faint.inventory.json` = `{"items":{}}` | ✅ |
| 4 | `dive` / `surface` khi đổi vùng (so d đầu và cuối bước); mặt nước hồi +6/tick, kẹp ở tối đa | `04-dive-surface`: bơi xuống tick 0, lên tick 60, dừng tick 150 | `dive {pos:[50, 0.567]}` tick 11 · `surface {pos:[50, 0.433]}` tick 116 · tick 200: oxy 1800 (đã kẹp), `zero_oxy_ticks` 0 | ✅ |
| 5 | Tất định: cùng seed + input → giống từng byte | Chạy `04-dive-surface` hai lần | `cmp` không khác; SHA-256 cả hai bắt đầu `98bbfa88fd8b2f9e` | ✅ |
| 6 | Không phá phần có sẵn | Cả bộ test (smoke P1 + khung + 12 test lát 1) | `Ran 44 tests … OK`, xem `test-output.txt` | ✅ |

Test tự động tương ứng: `tests/test_gather_lat1.py` (12 test), ngoài ra còn kiểm ngất xét trước cập bến (clarify #7) và nổi lên thì reset đếm ngạt.

## Chưa chắc / phụ thuộc PRD-0
- **Clarify #6, #7:** PO đối chiếu PRD-0 mục F: KHỚP (bước oxy vừa về 0 tính là bước ngạt đầu; ngất thắng cập bến).
- **Tên trường `data`:** đã sửa theo PRD-0 mục E (clarify #1): `oxygen_empty {oxygen_ticks:0}`, `faint {cause, lost, hp}`; `dive`/`surface`/`choke` khớp sẵn. Output 01–03 tạo lại sau khi sửa.
- **Chưa làm:** `invuln_ticks` có trong snapshot nhưng lát 1 không dùng (chưa thấy luật nào cho Phase 1).
- **Môi trường:** máy làm không có `python3` thật (Windows chỉ có lối tắt Store); `python3` lúc chạy là bản sao `python.exe` 3.12.0 trong một venv tạm.
