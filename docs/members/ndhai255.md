# ndhai255 (Nguyễn Đức Hải) — ghi nhận đóng góp

> **Do Integrator (Jancaster1234) soạn từ git log, `docs/proof/` và `docs/ai-usage-log.md` ngày 2026-11-21, Đức Hải chưa đọc/xác nhận.** Đây không phải phản tư do Hải viết; chỉ ghi sự thật kiểm chứng được. Hải sẽ sửa thành phản tư của mình và commit bằng tài khoản `ndhai255`.

- **Đã làm:**
  - P1 gather lát 2: `_harvest`, `_catch`, `_hold_add` + 14 test `tests/test_gather_lat2.py` ([`cdf80eb`](../../../../commit/cdf80eb), PR #1); resolve conflict khi gộp lát 1 ([`ceddf63`](../../../../commit/ceddf63)).
  - Bằng chứng `docs/proof/phase-1/gather-lat2/` + kiểm tên sự kiện với contract mục 4 ([`0917559`](../../../../commit/0917559), PR #3).
  - P4 `bench_cmd`: `chonoi/bench.py`, `tests/test_bench.py`, bằng chứng `docs/proof/phase-4/bench/`, giả định clarify #12–#13 ([`d5e401b`](../../../../commit/d5e401b), PR #4).
- **Đã review:** _(chờ Hải điền)_ — git chỉ cho thấy Hải tự gộp PR #1, #3, #4.
- **AI sai ở đâu (theo nhật ký AI và clarify):** lát 2, AI tự chọn giả định "giỏ thiếu chỗ nhận một phần" và "`catch` hụt vẫn hồi chiêu"; đối chiếu PRD-0 thì sai (từ chối cả lượt, hụt không hồi chiêu), Integrator sửa lại (`docs/clarify.md` #2, #8). AI đánh trùng số clarify #6 khi gộp lát 1, phát hiện lúc resolve conflict. Hải phát hiện thế nào: _(chờ Hải điền)_.
- **Điều học được:** _(chờ Hải điền)_.
