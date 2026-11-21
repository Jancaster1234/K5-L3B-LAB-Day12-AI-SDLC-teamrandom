# Jancaster1234 (Bùi Phan Thanh Phúc) — phản tư cá nhân

- **Tôi đã làm:** trưởng nhóm, Integrator và QA lead (từ khi Tuấn nghỉ giữa Phase 1). Chia việc 5 luồng, chốt contract; lát 1 gather ([`d150448`](../../../../commit/d150448)); gộp lát 3 + 4 ([`8f91a5d`](../../../../commit/8f91a5d)); viết lại quán theo PRD-0 ([`4795ae6`](../../../../commit/4795ae6)); v1.1: cá bơi/sinh, Cá Sấu, `day`/Shop/pause, `burn`; v1.2 độ tươi ([`369737b`](../../../../commit/369737b), [ADR-0001](../adr/0001-kho-ca-the-v12.md)); `soak_cmd`, contract v1.3, cửa sổ chơi `day`; gắn tag và phát hành.
- **Tôi đã giúp / review:** gộp nhánh của cả nhóm (PR lát 2, `haivq`, `quan-lat4`, `release-v1.0.0`, `qa-lat5`, `haivq-p4-docs`), giữ commit gốc của từng người; chạy lại bằng chứng của Đức Hải và Hiệu cho tới khi khớp từng byte trước khi gộp.
- **AI sai ở đâu, phát hiện thế nào:** contract nháp đầu tiên đoán tên sự kiện vì không đọc được PRD-0, PO đối chiếu PRD-0 mới lộ ra; AI ghi một mã commit bịa trong README bằng chứng P2 và chèn nhầm một test rỗng — phát hiện khi đọc lại diff trước khi commit.
- **Bài học:** chốt contract từ nguồn gốc (PRD) trước khi chia việc; gộp nhánh sớm; bằng chứng phải chạy lại được.
