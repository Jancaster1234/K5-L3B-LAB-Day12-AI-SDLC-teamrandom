# Ma trận truy vết Phase 3 (Ticket-03, Test Contract v1.2)

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P3-01 — Kho cá thể qua file và trong day; kho đếm trả mã 2 | Smoke bàn giao file; day 2 Ngày; file kho đếm | [P3 #2, #3, #5](../proof/phase-3/README.md) | Đạt |
| AC-P3-02 — Id, độ tươi, hàng ươn, giữ chỗ, giá, JSONL đúng luật | 13 test `tests/test_fresh.py`; kịch bản `04-quan-fresh` | [tests/test_fresh.py](../../tests/test_fresh.py), [P3 #4](../proof/phase-3/README.md) | Đạt |
| AC-P3-03 — HUD cho thấy độ tươi / hàng ươn | Thanh tươi dưới mỗi ô giỏ, gạch chéo khi ươn; kho quán hiện tươi thấp nhất và số ươn | [chonoi/web/index.html](../../chonoi/web/index.html) | Đạt (chưa có ảnh chụp chơi thử) |
| AC-P3-04 — Test qua ngưỡng, giữ lại khi vừa ươn, chốt giá, bàn giao | `HoldDecay`, `QuanStock`, `Handoff` | [tests/test_fresh.py](../../tests/test_fresh.py) | Đạt |
| AC-P3-05 — Ghi tác động, quyết định đổi schema, thứ tự tích hợp | ADR-0001 có bảng tác động và thứ tự tích hợp; `main` giữ v1.1 chạy được tới khi gộp | [ADR-0001](../adr/0001-kho-ca-the-v12.md) | Đạt |
| AC-P3-06 — CHANGELOG breaking change, regression còn hiệu lực, test đổi có lý do | CHANGELOG mục Phase 3; 140 test; lý do đổi test trong commit `369737b` | [CHANGELOG.md](../../CHANGELOG.md), [Log 140 test](../proof/phase-3/test-output.txt) | Đạt |
| AC-P3-07 — Mở rộng (nếu làm) có test | Không làm mở rộng P3 | — | Không áp dụng |
| AC-P3-08 — Ghi chép làm rõ, nhật ký AI | `docs/ai-usage-log.md` | — | Đạt |

## Đánh giá ngắn
- Lõi v1.2 đạt trên test tự động. Tag `phase-3` gắn trễ so với mốc 2:30.
