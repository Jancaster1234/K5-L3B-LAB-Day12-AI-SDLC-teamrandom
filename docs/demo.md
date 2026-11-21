# Checklist demo — Phase 4 (cập nhật cho v1.1.0)

Bản đầu do Tuấn (QA) viết theo việc 12b trong [kế hoạch nhóm](plan/lab-plan.md); Integrator cập nhật
cho Release v1.1.0 (cửa sổ `day`, Shop, cảnh báo, tương phản cao, đồ họa mới). Ticket-04 đầy đủ chưa
lưu trong repo, PO đối chiếu tiêu chí chính thức trước khi chốt nghiệm thu.

Tổng thời lượng khoảng **10 phút**. Chỉ đánh dấu bước đã chạy thật; mục thiếu thì nói thẳng.

## 0. Chuẩn bị trên Windows (trước giờ demo)

Mở PowerShell ở gốc repo. Đầu ra demo ghi vào `.local/demo/` (đã gitignore), không ghi đè proof đã commit.
Python thật trong venv tránh lỗi Store alias `python3`.

```powershell
git pull
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = 'tests;.'
powershell -ExecutionPolicy Bypass -File .\lab.ps1 setup
New-Item -ItemType Directory -Force .local/demo | Out-Null
```

Nếu `chonoi.live` báo `không mở được cổng 8000: [WinError 10013]`, cổng đang bị Windows giữ;
dùng `--port 8765` (các lệnh dưới đã đặt sẵn cổng).

## 1. Hồi quy và hai skill QA (1 phút) — gợi ý: Tuấn

```powershell
powershell -ExecutionPolicy Bypass -File .\lab.ps1 test
git log -1 --oneline
```

- [ ] Đọc số test (**150 tests, OK**), exit code, commit và phiên bản Python.
- [ ] Giới thiệu [run-phase-qa](../.agents/skills/run-phase-qa/SKILL.md) dùng trước tích hợp/tag
  và [verify-phase-proof](../.agents/skills/verify-phase-proof/SKILL.md) truy vết fixture → JSONL → verification.
- [ ] Nêu giới hạn: replay lát 1 là công cụ của v1.0 (checkout `39fc6fd`, 44 test lịch sử);
  trên v1.2+ dùng suite hiện tại, không ghi đè JSONL lịch sử để làm replay xanh.

## 2. Chơi thật một Ngày (4 phút) — gợi ý: Phúc

```powershell
.\.venv\Scripts\python.exe -m chonoi.live --mode day --port 8765
```

Mở http://127.0.0.1:8765/. Phím: `WASD`/mũi tên, `E` tương tác, `Space` bắt cá, `Esc`/`P` tạm dừng,
`H` tương phản cao, Shop `1`/`2`/`Enter`, `R` chơi lại.

- [ ] **Lặn:** hái hoa ở mặt nước (`E`), lặn bắt cá (`Space`); chỉ thanh oxy, Máu, hồi chiêu,
  giỏ và thanh độ tươi; dòng "cần lấy" theo kế hoạch Ngày.
- [ ] Bơi sâu gần Cá Sấu → cảnh báo "Thủy quái" + viền tím; ở dưới lâu → "Oxy sắp hết". Về bến (`E`) bỏ đồ vào kho.
- [ ] `Esc` tạm dừng / tiếp tục; `H` bật tương phản cao (cảnh báo chữ vàng lớn).
- [ ] **Quán:** `E` ở bếp → lửa + đồng hồ → "Chín! (E)" → bưng → phục vụ bàn đúng đơn; chỉ bong bóng
  gọi món, thanh kiên nhẫn đổi màu, tiền, uy tín, kho và hàng ươn; cảnh báo "Khách sắp giận".
- [ ] **Shop:** `1`/`2` mua (thông báo "Đã mua…" hoặc "Không đủ tiền"), dòng "có hiệu lực từ Ngày kế", `Enter` đóng.
- [ ] Lưu ảnh chụp thực tế khi trình diễn.

Một Ngày đủ dài (3 phút lặn + ca quán). Thiếu giờ thì mở thêm cảnh quán dựng sẵn ở terminal khác:

```powershell
.\.venv\Scripts\python.exe -m chonoi.live --mode quan --seed 1 --port 8766 --scenario docs/proof/phase-3/04-quan-fresh.scenario.json
```

Mở http://127.0.0.1:8766/: có sẵn 2 khách đã giữ đồ, nấu và phục vụ được ngay.

## 3. Bàn giao gather → file kho → quán (v1.2) — gợi ý: Quang Hải

```powershell
.\.venv\Scripts\python.exe -m chonoi.headless --mode gather --seed 1 --ticks 1 --snapshot-every 1000 --scenario docs/proof/phase-3/02-handoff.scenario.json --inputs docs/proof/phase-3/02-handoff.inputs.json --out .local/demo/gather.jsonl --inventory-out .local/demo/kho.json
.\.venv\Scripts\python.exe -m chonoi.headless --mode quan --seed 1 --ticks 0 --inventory .local/demo/kho.json --out .local/demo/quan.jsonl
Get-Content .local/demo/kho.json
Get-Content .local/demo/quan.jsonl
```

- [ ] Kho chứa mảng cá thể `{id,kind,fresh}`, không dùng schema đếm v1.0.
- [ ] Giỏ I1 (ca_linh, fresh 100) cập bến sau một bước; kho còn khoảng 99.991667,
  snapshot quán tick 0 cùng id/kind, fresh 99.992 do JSONL làm tròn ba chữ số.
- [ ] Giới thiệu test trọn vòng quán, độ tươi, pause và Shop:

```powershell
.\.venv\Scripts\python.exe -m unittest test_quan_integration test_fresh test_day -v
```

## 4. Tất định nhiều Ngày, soak, bench — gợi ý: Đức Hải

Soak chạy khoảng 11 giây, bench 33 giây: có thể chạy ngay lúc demo hoặc chạy trước rồi mở kết quả.

```powershell
.\.venv\Scripts\python.exe -m chonoi.headless --mode day --seed 42 --days 2 --ticks 50000 --snapshot-every 1000 --out .local/demo/day-a.jsonl
.\.venv\Scripts\python.exe -m chonoi.headless --mode day --seed 42 --days 2 --ticks 50000 --snapshot-every 1000 --out .local/demo/day-b.jsonl
Get-Content .local/demo/day-a.jsonl -Tail 1
Get-FileHash .local/demo/day-a.jsonl,.local/demo/day-b.jsonl -Algorithm SHA256
.\.venv\Scripts\python.exe -m chonoi.soak --seed 7 --days 10 --out .local/demo/soak.json
Get-Content .local/demo/soak.json
.\.venv\Scripts\python.exe -m chonoi.bench --seed 42 --duration 30 --out .local/demo/bench.json
Get-Content .local/demo/bench.json
```

- [ ] Dòng cuối `day-a` có `reason:days_complete`, `days_completed:2`; hai SHA-256 giống nhau (cùng seed → cùng output).
- [ ] Soak: `days_completed: 10`, `crashes: 0`, điểm từng Ngày; bot tất định (xem [bằng chứng soak](proof/phase-4/soak/README.md)).
- [ ] Bench: đo 30 giây sau 3 giây làm nóng; báo máy và tải nền cùng `frames`, `measured_s`, `avg_fps`, `p1_low_fps`, `load_ms`.
  Đây là render phần mềm RGB 1280×720 trong bench, **không** phải FPS trình duyệt.
  Tham khảo [bằng chứng bench](proof/phase-4/bench/README.md); không dùng số máy khác làm kết quả máy demo.

## 5. Quy trình, phát hành và giới hạn (1 phút) — gợi ý: Quang Hải (PO), Hiệu (Release)

- [ ] Tag `phase-1` … `phase-4`; Release [v1.0.0](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/releases/tag/v1.0.0)
  và [v1.1.0](https://github.com/Jancaster1234/K5-L3B-LAB-Day12-AI-SDLC-teamrandom/releases/tag/v1.1.0) (đồ họa, contract vẫn v1.3).
- [ ] Verification [P1](verification/phase-1.md), [P2](verification/phase-2.md), [P3](verification/phase-3.md),
  [P4](verification/phase-4.md); [ADR-0001 đổi kho](adr/0001-kho-ca-the-v12.md); [CHANGELOG](../CHANGELOG.md).
- [ ] README (chạy ≤ 3 lệnh), [release notes v1.1.0](release-notes-v1.1.0.md), [CREDITS](../CREDITS.md) (asset Kenney CC0).
- [ ] `docs/ai-usage-log.md`, `docs/members/*.md`, `git shortlog -sn` cho đánh giá chéo.
- [ ] Nói trung thực phần còn thiếu:
  - chưa có Menu chính, DayIntro / DayResult / Summary; Shop chỉ thao tác bàn phím;
  - mở rộng P3 (dòng lũ, khách đặt trước) chưa làm; mở rộng P2 chỉ có `burn`;
  - `chonoi/live.py` (file khung) có thêm route `/assets` để tải ảnh;
  - cảnh lặn vector, cảnh quán/Shop pixel art; log sự kiện có thể đè góc phải dưới ở cửa sổ nhỏ.

## Lần kiểm tra của Tuấn

Ngày 2026-11-21, Windows / Python 3.13.3, nền `c32eac3`.
Lượt này bổ sung tài liệu demo và hướng dẫn phạm vi hai skill theo việc 12b.
Các checkbox thao tác trực quan để trống cho người trình diễn kiểm thực tế.

Kết quả chạy thật ở nền trên:

- `lab.ps1 test`: 146 tests, 41.139 giây, OK, exit 0; không có lỗi giải mã stderr khi bật UTF-8.
- Bàn giao kho và hai lượt `day --days 2`: đều exit 0, hai output giống từng byte,
  kết thúc tick 44400, `days_completed:2`.
- Bench: 18179 khung / 30.0000274 giây; avg_fps 605.97, p1_low_fps 242.91,
  load_ms 155.79, exit 0. Đây là số đo trên máy Windows hiện tại, không phải cam kết FPS trình duyệt.
- Output cục bộ: `.local/demo/{gather,quan,day-a,day-b}.jsonl`,
  `.local/demo/kho.json`, `.local/demo/bench.json`; transcript suite ở
  `.local/qa-latest-tests.txt`. Khi demo chính thức cần lưu proof của lần chạy đó theo quy trình nhóm.

## Lần kiểm tra cho v1.1.0 (Integrator)

Ngày 2026-11-21, Windows 10 / Python 3.12.0 (venv `lab.ps1 setup`), nền `a850660` (tag `v1.1.0`).

- `lab.ps1 test`: 150 tests, OK, exit 0 (thêm test route `/assets`); cũng xanh khi chạy trong zip Release v1.1.0 giải nén.
- `chonoi.soak --seed 7 --days 10`: exit 0, 10.9 giây, `days_completed: 10`, `crashes: 0`.
- `chonoi.live --mode day --port 8765` chạy được (cổng 8000 bị Windows chặn, WinError 10013).
  Cảnh lặn và quán kiểm bằng ảnh chụp Edge headless khi điều khiển qua `/input`;
  màn Shop kiểm bằng snapshot dựng sẵn, **chưa chơi tới Shop thật** trong live.
- Mục 3: hai lệnh headless exit 0; kho `I1 ca_linh fresh 99.99166…`, snapshot quán tick 0 `fresh 99.992`;
  `unittest test_quan_integration test_fresh test_day`: 26 tests, OK.
- Mục 4: hai lượt `day --seed 42 --days 2` exit 0, kết thúc tick 44400, `days_complete`, `days_completed:2`;
  SHA-256 giống nhau (`0A4F1BEB…868122`).
- Bench chưa chạy lại trên nền này.
