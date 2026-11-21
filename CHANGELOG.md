# Changelog

## [Phase 1] - 2026-11-21

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
- **Bằng chứng kiểm chứng Lát 4 (`docs/proof/phase-1/quan-lat4/`)**:
  - Kịch bản 1: Bếp nấu chín sau 360 tick phát `dish_ready`.
  - Kịch bản 2: Khách ăn trong 3 tick phát `paid` kèm tiền boa và tăng uy tín.
- **Tiến độ Scrum/Release**:
  - Cập nhật biên bản standup giữa phase trong `docs/standup.md`.
  - Hoàn thiện hồ sơ thành viên `TEAM.md` và `docs/members/hoangngochieu10012000.md`.
