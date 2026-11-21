# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 P1 | Tên + `data` của từng sự kiện gather/quan (`docs/contracts/` mục 4) có đúng PRD-0 mục E không? Tên sự kiện khách đến là gì? | Giả định theo bảng trong contract; PO đối chiếu PRD-0 | PO |
| 2 | 2026-11-21 P1 | Giỏ còn ít chỗ hơn số thu được (vd. `ca_linh` cho 3 mà còn 2 chỗ): thêm một phần hay từ chối cả lượt? | Chưa chốt | PO |
| 3 | 2026-11-21 P1 | Thứ tự trong bước quan: kiên nhẫn → bếp → ăn → đi → interact → khách mới có đúng PRD-0 mục F? | Giả định như contract mục 2 | PO |
| 4 | 2026-11-21 P1 | Trạng thái khách ngoài `waiting`/`eating` (vd. `assigned`)? `hand` là chuỗi id món hay object? | Giả định `waiting`/`eating`, `hand` = chuỗi | PO |
| 5 | 2026-11-21 P1 | Tiền boa làm tròn thế nào (`tip_rate * price`)? Kiên nhẫn so với `tip_min_patience_ratio` tính lúc `served` hay lúc `paid`? | Giả định tính lúc `served` | PO |
