# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| 1 | tuannguyen-cell (Nguyễn Văn Tuấn) | Codex | Lát 5: cấu hình chạy Windows, kiểm chứng lại 4 fixture lát 1, link verification, tạo 2 skill QA/proof và log test | Không đo | So byte lần đầu báo khác do Git checkout CRLF; đối chiếu blob Git xác nhận cùng nội dung gốc. Sửa script để so byte với blob và giữa hai output mới. 44 test đạt; chưa kết luận toàn phase, giữ các giả định clarify #6/#7 chờ PO |
| 1 | Jancaster1234 | Claude Code (Claude Opus 5.5) | Đọc lab, chia 5 luồng, soạn `TEAM.md`, `docs/plan/phase-1.md` | không đo | Lab board không hiện PRD-0 cho AI nên phân công dựa vào README + `TODO(nhóm)` trong code |
| 1 | Jancaster1234 | Claude Code (Claude Opus 5.5) | Soạn nháp `docs/contracts/README.md` + câu hỏi `docs/clarify.md` | không đo | Tên sự kiện/trường khách là AI **đoán** từ code khung và UI, đánh dấu ⚠ chờ PO đối chiếu PRD-0 |
| 1 | Jancaster1234 | Claude Code (Claude Opus 5.5) | Gather lát 1 (`_update_oxygen`) + 12 test + bằng chứng `docs/proof/phase-1/gather-lat1/` | không đo | Lần chạy test đầu lỗi `No module named 'helpers'` vì trên Windows `PYTHONPATH` phải dùng `;` chứ không phải `:`; AI tự chọn 2 giả định (clarify #6, #7), người cần duyệt với PRD-0 |
