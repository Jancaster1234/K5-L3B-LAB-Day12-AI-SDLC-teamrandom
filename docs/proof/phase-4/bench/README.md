# Bằng chứng — Phase 4 bench (`bench_cmd`)

- **Lệnh:** `python3 -m chonoi.bench --seed 42 --duration 30 --out docs/proof/phase-4/bench/bench.json` (exit 0)
- **Code:** `chonoi/bench.py` (mới, chỉ thư viện chuẩn), test `tests/test_bench.py` · nhánh `NguyenDucHai`, đã merge `main` @ `4c78cee` · **Người làm:** ndhai255 (dùng Claude Code)
- **Môi trường:** Python 3.14.4, Linux, Intel i5-12500H (16 luồng) · **Ngày:** 2026-11-21

## Cảnh đo

Buổi sáng lõi: `runner.Session("gather", load_contract()["tuning"], {}, 42)`, mỗi khung `step()` với input rỗng (Út Sen đứng yên ở bến), rồi render phần mềm vào `bytearray(1280 * 720 * 3)` (RGB): tô nền (trời + nước), vẽ hình chữ nhật cho bến, nút hái (6), đàn cá (8, bơi theo v1.1), Cá Sấu (`monsters`, 1) và người chơi, đọc từ `session.snapshot()`. Buổi sáng hết giờ (10800 tick) thì dựng lại Session cùng seed, tính vào khung đó. Làm nóng 3 s, đo 30 s bằng `time.perf_counter` (chỉ trong bench, không đi vào sim). Đã đối chiếu nguyên văn Ticket-04 ([`docs/clarify.md`](../../../clarify.md) #12–#13): #13 (`load_ms` tới khung đầu tiên của cảnh, trước làm nóng) khớp code; #12 (dựng lại khi hết buổi) ticket không quy định, giữ giả định.

## Đối chiếu Ticket-04 mục 1 "Benchmark có render"

| Ticket-04 | `chonoi/bench.py` | Kết quả |
|---|---|---|
| `<bench_cmd> --seed <int> --duration <giây> --out <bench.json>`; `game.contract.json` có `bench_cmd` | `bench_cmd: "python3 -m chonoi.bench"`, `argparse` nhận đủ 3 cờ | Khớp |
| Năm trường `avg_fps, p1_low_fps, frames, measured_s, load_ms` | Ghi đúng 5 trường (`tests/test_bench.py`) | Khớp |
| `frames`, `measured_s`: số khung và số giây thực tế trong khoảng đo sau làm nóng; `avg_fps = frames / measured_s` | Đếm khung và giây `perf_counter` sau 3 s làm nóng | Khớp |
| `p1_low_fps`: `max(1, ceil(0.01 × frames))` khung chậm nhất, nghịch đảo thời gian trung bình (giây) | `p1_low()` | Khớp |
| `load_ms`: từ lúc khởi chạy đến khung đầu tiên của cảnh đo | Từ lúc nạp `chonoi.bench` đến hết khung đầu, trước làm nóng | Khớp (clarify #13; chưa gồm khởi động trình thông dịch) |
| Seed 42, làm nóng 3 s, đo 30 s; Út Sen đứng yên ở bến | `--seed 42`, `WARMUP_S = 3.0`, input rỗng | Khớp |
| Cảnh: buổi sáng lõi với độ tươi, cá bơi, Cá Sấu Năm Chèo | `Session("gather")` chạy luật v1.2 thật (độ tươi, cá bơi, `monsters`) | Khớp |
| Cửa sổ 1280×720, "hiệu ứng mặc định" | Render phần mềm vào framebuffer 1280×720, không mở cửa sổ thật, không có hiệu ứng | **Giới hạn đã biết** (ghi ở AC-P4-01). Ticket: điểm dựa vào chạy được lệnh và đúng `bench.json`; mốc FPS chỉ để báo cáo |

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
