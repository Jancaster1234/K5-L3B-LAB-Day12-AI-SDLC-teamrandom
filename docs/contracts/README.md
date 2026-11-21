# Hợp đồng tích hợp — Phase 1 (contract v1.0)

> Người giữ: Integrator (Jancaster1234) · Đã đối chiếu PRD-0 (PO HaiVuQ, `docs/clarify.md` #1–#10); code đã khớp PRD-0 ở mọi mục (giả định còn lại: clarify #11). PRD-0 thắng nếu khác. Đổi mục nào thì báo cả nhóm trên Discord và ghi lý do (ADR ở `docs/adr/`).
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

Giỏ (`self.hold`): mảng id theo thứ tự nhặt, **cuối mảng = mới nhất** (LIFO). Chỉ thêm qua `_hold_add(kind, n, events) -> int` (lát 2 viết): PRD-0 (clarify #2): **nhận cả lượt hoặc không nhận gì** — thiếu chỗ thì phát `hold_full`, nút giữ nguyên, đàn cá ở lại và không đặt hồi chiêu; `catch` hụt không sự kiện, không hồi chiêu (clarify #8).

### `chonoi/sim/quan.py` — theo PRD-0 mục F (clarify #3)
| # | Bước | Hàm | Chủ |
|---|---|---|---|
| 1 | `phase_tick` +1; giảm đồng hồ ca, `cook_ticks_left`, `eat_ticks_left`, `patience_ticks_left` (khách `waiting`); món đã `ready` từ đầu bước: `ready_ticks` +1 | `step()` | tích hợp |
| 2 | Bếp `cooking` về 0 → `ready` (`ready_ticks = 0`), `dish_ready` | `step()` | lát 4 |
| 3 | Đi lại, rồi tối đa **một** interact: đối tượng gần nhất trong `interact_radius` (hòa: **bếp trước bàn**, rồi id nhỏ). Đối tượng được chọn không dùng được thì **bỏ lượt**. Phục vụ đúng tick kiên nhẫn về 0 hoặc hết ca vẫn hợp lệ | `_move`, `_interact` → `_use_stove` / `_use_table` | lát 4 |
| 4 | Duyệt bàn theo id: ăn xong → `paid(finished_eating)`; còn giờ mà kiên nhẫn 0 → `customer_left(patience)` + `left_reputation_delta`; **hết ca**: đang ăn → `paid(closing)`, đang chờ → `customer_left(closing)` không trừ uy tín. Khách rời: nhả giữ chỗ, hủy món của đơn trên bếp/tay. Hết ca → `quan_end` | `_resolve_tables`, `_pay`, `_leave` | lát 3 + 4 |
| 5 | Còn giờ: khách mới theo lịch `phase_tick` (`first_customer_tick`, mỗi `customer_interval_s`); hết bàn thì bỏ lượt; bàn trống id nhỏ; chọn đều theo seed trong các món nấu được; không món nào → `no_dish` | `_spawn_customers` | lát 3 |

Hàm dùng chung: `_available()` (kho − tổng giữ chỗ), `_cookable_dishes()`.
Bếp `idle` nấu cho đơn `reserved` có `(order_tick, id bàn)` nhỏ nhất, tiêu đúng phần giữ chỗ của đơn đó (`items`), đơn → `assigned`. Không có đơn `reserved` → không nấu được (bỏ lượt).

## 3. Trạng thái (snapshot) — UI chỉ đọc, không ghi

Trường chung do runner thêm: `tick, mode, phase, state, time_left_ticks, money, earned, reputation, score`.

**Gather** (đã có trong `GatherSim.snapshot`): `player{pos, vel, heading_deg, oxygen_ticks, oxygen_max_ticks, hp, hp_max, zero_oxy_ticks, invuln_ticks, catch_cd_ticks, at_surface}`, `hold`, `hold_count`, `hold_capacity`, `nodes[{id, pos, kind, ready, regrow_ticks}]`, `fish[{id, pos, kind, heading_deg}]`.

**Quan**: `player{pos}`, `stock`, `hand`, `stoves`, `tables[{id, pos, customer_id}]`, `customers`.

Bếp: `{id, pos, state: "idle"|"cooking"|"ready", dish, cook_ticks_left, ready_ticks}`; `dish` = payload món hoặc `null`.

**Payload món** (`hand`, `stove.dish`, PRD-0 mục D): `{order_id, dish_id, base_price}` hoặc `null`; `order_id` = id khách. Tay giữ tối đa `carry_limit` (1).

**Khách = một đơn** (PRD-0 mục D, clarify #4). Snapshot đúng các trường sau:
| Trường | Ý nghĩa |
|---|---|
| `id` | `"C1"`, `"C2"`… (`self.ids.new("C")`); cũng là `order_id` |
| `table_id`, `dish_id` | bàn và món của đơn |
| `state` | `"waiting"` → `"eating"` |
| `order_status` | `"reserved"` (giữ nguyên liệu) → `"assigned"` (món ở bếp/tay) → `"served"`; hoặc `"unfulfillable"` (chờ, không giữ, không món — chỉ từ scenario) |
| `order_tick` | `phase_tick` lúc đến |
| `patience_ticks_left` | đầy = `patience_s * 60` lúc đến, giảm từ bước sau |
| `eat_ticks_left` | `eat_s * 60` khi `served` |
| `reserved` | `{nguyên liệu: số}` đúng công thức khi `reserved`, `{}` ở trạng thái khác |
| `base_price`, `tip` | giá món; boa chốt khi `served`: `floor(base_price × tip_rate)` nếu `patience_ticks_left / (patience_s*60) ≥ tip_min_patience_ratio`, không thì 0 |

Scenario `customers[]` (clarify #10): thiếu `reserved` ở đơn `reserved` thì cấp theo `(order_tick, id bàn)`; `assigned` phải có đúng một món ở bếp hoặc tay khớp đơn; `eating` phải `served`, `eat_ticks_left > 0`, có `base_price`, `tip`. Mã 2 khi giữ khác công thức / quá kho, bếp và tay cùng đơn, món không khớp đơn, bếp `cooking` có timer ≤ 0.

**Lệnh UI gửi vào**: chỉ input khung `move [x, d|z]`, `interact`, `catch` (`chonoi/inputs.py`, `BUTTONS_V10`). UI không gọi hàm sim.

## 4. Sự kiện (PRD-0 mục E)

Dòng JSONL: `{"type":"event","tick","phase","name","data"}`; phát theo đúng thứ tự xử lý trong `step()`.

| Tên | Ai phát | `data` (theo PRD-0 mục E, clarify #1) |
|---|---|---|
| `dive`, `surface` | lát 1 | `{pos}` ✅ |
| `oxygen_empty` | lát 1 | `{oxygen_ticks: 0}` ✅ |
| `choke` | lát 1 | `{hp}` ✅ |
| `faint` | lát 1 | `{cause: "choke", lost: [kind theo LIFO], hp: 0}` ✅, theo sau là `gather_end` `fainted` |
| `gather` | lát 2 | `{node_id, kind, amount}` ✅ |
| `node_regrown` | khung | `{node_id}` ✅ |
| `fish_caught` | lát 2 | `{fish_id, kind, yield}` ✅ |
| `hold_full` | lát 2 | `{action: "gather"\|"catch", node_id\|fish_id, required, free}` ✅ |
| `gather_end` | khung | `{reason, inventory:{items}}` ✅ |
| `customer_arrived` | lát 3 | `{order_id, table_id, dish_id}` ✅ |
| `no_dish` | lát 3 | `{}` ✅ |
| `customer_left` | lát 3 | `{order_id, table_id, reason: "patience"\|"closing", reputation}` ✅ (`reputation` = uy tín sau khi đổi, giả định clarify #11) |
| `cook_started` | lát 4 | `{stove_id, order_id, dish_id, items, base_price}` ✅ (`items` sắp theo kind) |
| `dish_ready`, `dish_picked` | lát 4 | `{stove_id, order_id, dish_id}` ✅ |
| `served` | lát 4 | `{order_id, table_id, dish_id, patience_ticks_left, base_price, tip}` ✅ |
| `paid` | lát 4 | `{order_id, table_id, base_price, tip, amount, reason: "finished_eating"\|"closing"}` ✅ |
| `quan_end` | khung | `{reason, money, earned, shift_earned, reputation}` ✅ |

✅ = code đã khớp. Người nghe: runner (ghi JSONL), UI (`chonoi.live` hiện 6 sự kiện cuối), QA (test).

## 5. Quy ước chung
- Ngẫu nhiên chỉ qua `self.rng` (`Streams`); không `random`, không đồng hồ hệ thống.
- Duyệt/sắp thực thể bằng `sort_by_id`; id mới bằng `IdAllocator.new(prefix)`.
- Tie-break mọi lựa chọn gần nhất: khoảng cách → (bếp trước bàn) → id nhỏ.
