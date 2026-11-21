# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| Lát 1 — oxy giảm dưới nước, oxygen_empty đúng một lần | Fixture oxy 3, chạy 5 tick; event tick 3, cuối tick 5 oxy 0 | [Fixture](../proof/phase-1/gather-lat1/01-oxy.scenario.json), [JSONL](../proof/phase-1/gather-lat1/01-oxy.out.jsonl), [QA replay](../proof/phase-1/qa-lat5/replay-output.txt) | Đạt theo fixture và test lát 1 |
| Lát 1 — ngạt theo chu kỳ, trừ Máu | Fixture oxy 1, 120 tick; choke tick 60 và 120, Máu 2 rồi 1 | [Fixture](../proof/phase-1/gather-lat1/02-choke.scenario.json), [JSONL](../proof/phase-1/gather-lat1/02-choke.out.jsonl) | Đạt theo giả định clarify #6; chờ PO đối chiếu PRD |
| Lát 1 — ngất mất giỏ, xuất kho rỗng | Fixture Máu 1, đếm ngạt 59; choke → faint → gather_end(fainted) tại tick 1 | [Fixture](../proof/phase-1/gather-lat1/03-faint.scenario.json), [JSONL](../proof/phase-1/gather-lat1/03-faint.out.jsonl), [Kho rỗng](../proof/phase-1/gather-lat1/03-faint.inventory.json) | Đạt; QA replay kiểm kho bằng JSON |
| Lát 1 — dive/surface, hồi oxy và kẹp trần | Bơi xuống/lên: dive tick 11, surface tick 116; tick 200 oxy 1800, đếm ngạt 0 | [Scenario](../proof/phase-1/gather-lat1/04-dive-surface.scenario.json), [Input](../proof/phase-1/gather-lat1/04-dive-surface.inputs.json), [JSONL](../proof/phase-1/gather-lat1/04-dive-surface.out.jsonl) | Đạt theo fixture và test lát 1 |
| Lát 1 — ngất trước cập bến; nổi lên reset ngạt | `Faint.test_ngat_xet_truoc_cap_ben`, `Choke.test_noi_len_reset_dem_ngat` | [Test lát 1](../../tests/test_gather_lat1.py), [Log QA](../proof/phase-1/qa-lat5/test-output.txt) | Đạt theo giả định clarify #7; chờ PO đối chiếu PRD |
| QA — tất định từng byte của 4 fixture lát 1 | Mỗi fixture chạy 2 lần seed 1; so byte với blob bằng chứng tại HEAD, SHA-256 trong log | [Script replay](../../.agents/skills/verify-phase-proof/scripts/replay_lat1.py), [Kết quả 4/4](../proof/phase-1/qa-lat5/replay-output.txt) | Đạt; so blob Git tránh CRLF do checkout Windows |
| QA — hồi quy, giao tiếp gather → kho → quan | Toàn suite: 44 test gồm 12 test lát 1, live server và smoke tích hợp kho | [Test tích hợp hiện có](../../tests/test_smoke_p1.py), [Log QA 44/44](../proof/phase-1/qa-lat5/test-output.txt) | Đạt trong phạm vi suite; chưa chứng minh toàn bộ luật quán |
| Harness AI — 2 skill của nhóm | Kiểm tra frontmatter bằng quick_validate; thực thi script replay | [run-phase-qa](../../.agents/skills/run-phase-qa/SKILL.md), [verify-phase-proof](../../.agents/skills/verify-phase-proof/SKILL.md), [Log kiểm skill 1](../proof/phase-1/qa-lat5/skill-validation.txt), [Log kiểm skill 2](../proof/phase-1/qa-lat5/skill-validation-proof.txt) | Đạt kiểm tra cấu trúc; script replay chạy thành công |
| Lát 2–4 và HUD đầy đủ | Cần bằng chứng riêng sau tích hợp từng lát | [Kế hoạch phân công](../plan/phase-1.md) | Chưa xác nhận trong lượt QA này |

## Đánh giá ngắn
- QA: Nguyễn Văn Tuấn (`tuannguyen-cell`), ngày 2026-11-21, Windows / Python 3.13.3. Nhánh `qa-lat5`, nền kiểm tra `b1f71ee` (code lát 1 `d150448`). [Tổng hợp QA](../proof/phase-1/qa-lat5/README.md), [bằng chứng tác giả lát 1](../proof/phase-1/gather-lat1/README.md).
- 44/44 test đạt; 4/4 fixture khớp bản Git và hai lần chạy; chưa xác nhận đạt toàn Phase 1. Nhãn trên là mô tả luật, chưa phải mã AC chính thức từ lab board.
- Cần PO đối chiếu [clarify #6, #7](../clarify.md) và tên trường sự kiện trong [contract nháp](../contracts/README.md) với PRD-0. Kết quả chạy đúng theo giả định hiện tại không thay thế việc xác nhận yêu cầu.
- Sau khi Integrator tích hợp lát 2–4: chạy lại suite, bổ sung proof riêng và cập nhật ma trận trước tag. Không gộp main hay gắn tag trong lượt QA này.
