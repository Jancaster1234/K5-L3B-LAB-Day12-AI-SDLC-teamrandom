# Bằng chứng — Phase 4 bench (`bench_cmd`)

- **Lệnh:** `python3 -m chonoi.bench --seed 42 --duration 30 --out docs/proof/phase-4/bench/bench.json` (exit 0)
- **Code:** `chonoi/bench.py` (mới, chỉ thư viện chuẩn), test `tests/test_bench.py` · nhánh `NguyenDucHai`, đã merge `main` @ `4c78cee` · **Người làm:** ndhai255 (dùng Claude Code)
- **Môi trường:** Python 3.14.4, Linux, Intel i5-12500H (16 luồng) · **Ngày:** 2026-11-21

## Cảnh đo

Buổi sáng lõi: `runner.Session("gather", load_contract()["tuning"], {}, 42)`, mỗi khung `step()` với input rỗng (Út Sen đứng yên ở bến), rồi render phần mềm vào `bytearray(1280 * 720 * 3)` (RGB): tô nền (trời + nước), vẽ hình chữ nhật cho bến, nút hái (6), đàn cá (8, bơi theo v1.1), Cá Sấu (`monsters`, 1) và người chơi, đọc từ `session.snapshot()`. Buổi sáng hết giờ (10800 tick) thì dựng lại Session cùng seed, tính vào khung đó. Làm nóng 3 s, đo 30 s bằng `time.perf_counter` (chỉ trong bench, không đi vào sim). Giả định chờ PO: `docs/clarify.md` #12 (dựng lại khi hết buổi), #13 (`load_ms`).

## Kết quả (`bench.json`)

| Trường | Giá trị | Ý nghĩa |
|---|---|---|
| `frames` | 81998 | số khung trong 30 s đo |
| `measured_s` | 30.000 | thời gian đo thật |
| `avg_fps` | 2733.2 | `frames / measured_s` |
| `p1_low_fps` | 1577.7 | nghịch đảo trung bình của 820 khung chậm nhất (`max(1, ceil(0.01 × frames))`) |
| `load_ms` | 22.8 | từ lúc nạp `chonoi.bench` đến hết khung đầu tiên của cảnh (trước làm nóng) |

Số đo phụ thuộc máy và tải nền; chạy lại sẽ lệch vài phần trăm, không so byte.

## Kiểm

`PYTHONPATH=tests:. python3 -m unittest discover -s tests -v` → 146 test, OK (gồm `test_bench.py`: chạy `--duration 1`, đủ đúng 5 trường, kiểu số, `frames > 0`, `avg_fps ≈ frames / measured_s`).
