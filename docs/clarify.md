# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 P1 | Tên + `data` của từng sự kiện gather/quan (`docs/contracts/` mục 4) có đúng PRD-0 mục E không? Tên sự kiện khách đến là gì? | Giả định theo bảng trong contract; PO đối chiếu PRD-0 | PO |
| 2 | 2026-11-21 P1 | Giỏ còn ít chỗ hơn số thu được (vd. `ca_linh` cho 3 mà còn 2 chỗ): thêm một phần hay từ chối cả lượt? | Lát 2 tạm giả định: **nhận một phần** (thêm 2, phát `fish_caught` count 2 rồi `hold_full`, đàn cá biến mất); giỏ đầy hẳn → chỉ `hold_full`, nút/cá giữ nguyên. Chờ PO chốt | PO |
| 3 | 2026-11-21 P1 | Thứ tự trong bước quan: kiên nhẫn → bếp → ăn → đi → interact → khách mới có đúng PRD-0 mục F? | Giả định như contract mục 2 | PO |
| 4 | 2026-11-21 P1 | Trạng thái khách ngoài `waiting`/`eating` (vd. `assigned`)? `hand` là chuỗi id món hay object? | Giả định `waiting`/`eating`, `hand` = chuỗi | PO |
| 5 | 2026-11-21 P1 | Tiền boa làm tròn thế nào (`tip_rate * price`)? Kiên nhẫn so với `tip_min_patience_ratio` tính lúc `served` hay lúc `paid`? | Giả định tính lúc `served` | PO |
| 6 | 2026-11-21 P1 | Bước oxy vừa về 0 có tính là bước ngạt đầu tiên không? (ảnh hưởng tick `choke`: k + 59 hay k + 60) | Giả định CÓ tính: oxy về 0 ở tick k → `choke` ở tick k + `choke_interval_ticks` − 1 (`tests/test_gather_lat1.py`) | PO |
| 7 | 2026-11-21 P1 | Cùng bước vừa ngất vừa bấm `interact` trong vùng bến: `fainted` hay `docked`? | Giả định `fainted` (xét oxy/Máu trước interact, theo TODO trong khung) | PO |
| 8 | 2026-11-21 P1 | Gather: vung `catch` dưới nước mà không có cá trong `catch_radius` có tính hồi chiêu không? Hai đàn cá cách đều thì chọn theo id nhỏ? Đàn bị bắt có biến mất không? | Lát 2 tạm giả định: hụt **vẫn** hồi chiêu; hòa → id nhỏ; bắt được → đàn biến mất (sinh lại là phase sau) | PO |
