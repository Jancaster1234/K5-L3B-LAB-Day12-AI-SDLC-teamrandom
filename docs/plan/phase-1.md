# Kế hoạch Phase 1 (≤ 1 trang)

- Mục tiêu: hoàn thành luật `gather` (lát 1–2) và `quan` (lát 3–4) theo PRD-0, qua smoke test + test AC của nhóm, gắn tag `phase-1` trước 1:00.

- Việc / người / phụ thuộc (link issue):

| Thời gian | Việc | Người | Phụ thuộc |
|---|---|---|---|
| 0:00–0:15 | Fork, add collaborator, điền `TEAM.md`, sửa `team` trong `game.contract.json`, `tools/check_team.py` OK | Cả nhóm (Integrator dẫn) | — |
| 0:00–0:15 | Chốt `docs/contracts/` (schema kho, sự kiện gather/quan, giao diện sim↔UI) | Integrator + PO | PRD-0 |
| 0:15–0:30 | Lát 1 gather: oxy, dive/surface, choke, Máu, faint, giỏ LIFO | `sim/gather` | contracts |
| 0:30–0:45 | Lát 2 gather: hái nút, regrow, bắt cá (cooldown), hold_full | `sim/gather` | lát 1 |
| 0:15–0:30 | Lát 3 quan: khách theo lịch, chọn món, giữ chỗ, kiên nhẫn, customer_left, no_dish | `sim/quan` | contracts |
| 0:30–0:45 | Lát 4 quan: bếp/bàn, served, paid, boa, uy tín, quan_end | `sim/quan` (+ `client/ui` pair) | lát 3 |
| 0:15–0:45 | HUD đọc snapshot + skill #1 ở `.agents/skills/`, cập nhật `AGENTS.md`, `ai-usage-log` | `client/ui` | contracts |
| 0:15–0:50 | Test hộp đen theo AC từng lát, kiểm tất định (cùng seed → giống byte) | `qa` | contracts |
| 0:45–0:55 | Tích hợp gather → kho → quan, điền `docs/verification/phase-1.md` + `docs/proof/phase-1/` | `qa` + Integrator | tất cả |
| 0:55 | Gắn tag `phase-1` | Integrator | test xanh |

- Rủi ro:
  - PRD-0 có chỗ mơ hồ (thứ tự xử lý trong bước, tie-break) → PO ghi `docs/clarify.md`, hỏi sớm.
  - Lát quan nặng hơn gather → `client/ui` pair với `sim/quan` ở lát 4.
  - Hard-code số liệu hoặc dùng `random` toàn cục → làm hỏng tất định; QA kiểm bằng chạy 2 lần cùng seed.
  - Hết giờ chưa xong → vẫn tag đúng hạn, ghi trung thực phần chưa đạt.
