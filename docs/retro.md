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

## Phase 2 (nhanh)
- Điều tốt:
- Điều tệ:
- 1 hành động cho Phase 3:

## Phase 4 (cuối)
- Rà lại hành động Phase 2: đã làm chưa? vì sao?
- Điều tốt / điều tệ:
- Số liệu: số commit theo người, cách đọc code của nhau, token theo người:
- Một lần AI sai và cách nhóm phát hiện:
- Nếu làm lại, đổi gì:
