# Hợp đồng tích hợp Quán (Lát 3 & Lát 4)

Tài liệu này chốt 2 điểm nối giữa Lát 3 (`sim/quan`: khách, giữ chỗ, kiên nhẫn) và Lát 4 (`sim/quan`: bếp, bàn, phục vụ, thanh toán, boa, uy tín).

---

## 1. Thứ tự gọi các hàm trong `QuanSim.step(inp)`

Trong mỗi tick mô phỏng, phương thức `step()` thực thi theo đúng thứ tự sau:

1. **Đồng hồ ca:**
   ```python
   self.time_left_ticks = max(0, self.time_left_ticks - 1)
   ```
2. **Cập nhật bếp (Lát 4):** `self._tick_stoves(events)`
   - Giảm `cook_ticks_left` của các bếp đang ở trạng thái `cooking`.
   - Khi `cook_ticks_left == 0`: chuyển sang trạng thái `ready`, phát sự kiện `dish_ready`.
3. **Cập nhật kiên nhẫn khách hàng (Lát 3):** `self._tick_patience(events)`
   - Giảm `patience_ticks_left` của các khách hàng ở trạng thái `waiting`.
   - Nếu `patience_ticks_left == 0`: khách bỏ đi, trừ uy tín `left_reputation_delta`, giải phóng `reserved`, phát sự kiện `customer_left`, rời bàn.
4. **Cập nhật khách ăn (Lát 4):** `self._tick_eating(events)`
   - Giảm `eat_ticks_left` của các khách hàng ở trạng thái `eating`.
   - Khi `eat_ticks_left == 0`: khách hoàn tất bữa ăn, thanh toán `price` (+ `tip` nếu được boa), tăng `money`, `earned`, `shift_earned`, tăng `reputation` (+ `tip_reputation` nếu có), phát sự kiện `paid`, khách rời bàn.
5. **Di chuyển người chơi:** `self._move(inp)`
   - Cập nhật vị trí, vận tốc và chặn biên quán.
6. **Tương tác của người chơi (Lát 4):**
   ```python
   if inp.pressed("interact"):
       self._interact(events)
   ```
   - Lọc các đối tượng hợp lệ trong bán kính `interact_radius`.
   - Chọn tối đa 1 hành động theo thứ tự ưu tiên: `(khoảng cách gần nhất, bếp trước bàn, id nhỏ hơn)`.
   - **Tương tác bếp:**
     - Bếp `ready` & tay rỗng: bốc món (`dish_picked`), bếp chuyển về `idle`, `self.hand = dish`.
     - Bếp `idle` & tay rỗng & có món nấu được: bắt đầu nấu (`cook_started`), trừ nguyên liệu kho, giải phóng reserved tương ứng, bếp chuyển về `cooking`.
   - **Tương tác bàn:**
     - Đang cầm món phù hợp với món khách tại bàn đang chờ (`waiting`): phục vụ (`served`), `self.hand = None`, khách chuyển sang `eating`, đặt `eat_ticks_left`, xác định đủ điều kiện boa (`patience_ratio >= tip_min_patience_ratio`).
7. **Sinh khách mới theo lịch (Lát 3):** `self._spawn_customers(events)`
   - Kiểm tra tick đến lượt (`first_customer_tick`, sau đó theo chu kỳ `customer_interval_s * 60`).
   - Tìm bàn trống và món nấu được, giữ chỗ nguyên liệu `reserved`, sinh khách `waiting`.
8. **Kiểm tra kết thúc ca:**
   - Nếu `self.time_left_ticks <= 0`: đặt `self.done = True`, `self.reason = "time"`, phát sự kiện `quan_end`.

---

## 2. Schema trường của một khách hàng (`Customer`)

Dùng chung cho Lát 3 và Lát 4 trong danh sách `self.customers`:

```json
{
  "id": "C1",
  "table_id": "T1",
  "dish_id": "ca_loc_nuong_trui",
  "dish": "ca_loc_nuong_trui",
  "state": "waiting",
  "patience_ticks_left": 3600,
  "patience_ticks_total": 3600,
  "reserved": {
    "ca_loc": 1
  },
  "eat_ticks_left": 0,
  "tipped": false
}
```

### Giải thích các trường:
| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | `str` | Mã định danh khách hàng duy nhất (ví dụ: `"C1"`). |
| `table_id` | `str` | Mã bàn khách đang ngồi (ví dụ: `"T1"`). |
| `dish_id` | `str` | Mã món ăn theo menu (ví dụ: `"ca_loc_nuong_trui"`). Đồng bộ cùng `dish`. |
| `dish` | `str` | Bí danh của `dish_id` để tương thích tối đa. |
| `state` | `str` | Trạng thái khách: `"waiting"` (chờ món) hoặc `"eating"` (đang ăn). |
| `patience_ticks_left` | `int` | Số tick kiên nhẫn còn lại trong khi chờ món. |
| `patience_ticks_total`| `int` | Tổng số tick kiên nhẫn lúc bắt đầu (dùng tính tỷ lệ kiên nhẫn còn lại). |
| `reserved` | `dict`| Số lượng nguyên liệu đã được giữ chỗ trong kho (`{"ca_loc": 1}`). |
| `eat_ticks_left` | `int` | Số tick ăn còn lại sau khi đã được phục vụ món. |
| `tipped` | `bool`| Đánh dấu khách có boa khi ăn xong hay không. |

---

## 3. Danh sách sự kiện Quán (Phase 1)

| Tên sự kiện | Phát sinh khi | Dữ liệu kèm theo (`data`) |
|---|---|---|
| `cook_started` | Người chơi bắt đầu nấu món tại bếp | `{"stove_id": str, "dish": str}` |
| `dish_ready` | Bếp hoàn thành thời gian nấu | `{"stove_id": str, "dish": str}` |
| `dish_picked` | Người chơi lấy món đã chín khỏi bếp | `{"stove_id": str, "dish": str}` |
| `served` | Người chơi đưa món đúng đến bàn khách | `{"table_id": str, "customer_id": str, "dish": str}` |
| `paid` | Khách ăn xong và thanh toán | `{"customer_id": str, "table_id": str, "dish": str, "price": int, "tip": int, "amount": int}` |
| `customer_left` | Khách hết kiên nhẫn bỏ về (Lát 3) | `{"customer_id": str, "table_id": str, "dish": str}` |
| `no_dish` | Không còn món nấu được cho khách (Lát 3) | `{"tick": int}` |
| `quan_end` | Kết thúc ca mở quán | `{"reason": str, "money": int, "earned": int, "shift_earned": int, "reputation": float}` |
