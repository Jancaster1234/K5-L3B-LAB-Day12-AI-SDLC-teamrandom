# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Windows PowerShell: `powershell -ExecutionPolicy Bypass -File .\lab.ps1 setup`, sau đó `powershell -ExecutionPolicy Bypass -File .\lab.ps1 test`.
- Nếu chạy test thủ công trên Windows: `$env:PYTHONPATH = 'tests;.'` (dấu `;`). Contract gọi `python3`: dùng Python thật trong venv; script setup tạo tên lệnh này cục bộ, không đổi contract.
- Headless: `python3 -m chonoi.headless --mode gather|quan|day --seed 1 --ticks 600 --out out.jsonl` (`day` thêm `--days 1..5`)
- Contract v1.3: `python3 -m chonoi.soak --seed 7 --days 10 --out soak.json` (~11 s), `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json`
- Chơi thử trên trình duyệt: `python3 -m chonoi.live --mode gather|quan|day` (mở địa chỉ in ra; WASD, E, Space, Esc/P, H, Shop 1/2/Enter, R). Windows báo `WinError 10013` ở cổng 8000 thì thêm `--port 8765`.

## Cấu trúc & quy ước
- (Starter Python là TÙY CHỌN; nhóm có thể dùng ngôn ngữ khác nếu giữ Test Contract.) Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi của nhóm: `chonoi/sim/gather.py`, `chonoi/sim/quan.py` (tìm `TODO(nhóm)`).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.
- Đồ họa chỉ ở client (`chonoi/web/index.html`, ảnh trong `chonoi/web/assets/`, phục vụ qua `GET /assets/<file>` của `live.py`). Asset ngoài chỉ CC0/CC-BY/MIT, giữ file license gốc cạnh ảnh và ghi `CREDITS.md`. Ảnh chưa tải thì client phải vẽ được hình khối thay thế.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase và hợp đồng kho trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- [run-phase-qa](.agents/skills/run-phase-qa/SKILL.md): chạy suite trước tích hợp/tag, lưu exit code và log thật, phân biệt lỗi Windows với lỗi luật.
- [verify-phase-proof](.agents/skills/verify-phase-proof/SKILL.md): chạy lại fixture lát 1, so byte với bằng chứng gốc và hai lần cùng seed, cập nhật link verification và giả định chờ PO.
- Windows trước QA/demo: `$env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'; $env:PYTHONPATH = 'tests;.'`, rồi `powershell -ExecutionPolicy Bypass -File .\lab.ps1 test`. UTF-8 áp dụng cả khi đọc stdout/stderr của tiến trình con; riêng `PYTHONIOENCODING` chưa đủ.
- Phạm vi proof: `replay_lat1.py` phục vụ bộ bằng chứng v1.0 trên checkout `39fc6fd`. Không dùng kết quả so blob v1.0 để kết luận hồi quy trên v1.2 (schema kho đã đổi). Với code hiện tại chạy toàn suite, đặc biệt `tests/test_fresh.py` và `tests/test_quan_integration.py`; đọc phiên bản contract/clarify mới nhất trước khi dùng hướng dẫn lịch sử trong skill.
- Phase 4: [checklist demo và lệnh PowerShell](docs/demo.md). Chỉ đánh dấu bước đã chạy, ghi rõ phần UI/soak còn thiếu; Integrator gộp nhánh và gắn tag.
- Sau phát hành (v1.1.0): sửa giao diện thì agent phải tự xem kết quả — chạy `chonoi.live`, điều khiển bằng `POST /input`, chụp `msedge --headless=new --screenshot` rồi đọc ảnh (cách làm và ảnh mẫu: [docs/proof/phase-4/ui/](docs/proof/phase-4/ui/README.md)). Test không bắt được chữ đè nhau hay emoji Unicode mới thành ô vuông trên Windows 10.
- Phát hành: tag có ghi chú + `gh release create` với zip từ `git archive --prefix=<repo>-vX.Y.Z/`; giải nén zip và chạy lại suite trước khi tải lên. Kiểm "chạy được tại từng tag" bằng `git worktree add --detach <thư mục> <tag>` rồi chạy suite trong đó.
- Phản tư `docs/members/<handle>.md` là bài chấm cá nhân: agent không viết thay giọng thành viên khác; nếu thiếu thì chỉ soạn bản ghi nhận dữ kiện và ghi rõ người soạn.
