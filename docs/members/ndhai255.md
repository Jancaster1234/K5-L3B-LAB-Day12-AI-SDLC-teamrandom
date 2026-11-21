# ndhai255 (Nguyễn Đức Hải) — phản tư cá nhân (≤ 200 từ)

> **Bản ghi nhận do Integrator (Jancaster1234) soạn từ git log, `docs/proof/`, `docs/ai-usage-log.md` và `docs/clarify.md` ngày 2026-11-21. Đức Hải chưa đọc/xác nhận; đây không phải lời của Hải.** Mục nào chỉ Hải trả lời được thì để trống.

- **Tôi đã làm (kèm link commit):**
  - P1 gather lát 2: `_harvest`, `_catch`, `_hold_add` + 14 test `tests/test_gather_lat2.py` ([`cdf80eb`](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/commit/cdf80eb)).
  - Bằng chứng `docs/proof/phase-1/gather-lat2/` + kiểm tên sự kiện với contract mục 4 ([`0917559`](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/commit/0917559)).
  - P4 `bench_cmd`: `chonoi/bench.py`, `tests/test_bench.py`, [bằng chứng bench](../proof/phase-4/bench/README.md), giả định clarify #12–#13 ([`d5e401b`](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/commit/d5e401b)).
- **Tôi đã review (kèm link):** (theo git) resolve conflict khi gộp `main` (gather lát 1) vào nhánh lát 2 ([`ceddf63`](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/commit/ceddf63)); tự gộp PR [#1](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/pull/1), [#3](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/pull/3), [#4](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/pull/4) vào `main`.
- **AI sai ở đâu và tôi phát hiện thế nào:** (theo nhật ký AI và clarify) ở lát 2, AI tự chọn giả định "giỏ thiếu chỗ nhận một phần" và "`catch` hụt vẫn hồi chiêu"; đối chiếu PRD-0 thì sai, Integrator sửa lại (clarify #2, #8). AI đánh trùng số clarify #6, phát hiện khi resolve conflict và đổi thành #8.
- **Điều tôi học được:** _(chờ Hải tự viết)_
