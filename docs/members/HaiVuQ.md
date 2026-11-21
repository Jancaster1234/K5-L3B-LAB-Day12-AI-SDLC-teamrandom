# HaiVuQ — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm (kèm link commit):**
  - Vai PO: cập nhật danh sách thành viên (`ad712f9`), đối chiếu và chốt 10 mục trong [`docs/clarify.md`](../clarify.md), cập nhật [`docs/contracts/README.md`](../contracts/README.md), [`docs/plan/phase-1.md`](../plan/phase-1.md) và [`docs/standup.md`](../standup.md) (`100688a`).
  - Phụ trách `sim/quan` — Lát 3 (`e50cabd`): triển khai sinh khách theo lịch (`_spawn_customers`), lọc món nấu được từ kho khả dụng (`_available`, `_cookable_dishes`), giữ/nhả nguyên liệu (`reserved`, `_release`), giảm kiên nhẫn và khách bỏ về (`_tick_patience`, `customer_left`, `no_dish`), suy ra `reserved` và kiểm mâu thuẫn kho trong `chonoi/scenario.py`, kèm 12 test trong [`tests/test_quan_lat3.py`](../../tests/test_quan_lat3.py) và bằng chứng [`docs/proof/phase-1/quan-lat3/`](../proof/phase-1/quan-lat3/README.md).
- **Tôi đã review (kèm link):**
  - Đối chiếu contract và giả định của Lát 1 (`d150448`), Lát 2 (`cdf80eb`) và điểm nối khách/bếp với Lát 4 (`b451805`).
- **AI sai ở đâu và tôi phát hiện thế nào:**
  - Ban đầu nếu tính tick sinh khách dựa vào `duration_ticks - time_left_ticks` thì khi test truyền `scenario.time_left_ticks` ngắn sẽ làm lệch mốc `first_customer_tick = 120`. Tôi phát hiện khi viết test scenario ngắn và sửa sang bộ đếm bước `self._tick` nội bộ của phiên.
- **Điều tôi học được:**
  - Chốt schema thực thể (`Customer`) và thứ tự gọi hàm trong `step()` sớm giúp Lát 3 và Lát 4 làm song song, tự kiểm chứng độc lập bằng scenario mà không chặn nhau.
