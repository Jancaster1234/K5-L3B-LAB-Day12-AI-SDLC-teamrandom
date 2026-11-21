# Kế hoạch Phase 1 (≤ 1 trang)

- Mục tiêu: hoàn thành luật `gather` (lát 1–2) và `quan` (lát 3–4) theo PRD-0, 5 luồng chạy song song, gắn tag `phase-1` trước 1:00.

## 5 luồng song song (mỗi luồng sở hữu hàm riêng → không chờ, ít conflict)

| # | Luồng | File / hàm sở hữu | Tự test bằng (không cần luồng khác) |
|---|---|---|---|
| 1 | Gather lát 1: dive/surface, oxy, oxygen_empty, choke, Máu, faint (giỏ rỗng) | `gather.py`: `_update_oxygen(prev_pos, events)` gọi sau `_move`, trả `True` nếu ngất | scenario `player.oxygen_ticks/hp/zero_oxy_ticks` |
| 2 | Gather lát 2: hái nút ở mặt nước, regrow, bắt cá (cooldown, dưới nước), hold_full | `gather.py`: `_harvest(events)`, `_catch(events)` | scenario `nodes`, `fish`, `hold`, `player.pos` |
| 3 | Quan lát 3: khách theo lịch, chọn món nấu được, giữ chỗ, kiên nhẫn, customer_left, no_dish | `quan.py`: `_spawn_customers(events)`, `_tick_patience(events)`, `_available()`, `_release(customer)` | scenario `stock`, `time_left_ticks`, `customers`, `random_customers` (`tests/test_quan_lat3.py`) |
| 4 | Quan lát 4: interact bếp/bàn (cook_started, dish_ready, dish_picked, served), ăn xong, paid, boa, uy tín, quan_end | `quan.py`: `_tick_stoves`, `_tick_eating`, `_interact(events)` | scenario `customers[]` dựng sẵn, `stoves`, `hand`, `stock` |
| 5 | QA + harness + UI: test tích hợp gather → kho → quan, tất định cùng seed, verification/proof, 2 skill `.agents/skills/`, `AGENTS.md`, `ai-usage-log`, HUD `chonoi/web/` | `tests/test_*_integration.py`, `docs/`, `.agents/`, `chonoi/web/` | headless + file kho |

## Mốc
| Thời gian | Việc |
|---|---|
| 0:00–0:10 | Fork/collaborator, mỗi người điền dòng của mình trong `TEAM.md` (commit riêng). **Chốt 2 điểm nối** (Integrator ghi vào `docs/contracts/`): (a) tên hàm + thứ tự gọi trong `step()` của mỗi sim, theo PRD-0; (b) schema khách (`id, table_id, dish, state, patience_ticks, reserved, eat_ticks…`) dùng chung cho lát 3 và 4. |
| 0:10–0:45 | 5 luồng làm song song, mỗi lát tự viết test của mình. Luồng 5 làm skill #1 trước để mọi người dùng. |
| 0:45–0:55 | Gộp theo thứ tự lát 1 → 2 → 3 → 4; luồng 5 chạy toàn bộ test + headless, điền `docs/verification/phase-1.md`. |
| 0:55 | Integrator gắn tag `phase-1`. |

## Rủi ro
- Hai người cùng sửa `step()` → conflict: chỉ thêm **một dòng gọi hàm** vào `step()`, logic nằm trong hàm của mình; thứ tự gọi đã chốt lúc 0:10.
- Lát 3/4 hiểu khác nhau về khách → schema khách chốt trước, đổi thì báo cả nhóm.
- PRD-0 mơ hồ (thứ tự trong bước, tie-break) → PO ghi `docs/clarify.md`, hỏi sớm.
- Hard-code số hoặc dùng `random` toàn cục → hỏng tất định; luồng 5 kiểm bằng chạy 2 lần cùng seed.
- Hết giờ chưa xong → vẫn tag đúng hạn, ghi trung thực phần chưa đạt.
