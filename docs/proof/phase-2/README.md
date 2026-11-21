# Bằng chứng Phase 2 — Test Contract v1.1

- **Code:** nhánh tích hợp v1.1 (commit `3f4dd66` (số chuẩn), `39dd6e9` (cá + Cá Sấu), `d7cdf6d` (day, Shop, pause)) · **Người làm:** Jancaster1234 (Integrator, dùng Claude Code)
- **Môi trường:** Python 3.12, Windows 10 · **Ngày:** 2026-11-21

Chạy lại từ gốc repo (Windows: `PYTHONPATH="tests;."`):

```bash
P=docs/proof/phase-2
# 1. Smoke tích hợp hai tiến trình (Ticket-02 mục 5, phút 20)
python3 -m chonoi.headless --mode gather --seed 42 --scenario $P/integration-dock.json --inputs $P/integration-dock-inputs.json --ticks 1 --out $P/integration-gather.jsonl --inventory-out $P/integration-catch.json
python3 -m chonoi.headless --mode quan --seed 42 --inventory $P/integration-catch.json --ticks 0 --out $P/integration-quan.jsonl
# 2. Smoke day --days 1
python3 -m chonoi.headless --mode day --seed 42 --days 1 --ticks 30000 --snapshot-every 600 --out $P/day1.jsonl
# 3. Nhiều Ngày: mua nâng cấp, áp cấp từ Ngày kế
python3 -m chonoi.headless --mode day --seed 42 --days 3 --ticks 9 --snapshot-every 1 --scenario $P/upgrades.scenario.json --inputs $P/upgrades.inputs.json --out $P/upgrades.jsonl
# 4. Regression P1 + P2
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

| # | Kiểm | Kết quả thật | Đạt? |
|---|---|---|---|
| 1 | Smoke tích hợp: quán tick 0 nhận đúng file kho | `integration-catch.json` = `{"items":{"bong_sung":2,"ca_loc":1}}`; snapshot quán tick 0 `stock` = `{"bong_sung":2,"ca_loc":1}` | ✅ |
| 2 | `day --days 1`: đủ chuỗi pha, chốt Ngày khi Shop đóng | `day_start`/`day_plan`/`phase_start(gather)` ở tick 0 → `gather_end` + `phase_start(quan)` tick 10800 → `quan_end` + `phase_start(shop)` tick 21600 → `shop_end(time)` tick 22200; end `reason:"days_complete"`, `days_completed:1`. Chạy 713 ms (yêu cầu ≤ 20 s) | ✅ |
| 3 | Shop + nâng cấp từ Ngày kế | Ngày 1: `bought oxygen 1 (200)`, `bought hp 1 (250)`; Ngày 2: `buy_failed {action:"oxygen", reason:"funds"}`. Snapshot dựng Ngày 2 (tick 5): `active_upgrades {hp:1, oxygen:1}`, `oxygen_max_ticks 2700`, `hp_max 4`; Ngày 1 (tick 0): 1800 / 3 | ✅ |
| 4 | Regression P1 + P2 trên số chuẩn | `Ran 123 tests … OK` (`test-output.txt`): P1 (lát 1–4, quán PRD-0) + `test_gather_v11` (cá bơi/sinh, Cá Sấu) + `test_day` (day, Shop, pause, mã 2, tất định) | ✅ |

Test cũ đổi vì luật mới (lý do trong từng commit): số đàn ban đầu 6 → 8, 1 bàn → 4 bàn, `day`/`attack` từ "bị từ chối" thành hợp lệ ở v1.1.

## Chưa làm / giới hạn
- Menu chính, DayIntro/EveningIntro/DayResult/Summary và HUD đầy đủ trên cửa sổ chơi: chưa (đang làm sau phần Test Contract).
- Mở rộng (nhóm 5 người cần ≥ 1): chưa — dự kiến `burn`.
