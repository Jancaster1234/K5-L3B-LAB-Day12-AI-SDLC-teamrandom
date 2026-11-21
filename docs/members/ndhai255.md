# ndhai255 (Nguyễn Đức Hải) — phản tư cá nhân (≤ 200 từ)

> Hải soạn cùng Claude Code; thay bản Integrator ghi hộ (`0184489`).

- **Tôi đã làm (kèm link commit):**
  - P1 gather lát 2: `_harvest`, `_catch`, `_hold_add` + 14 test ([`cdf80eb`](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/commit/cdf80eb)); [bằng chứng 7 kịch bản](../proof/phase-1/gather-lat2/README.md)([`0917559`](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/commit/0917559)).
  - P4 `bench_cmd`: `chonoi/bench.py`, `tests/test_bench.py`, [bằng chứng bench 30 s](../proof/phase-4/bench/README.md), giả định clarify #12–#13 ([`d5e401b`](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/commit/d5e401b)).
- **Tôi đã review (kèm link):** resolve conflict khi gộp gather lát 1 vào lát 2 ([`ceddf63`](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/commit/ceddf63)); gộp PR [#1](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/pull/1), [#3](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/pull/3), [#4](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/pull/4).
- **AI sai ở đâu và tôi phát hiện thế nào:**
  - Lát 2: chưa có PRD-0, AI tự chọn "giỏ thiếu chỗ nhận một phần" và "`catch` hụt vẫn hồi chiêu". PO đối chiếu thì cả hai sai; Integrator sửa (clarify #2, #8).
  - AI đánh trùng số clarify #6; lộ ra lúc resolve conflict, đổi thành #8.
  - Bench: `load_ms` tính trước hay sau làm nóng lệch ~22 ms/~3000 ms; ticket không rõ → ghi giả định #13 chờ PO.
- **Điều tôi học được:** giả định AI tự chọn phải ghi vào clarify và có test bám theo, để PO chốt khác thì sửa nhanh. Số bench phụ thuộc máy: test kiểm cấu trúc, không so byte.
