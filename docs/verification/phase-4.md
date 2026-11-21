# Ma trận truy vết Phase 4 (Ticket-04, Test Contract v1.3)

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P4-01 — Contract v1.3 khai đúng lệnh (`bench_cmd`, `soak_cmd`); `bench_cmd` chạy cảnh chuẩn 1280×720 tạo `bench.json` đúng 5 trường; `soak_cmd` sẵn sàng cho runner lớp | Chạy `<bench_cmd> --seed 42 --duration 30 --out bench.json`, `<soak_cmd> --seed 7 --days 10 --out soak.json`, `tests/test_bench.py` | — | Chưa kiểm |
| AC-P4-02 — Clone sạch chạy bằng tối đa 3 lệnh trên macOS/Linux; 3 cảnh báo (thủy quái gần, oxy sắp hết, khách sắp giận) có chữ/biểu tượng và chế độ tương phản cao hoạt động | Chơi thử từ clone sạch theo `README.md` và kiểm tra 3 cảnh báo ở chế độ tương phản cao | — | Chưa kiểm |
| AC-P4-03 — Regression P1–P3 còn hiệu lực đạt; `docs/verification/phase-4.md` và bằng chứng khớp commit gắn tag; ghi chép làm rõ (`docs/clarify.md`) và nhật ký AI (`docs/ai-usage-log.md`) đã cập nhật | Chạy toàn bộ suite test (`run-phase-qa` + `verify-phase-proof`), đối chiếu commit bàn giao | — | Chưa kiểm |
| AC-P4-04 — `CHANGELOG.md`, release notes (`docs/release-notes-v1.0.0.md`) và bản đóng gói đầy đủ; tag `phase-4` và GitHub Release `v1.0.0` cùng trỏ tới commit trên `main` | Kiểm tra `CHANGELOG.md`, `CREDITS.md`, `docs/release-notes-v1.0.0.md`, tag `phase-4` và Release `v1.0.0` | — | Chưa kiểm |
| AC-P4-05 — Retro đã rà hành động P2 và chốt việc tiếp theo; có phản tư cá nhân đủ người (`docs/members/<handle>.md`) và bằng chứng đóng góp từng người (`git shortlog -sn`) để đánh giá chéo | Kiểm tra `docs/retro.md`, `docs/members/*.md` và `git shortlog -sn` | — | Chưa kiểm |
| AC-P4-06 — Nếu làm mở rộng, có bài kiểm và bằng chứng cho từng mục | Kiểm tra mục mở rộng trong `README.md` và test/bằng chứng tương ứng (P2 đã có `burn` ở `tests/test_ext_burn.py`) | — | Chưa kiểm |

## Đánh giá ngắn
- Ma trận tạo từ DoD của Ticket-04 trên nhánh `haivq-p4-docs`; QA/Integrator điền bằng chứng và kết quả thực tế sau khi tích hợp đủ phần việc Phase 4.
