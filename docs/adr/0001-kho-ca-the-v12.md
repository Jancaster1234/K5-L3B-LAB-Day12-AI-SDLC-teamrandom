# ADR-0001: Đổi kho đếm sang kho cá thể có độ tươi (Change Request "Mùa Nước Nổi", v1.2)

- Trạng thái: chấp nhận
- Ngày, người quyết: 2026-11-21, Integrator Jancaster1234 (theo Ticket-03)

## Bối cảnh
Ticket-03 thay kho đếm `{"items": {kind: n}}` bằng kho cá thể `{"items": [{id, kind, fresh}]}`, thêm hao tươi, hàng ươn,
giữ chỗ theo id và giá theo độ tươi. Đây là breaking change ở hợp đồng tích hợp gather ↔ quán, file kho, scenario và JSONL.

## Các lựa chọn đã cân nhắc
1. Hỗ trợ hai phiên bản nội bộ (đếm và cá thể) trong lúc chuyển, bật v1.2 sau. Tốn thời gian, dễ lệch hai nhánh code.
2. Chuyển thẳng sang v1.2 trên một nhánh tích hợp, sửa đồng thời mọi module và test, gộp khi toàn bộ suite xanh. **Chọn.**
3. Lưu `fresh` dạng số thực. Bỏ: so ngưỡng 30 và `floor` giá dễ sai do làm tròn.

## Quyết định
- Chuyển thẳng (lựa chọn 2) trên nhánh `v1.2`; `main` giữ v1.1 chạy được cho tới khi gộp.
- `fresh` lưu nội bộ bằng số nguyên `u = fresh × 240` (`chonoi/fresh.py`): giỏ −2/tick, kho quán −1/tick, ươn khi `u < 7200`,
  giá `floor(giá × Σu / (n × 24000))`, đúng gợi ý "240 đơn vị mỗi điểm tươi" của Ticket-03.
- Id cá thể dùng chung `IdAllocator` (tiền tố `I`) nên tiếp tục xuyên pha và Ngày.
- Thứ tự tích hợp: (1) `fresh.py` + `inventory.py` (schema/adapter) → (2) gather → (3) quán → (4) day/scenario/manifest
  → (5) chuyển test → (6) test mới v1.2 → (7) HUD → gộp `main`.

## Hệ quả (bảng tác động)
| Module | File cần đổi | Test bị ảnh hưởng | Người phụ trách |
|---|---|---|---|
| Adapter / schema kho | `chonoi/fresh.py` (mới), `chonoi/inventory.py`, `chonoi/scenario.py`, `chonoi/contract.py`, `game.contract.json` | `test_smoke_p1` (kho, mã 2): đổi fixture sang cá thể; thêm ca kho đếm → mã 2 | Jancaster1234 |
| Lặn | `chonoi/sim/gather.py` | `test_gather_lat1/lat2/v11`: giỏ và `lost` là cá thể | Jancaster1234 |
| Quán | `chonoi/sim/quan.py` | `test_quan_lat3/lat4/prd0/integration`, `test_ext_burn`: `stock`/`reserved` theo id, giá theo tươi | Jancaster1234 |
| day | `chonoi/sim/day.py` | `test_day`: bàn giao giữ id, Ngày kế cấp id mới | Jancaster1234 |
| HUD | `chonoi/web/index.html` | `test_live` (giữ): thanh tươi + đánh dấu ươn | Jancaster1234 |
| QA | `tests/helpers.py` (`items`, `stock_items`, `count`, `fresh_price`), `tests/test_fresh.py` (mới, 13 test) | toàn suite 140 test | Jancaster1234 |

Cách cập nhật fixture: thay `"hold": ["ca_loc"]` bằng `"hold": [{"id":"I1","kind":"ca_loc","fresh":100}]`,
`"stock": {"ca_loc": 1}` bằng mảng cá thể, `reserved: {"ca_loc": 1}` bằng `reserved: ["I1"]`. File kho đếm cũ → mã 2.
