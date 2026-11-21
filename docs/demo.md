# Checklist demo — Tuấn (QA), Phase 4

Theo việc 12b trong [kế hoạch nhóm](plan/lab-plan.md). Checklist được đối chiếu
với code và bằng chứng hiện có; nội dung Ticket-04 đầy đủ chưa lưu trong repo,
nên cần PO đối chiếu các tiêu chí chính thức trước khi chốt nghiệm thu.

## Chuẩn bị trên Windows

Mở PowerShell ở gốc repo. Các đầu ra demo ghi trong `.local/demo/`,
không ghi đè proof đã commit. Python thật trong venv giúp tránh Store alias.

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = 'tests;.'
powershell -ExecutionPolicy Bypass -File .\lab.ps1 setup
New-Item -ItemType Directory -Force .local/demo | Out-Null
```

## 1. Hồi quy và hai skill QA

- [ ] Chạy suite, ghi số test, exit code, commit, phiên bản Python vào bằng chứng khi trình diễn.

```powershell
powershell -ExecutionPolicy Bypass -File .\lab.ps1 test
```

- [ ] Giới thiệu [run-phase-qa](../.agents/skills/run-phase-qa/SKILL.md) dùng trước tích hợp/tag
  và [verify-phase-proof](../.agents/skills/verify-phase-proof/SKILL.md) dùng truy vết fixture → JSONL → verification.
- [ ] Nêu giới hạn: replay lát 1 là công cụ của v1.0; chạy trên checkout `39fc6fd` nếu cần tái hiện kết quả 44 test lịch sử.
  Trên v1.2 dùng suite hiện tại; không ghi đè JSONL lịch sử để làm replay xanh.

## 2. Chơi thử gather và quan, HUD độ tươi

Chạy từng lệnh trong terminal riêng, dừng bằng Ctrl+C. Chọn cổng khác nếu
đã có bản chơi thử cũ chạy nền.

```powershell
.\.venv\Scripts\python.exe -m chonoi.live --mode gather --seed 42 --port 8012
# Terminal khác: cảnh quán có sẵn nguyên liệu/khách theo fixture v1.2
.\.venv\Scripts\python.exe -m chonoi.live --mode quan --seed 1 --port 8013 --scenario docs/proof/phase-3/04-quan-fresh.scenario.json
```

- [ ] Mở http://127.0.0.1:8012/; WASD/mũi tên di chuyển, E tương tác, Space bắt cá, R chơi lại.
- [ ] Quan sát oxy khi lặn/nổi, Máu, hồi chiêu, số lượng giỏ và độ tươi sau thu hoạch.
- [ ] Mở http://127.0.0.1:8013/; E ở bếp, đợi nấu xong, E bưng rồi phục vụ bàn đúng đơn.
- [ ] Quan sát timer khách/bếp, tiền, uy tín, thống kê độ tươi/hàng ươn; lưu ảnh thực tế khi trình diễn.
- [ ] Nêu rõ live hiện chỉ có `gather`/`quan`; menu/DayIntro/Shop/pause UI, ba cảnh báo và tương phản cao chưa được xác nhận hoàn tất.
  Không coi test pause headless là bằng chứng UI pause hoạt động.

## 3. Bàn giao gather → file kho → quan (v1.2)

```powershell
.\.venv\Scripts\python.exe -m chonoi.headless --mode gather --seed 1 --ticks 1 --snapshot-every 1000 --scenario docs/proof/phase-3/02-handoff.scenario.json --inputs docs/proof/phase-3/02-handoff.inputs.json --out .local/demo/gather.jsonl --inventory-out .local/demo/kho.json
.\.venv\Scripts\python.exe -m chonoi.headless --mode quan --seed 1 --ticks 0 --inventory .local/demo/kho.json --out .local/demo/quan.jsonl
Get-Content .local/demo/kho.json
Get-Content .local/demo/quan.jsonl
```

- [ ] Kho chứa mảng cá thể `{id,kind,fresh}`, không dùng schema đếm v1.0.
- [ ] Giỏ I1 (ca_linh, fresh 100) cập bến sau một bước; kho còn khoảng 99.991667,
  snapshot quán tick 0 cùng id/kind, fresh 99.992 do JSONL làm tròn ba chữ số.
- [ ] Giới thiệu test trọn vòng quán, test độ tươi, pause và Shop:

```powershell
.\.venv\Scripts\python.exe -m unittest test_quan_integration test_fresh test_day -v
```

## 4. Headless nhiều Ngày và tất định

```powershell
.\.venv\Scripts\python.exe -m chonoi.headless --mode day --seed 42 --days 2 --ticks 50000 --snapshot-every 1000 --out .local/demo/day-a.jsonl
.\.venv\Scripts\python.exe -m chonoi.headless --mode day --seed 42 --days 2 --ticks 50000 --snapshot-every 1000 --out .local/demo/day-b.jsonl
Get-Content .local/demo/day-a.jsonl -Tail 1
Get-FileHash .local/demo/day-a.jsonl,.local/demo/day-b.jsonl -Algorithm SHA256
```

- [ ] Dòng cuối có `reason:days_complete`, `days_completed:2`.
- [ ] Hai SHA-256 giống nhau; giới thiệu chuỗi pha và sự kiện Shop trong JSONL.
- [ ] Ghi rõ: chạy hai Ngày với input rỗng là kiểm tra hồi quy/tất định,
  chưa thay thế soak 10 Ngày có bot của Phase 4.

## 5. Benchmark 1280×720

```powershell
.\.venv\Scripts\python.exe -m chonoi.bench --seed 42 --duration 30 --out .local/demo/bench.json
Get-Content .local/demo/bench.json
```

- [ ] Đo 30 giây sau 3 giây làm nóng; báo máy và tải nền cùng `frames`,
  `measured_s`, `avg_fps`, `p1_low_fps`, `load_ms`.
- [ ] Nêu đúng phạm vi: render phần mềm RGB trong bench, không phải FPS trình duyệt.
  Tham khảo [bằng chứng bench của Đức Hải](proof/phase-4/bench/README.md);
  không dùng số máy khác làm kết quả máy demo.

## 6. Kiểm tra bàn giao Integrator

- [ ] Link [verification P1](verification/phase-1.md), [P2](verification/phase-2.md),
  [P3](verification/phase-3.md), [ADR đổi kho](adr/0001-kho-ca-the-v12.md).
- [ ] Đối chiếu lại clarify #6/#7: đã được PO xác nhận; ghi chú chờ PO trong proof QA cũ là lịch sử.
- [ ] Tại nền `c32eac3`, manifest đang v1.2, chưa có `soak_cmd`/`bench_cmd`;
  có module bench gọi trực tiếp. Integrator phụ trách khai manifest v1.3,
  soak 10 Ngày có bot, UI/accessibility, tag/release và đóng gói.
- [ ] Chỉ đánh dấu hoàn thành các mục đã quan sát/chạy thật;
  ghi mục thiếu và bàn giao thay vì tuyên bố toàn bộ Phase 4 đạt.

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
