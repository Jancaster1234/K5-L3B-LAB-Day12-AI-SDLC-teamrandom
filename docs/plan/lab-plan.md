# Kế hoạch phần còn lại của lab (Phase 2 → 4)

> Integrator: Jancaster1234 · lập 2026-11-21 sau khi có đủ Ticket-02/03/04. Thay cho chia theo từng phase.
> Nguyên tắc: Integrator (+ AI) làm phần lớn và mọi phần chạm luật/Test Contract; ba bạn nhận việc **nhỏ, độc lập**, mỗi việc một commit riêng.

## Thứ tự ưu tiên (theo điểm chấm)
Test ẩn (25) chạy lại cả phase trước, nên làm **lõi Test Contract trước**, giao diện sau.

| # | Việc | Phase | Người | Phụ thuộc |
|---|---|---|---|---|
| 1 | Tuning/manifest v1.1: 6 nguyên liệu, 6 món, N5/N6, B2, T2–T4, 8 đàn, monsters, day_plan, shop; kiểm `contract.py`, `inventory.py`, `scenario.py` | P2 | Phúc | — |
| 2 | Cá bơi + sinh theo lịch (`fish_*`), `fish_spawned` | P2 | Phúc | 1 |
| 3 | Cá Sấu: patrol/chase/hit/recoil, bất tử, `monster_hit`, `faint(cause:"monster")` | P2 | Phúc | 1 |
| 4 | Quán 2 bếp/4 bàn/6 món (luật đã tổng quát, chủ yếu dữ liệu + test) | P2 | Phúc | 1 |
| 5 | `--mode day`: DayIntro→gather→quan→Shop, `--days`, kế hoạch D1–D5, Shop (`oxygen`, `hp`, `buy_failed`, `shop_done`, 600 tick), pause, snapshot/event v1.1, `days_completed` | P2 | Phúc | 1–4 |
| 6 | Mở rộng bắt buộc (nhóm 5 người ≥ 1 mục): **Cháy món (`burn`)** | P2 | Phúc | 4 |
| 7 | v1.2 độ tươi: kho cá thể `{id,kind,fresh}`, hao tươi, `spoiled`, giữ theo id, giá theo tươi | P3 | Phúc | 5 |
| 8 | `soak_cmd` (10 Ngày, bot tất định) + contract v1.3 | P4 | Phúc | 5, 7 |
| 9 | `bench_cmd` (cảnh lặn 1280×720, `bench.json`) | P4 | **Đức Hải** | chỉ cần `GatherSim` |
| 10 | HUD/menu/pause, 3 cảnh báo + chế độ tương phản cao | P2/P4 | Phúc | 5 |
| 11 | Ma trận AC `docs/verification/phase-2/3/4.md`, `clarify.md`, `retro.md` | P2–P4 | **Quang Hải** | — (docs) |
| 12 | README (chạy ≤ 3 lệnh, điều khiển, điểm, test, headless, bench, Sáng tạo của nhóm), CHANGELOG theo phase, CREDITS/LICENSE, nháp release notes, kịch bản demo | P1–P4 | **Hiệu** | — (docs) |
| 13 | Tag `phase-2/3/4`, Release `v1.0.0` + bản đóng gói | P2–P4 | Phúc | tất cả |
| 14 | `docs/members/<handle>.md`, dòng của mình trong `ai-usage-log.md` | — | **mỗi người** | — |

## Quy tắc tránh conflict
- Chỉ Integrator sửa `chonoi/`, `game.contract.json`, `tests/` (trừ file test riêng của việc #9).
- Đức Hải chỉ tạo file mới: `chonoi/bench.py`, `tests/test_bench.py`, `docs/proof/phase-4/bench/`.
- Quang Hải chỉ sửa `docs/verification/`, `docs/clarify.md`, `docs/retro.md`, `docs/plan/`.
- Hiệu chỉ sửa `README.md`, `CHANGELOG.md`, `CREDITS.md`, `docs/release-notes-v1.0.0.md`, `docs/demo.md`.
- Mỗi người làm trên nhánh riêng, push nhánh rồi báo Integrator gộp.

## Rủi ro
- Hạn giờ: ưu tiên #1–#5 (test ẩn P2) → #7 → #8/#9 → UI. Việc chưa xong ghi trung thực trong verification.
- Viết lại lớn (v1.1, v1.2) dễ hỏng regression P1: mỗi bước chạy toàn bộ test, test đổi phải ghi lý do trong commit.
