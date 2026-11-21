# Bằng chứng Phase 3 — Test Contract v1.2 (độ tươi, kho cá thể)

- **Code:** commit `369737b` (v1.2) · **Quyết định:** [ADR-0001](../../adr/0001-kho-ca-the-v12.md) · **Người làm:** Jancaster1234 (Claude Code)
- **Chạy lại** từ gốc repo, với `H="python3 -m chonoi.headless --seed 1 --snapshot-every 1000"` và `P=docs/proof/phase-3`:

```bash
$H --mode gather --ticks 1 --scenario $P/01-spoil.scenario.json --out $P/01-spoil.out.jsonl
$H --mode gather --ticks 1 --scenario $P/02-handoff.scenario.json --inputs $P/02-handoff.inputs.json --out $P/02-handoff-gather.jsonl --inventory-out $P/02-handoff-kho.json
$H --mode quan --ticks 0 --inventory $P/02-handoff-kho.json --out $P/02-handoff-quan.jsonl
$H --mode quan --ticks 0 --inventory $P/03-counting-kho.json --out $P/03-x.jsonl   # mong đợi mã 2
python3 -m chonoi.headless --seed 1 --snapshot-every 1 --mode quan --ticks 2 --scenario $P/04-quan-fresh.scenario.json --inputs $P/04-quan-fresh.inputs.json --out $P/04-quan-fresh.out.jsonl
python3 -m chonoi.headless --mode day --seed 42 --days 2 --ticks 50000 --snapshot-every 1000 --out $P/05-day2.jsonl
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

| # | Kiểm | Kết quả thật | Đạt? |
|---|---|---|---|
| 1 | Ví dụ ngưỡng của Ticket-03: cá thể fresh 30, gather 1 bước | `01-spoil.out.jsonl`: `{"tick":1,"name":"spoiled","data":{"item_id":"I1","kind":"ca_linh","location":"hold"}}`, trùng ví dụ ticket | ✅ |
| 2 | Smoke bàn giao file: fresh 100, cập bến frame 0 → quán `--inventory --ticks 0` | `02-handoff-kho.json` = `{"items":[{"id":"I1","kind":"ca_linh","fresh":99.99166666666666}]}` (sau 1 lần hao ở giỏ); snapshot quán tick 0 `stock` = `I1, ca_linh, 99.992` (JSONL làm tròn 3 chữ số, trong dung sai ±0.01) | ✅ |
| 3 | v1.2 từ chối kho đếm | `03-counting-kho.json` `{"items":{"ca_loc":1}}` → mã 2 (`03-counting-stderr.txt`) | ✅ |
| 4 | Giữ theo id, giữ lại khi ươn, giá theo tươi | `04-quan-fresh`: tick 1 `spoiled I5` (kho) → C2 nhả I5, giữ lại `I6`; `cook_started` C1 tiêu `I4, I1, I2, I3` (kind rồi id), `base_price` 77 = floor(120 × 64.996 / 100) | ✅ |
| 5 | day 2 Ngày trên v1.2 | `05-day2.jsonl`: `reason:"days_complete"`, `days_completed:2`, 44.400 tick trong 1.181 ms | ✅ |
| 6 | Regression P1–P3 | `Ran 140 tests … OK` (`test-output.txt`), gồm `tests/test_fresh.py` (13 test) | ✅ |

## Chưa làm
- Mở rộng P3 (dòng lũ `current`, khách đặt trước `reservations`): chưa.
