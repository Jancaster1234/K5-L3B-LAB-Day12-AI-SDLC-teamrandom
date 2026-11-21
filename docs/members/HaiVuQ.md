# HaiVuQ — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm (kèm link commit):**
  - PO: điền dòng của mình trong `TEAM.md` (`ad712f9`); gom 10 câu hỏi/giả định vào [`docs/clarify.md`](../clarify.md), cập nhật [`docs/plan/phase-1.md`](../plan/phase-1.md), [`docs/standup.md`](../standup.md) (`100688a`). Các mục clarify **chưa** được đối chiếu với PRD-0.
  - Quán lát 3 (`e50cabd`): `_spawn_customers`, `_tick_patience`, `_available`, `_release`, `_cookable_dishes`, suy ra `reserved` từ scenario + kiểm mâu thuẫn trong `chonoi/scenario.py`; 12 test [`tests/test_quan_lat3.py`](../../tests/test_quan_lat3.py); bằng chứng [`docs/proof/phase-1/quan-lat3/`](../proof/phase-1/quan-lat3/README.md) (`f64cc5f`).
- **Tôi đã review (kèm link):**
  - (Chưa review chính thức PR/commit nào của bạn khác — TODO: tự điền khi review.)
- **AI sai ở đâu và tôi phát hiện thế nào:**
  - AI ghi các mục clarify là "Chốt" dù không có quyền truy cập PRD-0, và tự viết một ví dụ "AI sai" không có thật trong file này. Tôi phát hiện khi đọc lại trước lúc gộp và yêu cầu sửa thành "giả định" (commit sửa sau `f64cc5f`).
  - AI cũng chọn thứ tự `step()` của quán khác với contract của lát 4 (clarify #3) — phát hiện khi so với nhánh `quan-lat4`.
- **Điều tôi học được:**
  - (TODO: tự điền.)
