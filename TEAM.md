# TEAM

**Tên nhóm:** teamrandom  **Số người:** 5  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Bùi Phan Thanh Phúc (trưởng nhóm) | Jancaster1234 | `sim/gather` — lát 1: oxy, ngạt, Máu, ngất · `sim/quan` tích hợp · `qa` (nhận từ Tuấn) | Integrator (giữ `docs/contracts/`, gộp code, gắn tag) + QA lead (từ khi Tuấn nghỉ) | lát 2, `qa` |
|Nguyễn Đức Hải |ndhai255 | `sim/gather` — lát 2: hái nút, bắt cá, giỏ đầy | Dev | lát 1, Integrator (gắn tag nếu vắng) |
|Vũ Quang Hải |HaiVuQ | `sim/quan` — lát 3: khách, giữ chỗ, kiên nhẫn | PO (đọc PRD trên lab board, hỏi giảng viên, giữ `docs/clarify.md`, viết `docs/plan/`) | lát 4 |
|Hoàng Ngọc Hiệu |hoangngochieu10012000 | `sim/quan` — lát 4: bếp, bàn, trả tiền, boa, uy tín | Scrum/Release (`docs/standup.md`, `CHANGELOG.md`, Release) | lát 3 |
|Nguyễn Văn Tuấn |tuannguyen-cell | `qa` + `client/ui` + harness AI (**đã nghỉ, 2026-11-21, giữa Phase 1**) | QA lead tới khi nghỉ: skill `run-phase-qa`, `verify-phase-proof`, hướng dẫn Windows, verification Phase 1. Việc còn lại chuyển cho Jancaster1234 | — |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: Discord nhóm teamrandom.
- Khi bất đồng về thiết kế: nói 2 phút, không xong thì Integrator quyết và ghi lý do (ADR ở `docs/adr/` nếu đụng contract).
- Khi ai đó trễ hoặc vướng quá 10 phút: báo ngay trong kênh, người dự phòng (cột cuối) nhận việc.
- Giờ standup giữa phase: giữa mỗi phase 3 phút, Scrum ghi vào `docs/standup.md`.
- Không chờ nhau: mỗi lát sở hữu hàm riêng (xem `docs/plan/phase-1.md`), tự viết test cho lát mình bằng scenario dựng sẵn; QA đọc commit trước khi tag.
- Cách làm việc với Git: nhánh ngắn theo lát (`gather-lat1`, `quan-lat3`…), chạy test rồi gộp vào `main`; chỉ Integrator gắn tag `phase-n`.
- Đổi nhân sự: Tuấn nghỉ giữa Phase 1; giữ tên trong bảng vì commit đã làm vẫn tính. Việc QA chuyển cho trưởng nhóm, người dự phòng gắn tag là Đức Hải.
- Mỗi người ≥ 3 commit có nội dung bằng tài khoản của mình; làm cặp thì ghi `Co-authored-by:`.
