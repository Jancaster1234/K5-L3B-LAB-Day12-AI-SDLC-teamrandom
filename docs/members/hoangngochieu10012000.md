# hoangngochieu10012000 (Hoàng Ngọc Hiệu) — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Commit 92b28dd, 9eb6636, b451805, 7e63721 là của tôi, tạo dưới tài khoản cũ hoangngochieu trước khi đổi cấu hình.
  - Phụ trách Quán lát 4 (`sim/quan`): logic bếp, bàn, trả tiền, boa (tip), uy tín (reputation), kết thúc ca.
  - Viết hợp đồng tích hợp giữa lát 3 và lát 4 (`docs/contracts/quan.md`): thứ tự gọi hàm trong `step()` và schema khách hàng.
  - Viết bộ test chuyên biệt cho lát 4 (`tests/test_quan_lat4.py`).
  - Đảm nhận vai Scrum/Release: cập nhật `docs/standup.md`, `CHANGELOG.md`.
- Tôi đã review (kèm link):
  - Review hợp đồng kho `docs/contracts/inventory.sample.json` và kế hoạch `docs/plan/phase-1.md`.
- AI sai ở đâu và tôi phát hiện thế nào:
  - Khi tương tác interact ở quán, cần chú ý quy tắc ưu tiên (khoảng cách, bếp trước bàn, id) và điều kiện hợp lệ khi cầm món/tay rỗng.
- Điều tôi học được:
  - Cách chia nhỏ lát cắt chức năng để làm việc song song không conflict thông qua hợp đồng giao tiếp rõ ràng.
