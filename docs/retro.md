# Retro nhóm

## Phase 1 (nháp — HaiVuQ ghi trước khi tag `phase-1`)
- **Điều tốt:**
  - Chia 5 lát cắt song song ngay từ đầu (`gather` lát 1–2, `quan` lát 3–4, QA/harness lát 5) giúp cả 5 thành viên làm độc lập, gộp vào `main` đạt 78/78 test xanh và có test tích hợp trọn vòng (`tests/test_quan_integration.py`).
  - Có bằng chứng chạy thật (`docs/proof/phase-1/`) và 2 skill QA tự kiểm tra/replay (`.agents/skills/`).
- **Điều tệ:**
  - Các nhánh mở sớm trước khi chốt contract chung dẫn tới lệch tên trường (`dish` vs `dish_id`), lệch thứ tự `step()` giữa lát 3 và lát 4 (`docs/contracts/quan.md` vs `docs/contracts/README.md`), và lệch handle GitHub trong `TEAM.md`.
  - AI tự ghi "Chốt" vào `docs/clarify.md` và tự bịa ví dụ trong phản tư dù chưa xem PRD-0 trên lab board; phải rà lại và sửa thủ công.
  - Đối chiếu PRD-0 hơi muộn (sau khi đã gộp lát 1–4) nên nhiều giả định trong contract nháp/code bị lệch so với PRD-0 mục D/E/F (tên trường event, `hold_full`/giỏ all-or-nothing, `catch` hụt không đặt cooldown, payload `hand`/`stove.dish`, thứ tự `step()` quán và `floor` cho `tip`) — phải tốn công sửa lại code trước khi chốt.
- **1 hành động cho Phase 2:**
  - Chốt một file contract duy nhất và đối chiếu PRD ngay đầu phase trước khi chia nhánh; người làm phải đọc lại toàn bộ output AI (đặc biệt là `clarify.md`, `proof/`, phản tư) trước khi push.

## Phase 2 (Retro Phase 2)
- **3 điều làm tốt:**
  - Ưu tiên làm lõi Test Contract v1.1 trước (cá bơi/sinh, Cá Sấu, `--mode day`, Shop, pause) và hoàn thành cả mở rộng `burn` (`tests/test_ext_burn.py`), đạt 127 test xanh (`docs/verification/phase-2.md`).
  - Chuyển sang mô hình tập trung vào một người sửa `chonoi/` + `game.contract.json` (`Jancaster1234`) để tránh conflict khi viết lại lớn theo PRD-0 và Ticket-02 (`docs/plan/lab-plan.md`).
  - Có bằng chứng chạy thật cho P2 (`docs/proof/phase-2/`, gồm `day --days 1`, nâng cấp nhiều Ngày, smoke tích hợp `gather` → `quan`).
- **3 điều vướng:**
  - Phải sửa lại Phase 1 theo đúng PRD-0 trước khi vào Phase 2 nên gắn tag `phase-2` trễ so với mốc 1:55.
  - Phần giao diện trên `chonoi.live` chưa làm xong menu/intro/Shop/HUD v1.1 (`AC-P2-08` chưa đạt).
  - Tuấn tạm nghỉ giữa Phase 1 rồi mới quay lại từ Phase 4, nên phần lớn việc P2–P3 dồn vào Integrator.
- **1 hành động cho Phase 3 (người nhận: `Jancaster1234`):**
  - Trước khi đổi schema kho sang cá thể `{id, kind, fresh}` (v1.2), viết `docs/adr/0001-kho-ca-the-v12.md` nêu rõ bảng tác động và thứ tự tích hợp, giữ `main` chạy được ở v1.1 cho tới lúc gộp xong toàn bộ test.

## Phase 4 (Retro cuối lab)
- **Rà lại hành động của retro P2:**
  - **Đã làm gì:** `Jancaster1234` đã lập [ADR-0001](adr/0001-kho-ca-the-v12.md) ghi rõ bảng tác động và thứ tự tích hợp trước khi đổi schema kho v1.2, giữ `main` chạy được ở v1.1 tới khi gộp (`369737b`, `4c78cee`), đạt 140/140 test xanh ở Phase 3 (`AC-P3-05`, `AC-P3-06`).
  - **Còn vướng gì, vì sao:** Tag `phase-3` vẫn gắn trễ so với mốc 2:30 do phải chuyển đổi 37 test cũ sang schema kho cá thể mới; đồng thời `chonoi.live` vẫn chưa có menu/intro/Shop trên cửa sổ chơi (`AC-P2-08`) và nhóm chưa làm mở rộng P3 (`AC-P3-07`) vì ưu tiên lõi Test Contract.
- **Điều tốt / điều tệ:**
  - Tốt: Tách ranh giới file rõ ràng ở Phase 4 (`docs/plan/lab-plan.md`) — `chonoi/bench.py` cho `ndhai255`, `docs/verification/phase-4.md` + `docs/retro.md` cho `HaiVuQ`, `README.md`/release notes cho `hoangngochieu10012000`, `AGENTS.md`/`docs/demo.md`/QA cho `tuannguyen-cell` — tránh xung đột khi tích hợp.
  - Tệ: Chênh lệch khối lượng giữa các thành viên ở P2–P3; cần đọc kỹ yêu cầu gốc trên lab board sớm hơn ngay từ đầu mỗi phase.
- **Một lỗi AI đã mắc và cách nhóm xác minh (theo `docs/ai-usage-log.md`):**
  - **Lỗi:** Ở Phase 1 (`HaiVuQ`), AI tự ghi các mục trong `docs/clarify.md` là "Chốt" dù không truy cập được PRD-0 trên lab board, và tự bịa một ví dụ "AI sai" trong `docs/members/HaiVuQ.md` (ngoài ra ở P2 `Jancaster1234` ghi nhầm mã commit bịa `9b0d…`, ở P3 AI chèn nhầm một test rỗng `pass`).
  - **Cách nhóm xác minh:** Người đọc lại diff và đối chiếu trực tiếp PRD-0/Ticket từ lab board trước khi gộp, sửa toàn bộ mục chưa kiểm thành giả định, xóa nội dung bịa và chạy lại toàn bộ `unittest` + `headless` kiểm chứng bằng chứng thật.
- **Nếu làm lại, đổi gì:**
  - Dán nguyên văn PRD/Ticket vào repo hoặc cho AI ngay từ phút đầu mỗi phase; chạy `check_team.py` và đối chiếu contract trước khi chia nhánh song song.

## Sau phát hành (Integrator `Jancaster1234`, 2026-11-21 tối)
- **Đã làm:** Release v1.1.0 chỉ đổi client (đồ họa ba cảnh, asset Kenney CC0), luật/contract/headless giữ nguyên; chạy lại suite tại cả 5 tag và clone sạch từ GitHub để chắc "chạy được tại từng tag".
- **Học được:** kiểm giao diện bằng ảnh chụp thật bắt được lỗi mà test không thấy (emoji 🫧 thành ô vuông trên Windows 10, chữ đè quầy bếp, quầy Shop tràn mép). Lần sau đưa bước chụp ảnh vào checklist QA ngay từ Phase 2, không để tới sau demo.
- **Còn mở:** mở rộng P3. (Đã xong sau đó: Menu/DayIntro/Buổi tối/Kết quả/Tổng kết, ảnh tương phản cao, clone sạch trên Linux.) (Phản tư `ndhai255`: Đức Hải đã tự viết, PR #5.)
