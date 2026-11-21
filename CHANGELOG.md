# Changelog

## [Unreleased] - Phase 1

### Added
- **Quán Lát 4 (`chonoi/sim/quan.py`)**:
  - `_tick_stoves`: bếp nấu xong chuyển trạng thái sang `ready`, phát sự kiện `dish_ready`.
  - `_tick_eating`: khách ăn xong trả tiền (`paid`), tính tiền boa (tip) khi tỷ lệ kiên nhẫn lúc phục vụ $\ge 50\%$, cập nhật uy tín (`reputation` $+0.2$), khách rời bàn.
  - `_interact`: tương tác người chơi với bếp và bàn (`cook_started`, `dish_picked`, `served`), xử lý ưu tiên tie-break (khoảng cách gần nhất, bếp trước bàn, id nhỏ hơn).
  - Kết thúc ca quán (`quan_end`) khi hết thời gian.
  - Bộ test độc lập cho Lát 4 (`tests/test_quan_lat4.py`).
- **Hợp đồng tích hợp (`docs/contracts/quan.md`)**:
  - Chốt thứ tự gọi hàm trong `QuanSim.step()`.
  - Chốt schema trường của khách hàng (`Customer`) dùng chung cho Lát 3 và 4.
- **Tiến độ Scrum/Release**:
  - Cập nhật biên bản standup giữa phase trong `docs/standup.md`.
  - Điền thông tin thành viên Hoàng Ngọc Hiếu trong `TEAM.md` và `docs/members/hoangngochieu.md`.
