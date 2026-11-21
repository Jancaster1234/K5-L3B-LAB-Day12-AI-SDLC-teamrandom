# Bằng chứng — Gather lát 2 (hái nút, mọc lại, bắt cá, giỏ + hold_full, cập bến → kho)

- **Code:** commit `cdf80eb` (gộp vào `main` qua PR #1), hàm `_harvest`, `_catch`, `_hold_add`, `_nearest` trong `chonoi/sim/gather.py` · **Người làm:** ndhai255 (dùng Claude Code, xem `docs/ai-usage-log.md`)
- **Môi trường:** Python 3.14.4, Linux · **Ngày:** 2026-11-21 · bằng chứng chạy trên `main` @ `8f91a5d`
- **Số liệu** (từ `game.contract.json`): `interact_radius` 2.0 · `surface_depth` 0.5 · `node_yield` 1 · `regrow_s` 20 → 1200 tick · `catch_radius` 2.0 · `catch_cooldown_s` 0.5 → 30 tick · `fish_yield` `ca_linh` 3 / `ca_loc` 1 · `hold_capacity` 12 · `dock_pos` [2, 0], `dock_radius` 3
- **Đọc tick:** input ở frame `tick k` được xử lý ở bước k → sự kiện mang `tick` k + 1 (giống lát 1).
> **Cập nhật theo PRD-0 (Integrator Jancaster1234, 2026-11-21):** lát 2 đã sửa theo PRD-0 (`docs/clarify.md` #1, #2, #8): `gather.amount`, `fish_caught.yield`, `hold_full {action, node_id|fish_id, required, free}`, giỏ thiếu chỗ **từ chối cả lượt**, `catch` hụt / thiếu chỗ không hồi chiêu. Mọi `*.out.jsonl` đã tạo lại; bảng dưới đã sửa theo output mới.

Chạy lại từ thư mục gốc repo (trên Windows dùng `PYTHONPATH="tests;."`):

```bash
H="python3 -m chonoi.headless --mode gather --seed 1 --snapshot-every 1000"
P=docs/proof/phase-1/gather-lat2
$H --ticks 5  --scenario $P/01-harvest.scenario.json --inputs $P/01-harvest.inputs.json --out $P/01-harvest.out.jsonl
$H --ticks 12 --scenario $P/02-regrow.scenario.json  --inputs $P/02-regrow.inputs.json  --out $P/02-regrow.out.jsonl
$H --ticks 3  --scenario $P/03a-underwater-interact.scenario.json --inputs $P/03a-underwater-interact.inputs.json --out $P/03a-underwater-interact.out.jsonl
$H --ticks 3  --scenario $P/03b-surface-catch.scenario.json --inputs $P/03b-surface-catch.inputs.json --out $P/03b-surface-catch.out.jsonl
$H --ticks 45 --scenario $P/04-catch-cooldown.scenario.json --inputs $P/04-catch-cooldown.inputs.json --out $P/04-catch-cooldown.out.jsonl
$H --ticks 45 --scenario $P/05-hold-full.scenario.json --inputs $P/05-hold-full.inputs.json --out $P/05-hold-full.out.jsonl
$H --ticks 90 --scenario $P/06-dock-inventory.scenario.json --inputs $P/06-dock-inventory.inputs.json --out $P/06-dock-inventory.out.jsonl --inventory-out $P/06-dock-inventory.inventory.json
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

## Kết quả

| # | Luật | Kịch bản | Kết quả quan sát | Đạt? |
|---|---|---|---|---|
| 1 | `interact` ở mặt nước hái nút `ready` gần nhất trong `interact_radius`; hòa khoảng cách → id nhỏ; đặt `regrow_ticks` 1200; giỏ LIFO | `01-harvest`: đứng [20, 0], giỏ `[ca_loc]`, N2 ở x 19 và N1 ở x 21 (cách đều), N3 ở x 40; bấm E tick 0 và tick 2 | tick 1 `gather {node_id:"N1", kind:"bong_sung", amount:1}` · tick 3 `gather {node_id:"N2", …}` · N3 ngoài bán kính không bị hái · tick 5: giỏ `[ca_loc, bong_sung, bong_dien_dien]`, N1 `regrow_ticks` 1196, N2 1198 | ✅ |
| 2 | Nút chưa mọc không hái được; đếm về 0 → `node_regrown`, hái lại được | `02-regrow`: N1 `regrow_ticks` 5, bấm E tick 0 và tick 10 | tick 0 không có `gather` · tick 5 `node_regrown {node_id:"N1"}` · tick 11 `gather` N1, `regrow_ticks` đặt lại 1200 | ✅ |
| 3 | Sai vùng: dưới nước không hái; mặt nước không bắt cá (không tính hồi chiêu) | `03a`: đứng d = 1 cạnh N1, bấm E · `03b`: đứng d = 0 cạnh F1 (d = 1), bấm Space | Không có sự kiện nào; giỏ rỗng, N1 vẫn `ready`, F1 vẫn còn, `catch_cd_ticks` 0 | ✅ |
| 4 | `catch` dưới nước bắt đàn gần nhất trong `catch_radius` (hòa → id nhỏ), thu `fish_yield`, đàn biến mất; hồi chiêu 30 tick chặn lần bấm tiếp | `04-catch-cooldown`: đứng [30, 10], F1 `ca_linh` và F2 `ca_loc` cùng cách 1; bấm Space tick 0, 15, 40 | tick 1 `fish_caught {fish_id:"F1", kind:"ca_linh", yield:3}` · tick 15 bị hồi chiêu chặn (không sự kiện) · tick 41 `fish_caught` F2 yield 1 · giỏ `[ca_linh×3, ca_loc]`, `fish` rỗng | ✅ |
| 5 | Giỏ thiếu chỗ cho cả `yield` → **từ chối cả lượt**: `hold_full`, đàn ở lại, **không** hồi chiêu (PRD-0, clarify #2) | `05-hold-full`: giỏ 10/12, F1 `ca_linh` (yield 3) gần nhất; bấm Space tick 0 và 40 | tick 1 `hold_full {action:"catch", fish_id:"F1", required:3, free:2}` · tick 41 lại `hold_full` y hệt (không bị hồi chiêu chặn) · giỏ vẫn 10/12, F1 và F2 vẫn còn, `catch_cd_ticks` 0 | ✅ |
| 6 | Cập bến xét TRƯỚC hái; `gather_end docked` ghi kho = giỏ | `06-dock-inventory`: hái N1 ở x 8, bơi về bến, bấm E ở x 4.4 ngay cạnh N2 `ready` | tick 1 `gather` N1 · tick 61 `gather_end {reason:"docked", inventory:{items:{bong_sung:1}}}`, N2 vẫn `ready` (không bị hái) · `06-dock-inventory.inventory.json` = `{"items":{"bong_sung":1}}` | ✅ |
| 7 | Tất định: cùng seed + input → giống từng byte | Chạy `04` và `06` mỗi kịch bản hai lần | `cmp` không khác; SHA-256 `04` bắt đầu `b44fab04996ecbb4`, `06` bắt đầu `9545f3a2cad9b0bc` | ✅ |
| 8 | Không phá phần có sẵn | Cả bộ test (smoke P1 + khung + lát 1 + 14 test lát 2 + quán + QA) | `Ran 92 tests … OK`, xem `test-output.txt` | ✅ |

Test tự động tương ứng: `tests/test_gather_lat2.py` (15 test: 8 hái, 7 bắt cá — gồm từ chối cả lượt và vung hụt không hồi chiêu).

## Kiểm tên sự kiện với `docs/contracts/` mục 4

| Sự kiện | Contract mục 4 | Code (`gather.py`) | Output thật | Khớp? |
|---|---|---|---|---|
| `gather` | `{node_id, kind, amount}` | `_harvest` | `{"node_id":"N1","kind":"bong_sung","amount":1}` (01, 02, 06) | ✅ |
| `fish_caught` | `{fish_id, kind, yield}` | `_catch` | `{"fish_id":"F1","kind":"ca_linh","yield":3}` (04) | ✅ |
| `hold_full` | `{action, node_id\|fish_id, required, free}` | `_hold_add` | `{"action":"catch","fish_id":"F1","required":3,"free":2}` (05) | ✅ |
| `node_regrown` (khung) | `{node_id}` ✅ | bước 1 của `step()` | `{"node_id":"N1"}` (02) | ✅ |
| `gather_end` (khung) | `{reason, inventory:{items}}` ✅ | `_finish` | `{"reason":"docked","inventory":{"items":{"bong_sung":1}}}` (06) | ✅ |

Thứ tự trong một bước khớp contract mục 2: bến → hái (`interact`) → bắt cá (`catch`); giỏ thiếu chỗ chỉ phát `hold_full` (không có `gather`/`fish_caught` cùng lượt).

## Chưa chắc / phụ thuộc PRD-0
- Tên trường và luật giỏ / hồi chiêu đã theo PRD-0 (PO đối chiếu, clarify #1, #2, #8).
- `hold_full` phát mỗi lần bấm khi giỏ thiếu chỗ (PRD-0 không nói chống lặp).
- Đàn bị bắt biến mất, không sinh lại ở Phase 1.
