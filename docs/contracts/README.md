# Hợp đồng tích hợp — Phase 1 (contract v1.0)

> Người giữ: Integrator (Jancaster1234) · PO (HaiVuQ) đã đối chiếu mục 3, 4 với **PRD-0 mục D, E** (chi tiết ở `docs/clarify.md` #1–#10). Đổi mục nào thì báo cả nhóm trên Discord và ghi lý do (ADR ở `docs/adr/`).
> Số liệu luôn đọc từ `game.contract.json` (`tuning.*`), không hard-code.

## 1. File kho (PRD-0 mục G) — đã cố định bởi `chonoi/inventory.py`

```json
{"items":{"bong_sung":2,"ca_loc":1}}
```
- Khóa gốc duy nhất `items`; id nguyên liệu ∈ `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung`; giá trị nguyên ≥ 0.
- Ghi: bỏ mục bằng 0, khóa sắp theo id, JSON gọn, kết thúc `\n`, ghi nguyên tử. Mẫu: `inventory.sample.json`.
- Ghi **đúng một lần** khi có `gather_end` (runner lo). Chạm `--ticks` trước khi kết thúc → **không** ghi.
- `gather_end` lý do `docked` / `time` → kho = giỏ hiện tại; `fainted` → kho rỗng `{"items":{}}`.
- `quan` nhận kho qua `--inventory` **hoặc** `scenario.quan.stock` (cả hai → mã 2).

## 2. Thứ tự trong `step()` và ai sở hữu hàm

Mỗi lát chỉ thêm **một dòng gọi** vào `step()`; logic nằm trong hàm của mình. Không sửa hàm của lát khác — cần thì nhắn chủ hàm.

### `chonoi/sim/gather.py`
| # | Bước | Hàm | Chủ |
|---|---|---|---|
| 1 | Đồng hồ, invuln/catch cooldown, nút mọc lại (`node_regrown`) | có sẵn | khung |
| 2 | Bơi + chặn mép (giữ `prev_d = self.pos[1]` trước khi gọi) | `_move` | khung |
| 3 | dive/surface (so `prev_d` với `d` cuối bước), oxy theo `d` cuối bước, `oxygen_empty`, ngạt, `choke`; Máu 0 → `faint`, giỏ rỗng, `_finish("fainted")`, **return** | `_update_oxygen(prev_d, events) -> bool` (True = đã ngất) | lát 1 · Jancaster1234 |
| 4 | `interact`: bến trước (có sẵn), không ở bến → hái | `_harvest(events)` | lát 2 · ndhai255 |
| 5 | `catch` | `_catch(events)` | lát 2 · ndhai255 |
| 6 | Hết giờ → `_finish("time")` | có sẵn | khung |

Giỏ (`self.hold`): mảng id theo thứ tự nhặt, **cuối mảng = mới nhất** (LIFO). Chỉ thêm qua `_hold_add(kind, n, events) -> int` (lát 2 viết): thêm tối đa đến `hold_capacity`, trả số đã thêm, phát `hold_full` khi không thêm đủ. ⚠ PRD-0: thêm một phần hay từ chối cả lượt khi giỏ thiếu chỗ.

### `chonoi/sim/quan.py`
| # | Bước | Hàm | Chủ |
|---|---|---|---|
| 1 | Đồng hồ | có sẵn | khung |
| 2 | Giảm kiên nhẫn khách `waiting`; về 0 → `customer_left`, nhả giữ chỗ, uy tín `+= left_reputation_delta` | `_tick_patience(events)` | lát 3 · HaiVuQ |
| 3 | Bếp nấu: `cook_ticks_left` −1; về 0 → `ready`, `dish_ready` | `_tick_stoves(events)` | lát 4 · Hiệu |
| 4 | Khách ăn: `eat_ticks_left` −1; về 0 → `paid` (tiền + boa, uy tín), rời bàn | `_tick_eating(events)` | lát 4 |
| 5 | Đi lại + chặn biên | `_move` | khung |
| 6 | Tối đa **một** interact; chọn đối tượng gần nhất trong `interact_radius`, hòa thì **bếp trước bàn**, rồi id nhỏ | `_interact(events)` | lát 4 |
| 7 | Khách mới theo lịch (`first_customer_tick`, rồi mỗi `customer_interval_s`), chọn món nấu được, giữ chỗ; không món nào → `no_dish` | `_spawn_customers(events)` | lát 3 |
| 8 | Hết giờ → `quan_end` | có sẵn | khung |

**Chốt khi tích hợp (Integrator, clarify #3):** kiên nhẫn → bếp → ăn → đi → interact → khách mới, theo gợi ý `TODO` của khung ("giảm kiên nhẫn / nấu / ăn"). ⚠ PRD-0 mục F: nếu khác, chỉ đổi thứ tự dòng gọi, không đổi hàm.

Hàm dùng chung do lát 3 viết, lát 4 gọi: `_available() -> dict` (kho − tổng giữ chỗ), `_release(customer)` (nhả giữ chỗ), `_cookable_dishes()`.
Bếp idle chọn món (`_dish_to_cook`): (1) khách chờ còn giữ chỗ đủ công thức → nấu bằng phần giữ chỗ đó; (2) khách chờ mà số món đang nấu/bưng chưa đủ → nấu bằng kho khả dụng; (3) không ai cần → món đầu tiên nấu được. **Không bao giờ lấy nguyên liệu đang giữ cho khách khác.** Nấu: trừ `stock` theo công thức, nhả `reserved` của khách đó.

## 3. Trạng thái (snapshot — PRD-0 mục D & E) — UI chỉ đọc, không ghi

Trường chung do runner thêm: `type:"snapshot", tick, sim_tick, mode, phase, phase_tick, state ("playing"|"finished"), time_left_ticks, money, earned, reputation, score` (`score = earned + 100 * floor(reputation)`).

**Gather** (đã có trong `GatherSim.snapshot`): `player{pos, vel, heading_deg, oxygen_ticks, oxygen_max_ticks, hp, hp_max, zero_oxy_ticks, invuln_ticks, catch_cd_ticks, at_surface}`, `hold`, `hold_count`, `hold_capacity`, `nodes[{id, pos, kind, ready, regrow_ticks}]`, `fish[{id, pos, kind, heading_deg}]`.

**Quan**: `player{pos, vel}`, `stock` (gồm cả phần giữ chỗ), `hand`, `stoves[]`, `tables[{id, pos, customer_id}]` (bàn trống `customer_id: null`), `customers[]` (chỉ liệt kê khách còn ngồi).

**Payload món** (dùng cho `stove.dish` và `hand`): `{order_id, dish_id, base_price}` (với `order_id` bằng `id` khách) hoặc `null`.

**Bếp (`stoves[]`)**: `{id, pos, state: "idle"|"cooking"|"ready", dish, cook_ticks_left, ready_ticks}`. `dish` là payload món hoặc `null`; `ready_ticks` là tuổi món trên bếp (mặc định `0` khi `ready`, chỉ tăng cho món đã `ready` ở đầu bước).

**Khách (`customers[]`)** — dùng chung lát 3 (tạo) và lát 4 (phục vụ), theo PRD-0 mục D:
| Trường | Kiểu & quy ước (PRD-0 mục D) | Ai ghi |
|---|---|---|
| `id` | `"C1"`, `"C2"`… cấp bằng `self.ids.new("C")` (đồng thời là `order_id`) | lát 3 |
| `table_id` | id bàn đang ngồi | lát 3 |
| `dish_id` | khóa trong `tuning.menu` | lát 3 |
| `order_tick` | `phase_tick` lúc khách đến (mặc định `0` ở scenario) | lát 3 |
| `state` | `"waiting"` (mặc định) → `"eating"` | lát 3 tạo, lát 4 chuyển |
| `patience_ticks_left` | `patience_s * 60` lúc đến; bắt đầu giảm từ bước sau | lát 3 |
| `eat_ticks_left` | `0` khi chưa ăn; `eat_s * 60` khi `served` | lát 4 |
| `order_status` | `"reserved"` (mặc định) \| `"assigned"` (đúng 1 món ở bếp hoặc tay, `reserved` rỗng) \| `"unfulfillable"` (còn chờ, `reserved` rỗng, không có món) \| `"served"` (khi `eating`, phải có `eat_ticks_left > 0` và `base_price`, `tip` đã chốt) | lát 3 tạo, lát 4 chuyển |
| `reserved` | map `{kind: số lượng}` theo công thức (`{}` khi `assigned`/`unfulfillable`/`served`) | lát 3 giữ, lát 4 tiêu khi `cook_started` |
| `base_price` | tiền món trước boa (chốt khi bắt đầu nấu / `served`) | lát 4 |
| `tip` | `floor(base_price * tip_rate)` nếu tỷ lệ kiên nhẫn còn lại sau bước 1 ≥ `tip_min_patience_ratio`, ngược lại `0` (chốt khi `served`) | lát 4 |

`hand`: **payload món** `{order_id, dish_id, base_price}` hoặc `null` (mặc định `null`, tối đa `carry_limit`).

**Lệnh UI gửi vào**: chỉ input khung `move [x, d|z]`, `interact`, `catch` (`chonoi/inputs.py`, `BUTTONS_V10`). UI không gọi hàm sim.

## 4. Sự kiện (PRD-0 mục E)

Dòng JSONL: `{"type":"event","tick","phase","name","data"}`; phát theo đúng thứ tự xử lý trong `step()`.

| Tên | Ai phát | `data` (chốt theo PRD-0 mục E) |
|---|---|---|
| `dive`, `surface` | lát 1 | `{pos}` (sau di chuyển, chỉ khi đổi phía biên mặt nước) |
| `oxygen_empty` | lát 1 | `{oxygen_ticks: 0}` (khi vừa chạm 0) |
| `choke` | lát 1 | `{hp}` (`hp` sau trừ) |
| `faint` | lát 1 | `{cause: "choke", lost, hp: 0}` (`lost` là mảng `kind` bỏ theo LIFO), theo sau là `gather_end` `fainted` |
| `gather` | lát 2 | `{node_id, kind, amount}` |
| `node_regrown` | khung | `{node_id}` ✅ |
| `fish_caught` | lát 2 | `{fish_id, kind, yield}` (một event mỗi đàn lấy đủ `yield`) |
| `hold_full` | lát 2 | `{action: "gather"\|"catch", node_id hoặc fish_id, required, free}` |
| `gather_end` | khung | `{reason: "time"\|"docked"\|"fainted", inventory: {items}}` ✅ |
| `customer_arrived` | lát 3 | `{order_id, table_id, dish_id}` |
| `no_dish` | lát 3 | `{}` (khi có bàn mà thiếu món) |
| `cook_started` | lát 4 | `{stove_id, order_id, dish_id, items, base_price}` (`items` là mảng `kind` sắp theo `kind`) |
| `dish_ready` | lát 4 | `{stove_id, order_id, dish_id}` |
| `dish_picked` | lát 4 | `{stove_id, order_id, dish_id}` |
| `served` | lát 4 | `{order_id, table_id, dish_id, patience_ticks_left, base_price, tip}` |
| `paid` | lát 4 | `{order_id, table_id, base_price, tip, amount, reason: "finished_eating"\|"closing"}` (`base_price` là tiền món trước boa) |
| `customer_left` | lát 3/4 | `{order_id, table_id, reason: "patience"\|"closing", reputation}` |
| `quan_end` | khung | `{reason: "time", money, earned, shift_earned, reputation}` ✅ |

✅ = khung đã cố định. Người nghe: runner (ghi JSONL), UI (`chonoi.live` hiện 6 sự kiện cuối), QA (test).

Quy ước định dạng theo PRD-0 mục E:
- `items` (trong `cook_started`) và `lost` (trong `faint`) là **mảng `kind`**: `cook_started.items` sắp theo `kind`; `faint.lost` theo thứ tự bỏ (nhặt sau bỏ trước — LIFO).
- Toàn bộ sự kiện Quán dùng **`order_id`** (bằng `id` khách) và **`dish_id`**. Bản `docs/contracts/quan.md` (lát 4) đã gộp vào file này.

## 5. Quy ước chung
- Ngẫu nhiên chỉ qua `self.rng` (`Streams`); không `random`, không đồng hồ hệ thống.
- Duyệt/sắp thực thể bằng `sort_by_id`; id mới bằng `IdAllocator.new(prefix)`.
- Tie-break mọi lựa chọn gần nhất: khoảng cách → (bếp trước bàn) → id nhỏ.
