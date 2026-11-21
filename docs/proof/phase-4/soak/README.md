# Bằng chứng soak (Ticket-04 mục 2)

`python3 -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak/soak.json`

- Bot tất định (`chonoi/soak.py`): hái nút gần bến rồi cập bến, nấu → bưng → phục vụ ở quán, mua nâng cấp nếu đủ tiền, đóng Shop.
- Kết quả: `days_completed: 10`, `crashes: 0` (đạt điều kiện của runner lớp). Kế hoạch D1–D5 lặp ở Ngày 6–10; earned/uy tín tiếp tục xuyên Ngày.
- Chạy 2 lần cùng seed: các trường gameplay giống nhau (bỏ `duration_s`), xem `tests/test_soak.py`.
