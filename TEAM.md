# TEAM

**Tên nhóm:** …  **Số người:** 4  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| | | `sim/gather` | Integrator (trưởng nhóm: fork, giữ `docs/contracts/`, gộp code, gắn tag) | `sim/quan` |
| | | `sim/quan` | PO (đọc PRD trên lab board, hỏi giảng viên, giữ `docs/clarify.md`, viết `docs/plan/`) | `sim/gather` |
| | | `client/ui` | Scrum/Release + harness AI (HUD, skill `.agents/skills/`, `AGENTS.md`, `ai-usage-log`, Release) | `qa` |
| | | `qa` | QA lead (test hộp đen theo AC, `docs/verification/`, `docs/proof/`, review trước tag, `retro`) | `client/ui` |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: …
- Khi bất đồng về thiết kế: nói 2 phút, không xong thì Integrator quyết và ghi lý do (ADR ở `docs/adr/` nếu đụng contract).
- Khi ai đó trễ hoặc vướng quá 10 phút: báo ngay trong kênh, người dự phòng (cột cuối) nhận việc.
- Giờ standup giữa phase: giữa mỗi phase 3 phút, Scrum ghi vào `docs/standup.md`.
- Cách đọc code của nhau: QA đọc commit `sim/*` trước khi tag; `sim/gather` và `sim/quan` đọc chéo nhau.
- Cách làm việc với Git: nhánh ngắn theo lát (`gather-lat1`, `quan-lat3`…), chạy test rồi gộp vào `main`; chỉ Integrator gắn tag `phase-n`.
- Mỗi người ≥ 3 commit có nội dung bằng tài khoản của mình; làm cặp thì ghi `Co-authored-by:`.
