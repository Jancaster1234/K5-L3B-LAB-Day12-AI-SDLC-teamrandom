"""Buổi tối — Mở Quán. KHUNG: đi lại, chặn biên, đồng hồ, kho nạp từ file/scenario.

Nhóm viết tiếp (PRD-0 mục F, Quán):
  Lát 3 (XONG, HaiVuQ): khách đến theo lịch (_spawn_customers), chọn món nấu được (_cookable_dishes),
                        giữ chỗ nguyên liệu (_available, _release), kiên nhẫn (_tick_patience),
                        bỏ đi (customer_left), no_dish, suy ra reserved và kiểm mâu thuẫn từ scenario.
  Lát 4 (XONG, Hiệu): bếp (_tick_stoves), ăn + trả tiền + boa + uy tín (_tick_eating),
                     interact bếp/bàn (_interact: cook_started, dish_picked, served).
  Thứ tự trong step() và tên sự kiện: docs/contracts/README.md mục 2 và 4.
"""

import math

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from ..inventory import validate_items
from .ramp import ramp_velocity

TICK = 60.0


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        self._tick = 0
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = scenario.get("hand")
        self.random_customers = scenario.get("random_customers", True)
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        self.reputation = float(scenario.get("reputation", t["reputation_initial"]))
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        self.customers = self._init_customers(scenario.get("customers", []))
        for e in self.customers:
            ids.reserve(e["id"])
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def _init_customers(self, raw_customers: list) -> list:
        """Lát 3: dựng danh sách khách từ scenario, suy ra giữ chỗ (reserved) và kiểm mâu thuẫn kho."""
        patience_default = int(round(self.t["patience_s"] * TICK))
        eat_default = int(round(self.t["eat_s"] * TICK))
        in_flight = {}
        for s in self.stoves:
            if s.get("state") in ("cooking", "ready") and s.get("dish"):
                d = s["dish"]
                in_flight[d] = in_flight.get(d, 0) + 1
        if isinstance(self.hand, str) and self.hand:
            in_flight[self.hand] = in_flight.get(self.hand, 0) + 1

        avail = dict(self.stock)
        out = []
        for c in sort_by_id(raw_customers):
            cust = dict(c)
            dish = cust.get("dish_id") or cust.get("dish")
            if not isinstance(dish, str) or dish not in self.menu:
                raise BadInput(f"customers.{cust.get('id')}: dish_id không hợp lệ ({dish!r})")
            cust["dish_id"] = dish
            cust["dish"] = dish
            state = cust.get("state", "waiting")
            if state not in ("waiting", "eating", "assigned"):
                raise BadInput(f"customers.{cust.get('id')}: state không hợp lệ ({state!r})")
            cust["state"] = state
            p_left = cust.get("patience_ticks_left", cust.get("patience_ticks", patience_default))
            p_total = cust.get("patience_ticks_total", patience_default)
            e_left = cust.get("eat_ticks_left", cust.get("eat_ticks", eat_default if state == "eating" else 0))
            cust["patience_ticks_left"] = p_left
            cust["patience_ticks_total"] = p_total
            cust["eat_ticks_left"] = e_left

            if "reserved" in c:
                res = validate_items(c["reserved"])
                for k, qty in res.items():
                    if avail.get(k, 0) < qty:
                        raise BadInput(f"customers.{cust['id']}: giữ chỗ vượt quá kho ({k})")
                    avail[k] -= qty
            elif state == "assigned":
                if in_flight.get(dish, 0) <= 0:
                    raise BadInput(f"customers.{cust['id']}: đơn assigned phải khớp món đang nấu/chín/bưng")
                in_flight[dish] -= 1
                res = {}
            elif state == "waiting":
                recipe = self.menu[dish]["recipe"]
                if all(avail.get(k, 0) >= qty for k, qty in recipe.items()):
                    res = dict(recipe)
                    for k, qty in res.items():
                        avail[k] -= qty
                elif in_flight.get(dish, 0) > 0:
                    in_flight[dish] -= 1
                    res = {}
                else:
                    raise BadInput(f"customers.{cust['id']}: giữ chỗ vượt quá kho cho món {dish}")
            else:
                res = {}
            cust["reserved"] = res
            out.append(cust)
        return sort_by_id(out)

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in sort_by_id(self.stoves)],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers),
        }

    def step(self, inp):
        events = []
        self._tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        # Thứ tự chốt ở docs/contracts/README.md mục 2 (clarify #3)
        self._tick_patience(events)   # lát 3: hết kiên nhẫn -> customer_left
        self._tick_stoves(events)     # lát 4: chín -> dish_ready
        self._tick_eating(events)     # lát 4: ăn xong -> paid
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)    # lát 4: tối đa MỘT interact
        self._spawn_customers(events)  # lát 3: khách mới theo lịch, no_dish
        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        return events

    # --- lát 3: khách, giữ chỗ, kiên nhẫn (chủ: HaiVuQ) -----------------------
    def _available(self) -> dict:
        """Kho khả dụng = stock hiện tại trừ tổng reserved của khách đang chờ."""
        avail = dict(self.stock)
        for c in self.customers:
            if c.get("state") in ("waiting", "assigned"):
                for k, qty in c.get("reserved", {}).items():
                    avail[k] = avail.get(k, 0) - qty
        return {k: avail[k] for k in sorted(avail) if avail[k] > 0}

    def _release(self, customer: dict):
        """Nhả giữ chỗ nguyên liệu của khách."""
        customer["reserved"] = {}

    def _cookable_dishes(self) -> list:
        """Danh sách món trong menu (sắp theo id) đủ nguyên liệu từ kho khả dụng."""
        avail = self._available()
        out = []
        for dish_id in sorted(self.menu.keys()):
            recipe = self.menu[dish_id]["recipe"]
            if all(avail.get(k, 0) >= qty for k, qty in recipe.items()):
                out.append(dish_id)
        return out

    def _tick_patience(self, events):
        """Giảm kiên nhẫn khách waiting; về 0 -> customer_left, nhả giữ chỗ, cộng left_reputation_delta."""
        leaving = []
        for c in sort_by_id(self.customers):
            if c.get("state") in ("waiting", "assigned"):
                c["patience_ticks_left"] = max(0, int(c.get("patience_ticks_left", 0)) - 1)
                if c["patience_ticks_left"] == 0:
                    leaving.append(c)

        r_min = float(self.t.get("reputation_min", 0))
        r_max = float(self.t.get("reputation_max", 5))
        delta = float(self.t["left_reputation_delta"])
        for c in leaving:
            self._release(c)
            self.reputation = max(r_min, min(r_max, round(self.reputation + delta, 3)))
            self.customers.remove(c)
            events.append(("customer_left", {"customer_id": c["id"], "table_id": c["table_id"]}))

    def _spawn_customers(self, events):
        """Khách mới theo lịch (first_customer_tick, customer_interval_s), chọn món nấu được, giữ chỗ."""
        if not self.random_customers:
            return
        first_tick = int(self.t["first_customer_tick"])
        interval_ticks = int(round(self.t["customer_interval_s"] * TICK))
        if self._tick < first_tick:
            return
        if interval_ticks > 0 and (self._tick - first_tick) % interval_ticks != 0:
            return

        occupied = {c["table_id"] for c in self.customers}
        free_tables = [tb for tb in sort_by_id(self.tables) if tb["id"] not in occupied]
        if not free_tables:
            return

        cookable = self._cookable_dishes()
        if not cookable:
            events.append(("no_dish", {}))
            return

        table = free_tables[0]
        dish_id = self.rng.get("customer").choice(cookable)
        cid = self.ids.new("C")
        patience_ticks = int(round(self.t["patience_s"] * TICK))
        reserved = dict(self.menu[dish_id]["recipe"])
        self.customers.append({
            "id": cid,
            "table_id": table["id"],
            "dish_id": dish_id,
            "dish": dish_id,
            "state": "waiting",
            "patience_ticks_left": patience_ticks,
            "patience_ticks_total": patience_ticks,
            "reserved": reserved,
            "eat_ticks_left": 0,
        })
        events.append(("customer_arrived", {
            "customer_id": cid,
            "table_id": table["id"],
            "dish_id": dish_id,
        }))

    # --- lát 4: bếp, bàn, trả tiền, boa, uy tín (chủ: Hiệu) ---------------
    def _tick_stoves(self, events):
        """Giảm thời gian nấu; chín -> ready và phát dish_ready."""
        for s in sort_by_id(self.stoves):
            if s.get("state") == "cooking":
                s["cook_ticks_left"] = max(0, s.get("cook_ticks_left", 0) - 1)
                if s["cook_ticks_left"] == 0:
                    s["state"] = "ready"
                    s["ready_ticks"] = 0
                    events.append(("dish_ready", {"stove_id": s["id"], "dish_id": s.get("dish")}))
            elif s.get("state") == "ready":
                s["ready_ticks"] = s.get("ready_ticks", 0) + 1

    def _tick_eating(self, events):
        """Giảm thời gian ăn; ăn xong trả tiền (+ boa), cộng uy tín nếu boa, phát paid, rời bàn."""
        finished = []
        for c in sort_by_id(self.customers):
            if c.get("state") == "eating":
                c["eat_ticks_left"] = max(0, c.get("eat_ticks_left", 0) - 1)
                if c["eat_ticks_left"] == 0:
                    finished.append(c)

        for c in finished:
            dish = c["dish_id"]
            price = int(c["price"]) if "price" in c else self.menu[dish]["price"]
            if "tipped" in c:
                is_tipped = bool(c["tipped"])
            else:
                is_tipped = self._tip_ok(c)
            tip = int(c["tip"]) if "tip" in c else (int(round(price * float(self.t["tip_rate"]))) if is_tipped else 0)
            amount = price + tip
            self.money += amount
            self.earned += amount
            self.shift_earned += amount
            if is_tipped:
                self.reputation = self._clamp_rep(self.reputation + float(self.t["tip_reputation"]))
            events.append(("paid", {"customer_id": c["id"], "table_id": c["table_id"], "dish_id": dish,
                                    "price": price, "tip": tip, "amount": amount}))
            self.customers.remove(c)

    def _tip_ok(self, c) -> bool:
        p_total = c.get("patience_ticks_total", int(round(self.t["patience_s"] * TICK)))
        return p_total > 0 and c.get("patience_ticks_left", 0) / p_total >= float(self.t["tip_min_patience_ratio"])

    def _clamp_rep(self, value) -> float:
        lo, hi = float(self.t.get("reputation_min", 0)), float(self.t.get("reputation_max", 5))
        return max(lo, min(hi, round(value, 3)))

    def _in_flight(self, dish) -> int:
        """Số phần món `dish` đang nấu / đã chín trên bếp / đang bưng."""
        n = sum(1 for s in self.stoves if s.get("dish") == dish and s.get("state") in ("cooking", "ready"))
        return n + (1 if self.hand == dish else 0)

    def _dish_to_cook(self):
        """Chọn (món, khách) để nấu ở bếp idle. Không lấy nguyên liệu đang giữ chỗ cho khách khác:
        1) khách chờ (id nhỏ trước) còn giữ chỗ đủ công thức -> nấu bằng phần giữ chỗ của khách đó;
        2) khách chờ mà số món đang nấu/bưng chưa đủ -> nấu bằng kho khả dụng (lát 3 `_available`);
        3) không khách nào cần -> nấu món đầu tiên nấu được (lát 3 `_cookable_dishes`)."""
        waiting = sort_by_id([c for c in self.customers if c.get("state") in ("waiting", "assigned")])
        for c in waiting:
            recipe = self.menu[c["dish_id"]]["recipe"]
            res = c.get("reserved", {})
            if all(res.get(k, 0) >= q for k, q in recipe.items()):
                return c["dish_id"], c
        avail = self._available()
        for c in waiting:
            d = c["dish_id"]
            needed = sum(1 for o in waiting if o["dish_id"] == d)
            if self._in_flight(d) < needed and all(avail.get(k, 0) >= q for k, q in self.menu[d]["recipe"].items()):
                return d, c
        cookable = self._cookable_dishes()
        return (cookable[0], None) if cookable else (None, None)

    def _interact(self, events):
        """Tối đa MỘT interact, chọn đối tượng theo (khoảng cách, bếp trước bàn, id)."""
        radius = float(self.t["interact_radius"])
        candidates = []
        for s in self.stoves:
            d = math.dist(self.pos, s["pos"])
            if d > radius or self.hand is not None:
                continue
            if s.get("state") == "ready":
                candidates.append((d, 0, id_key(s["id"]), "stove_pick", s, None))
            elif s.get("state") == "idle":
                dish, cust = self._dish_to_cook()
                if dish is not None:
                    candidates.append((d, 0, id_key(s["id"]), "stove_cook", s, (dish, cust)))
        for tb in self.tables:
            d = math.dist(self.pos, tb["pos"])
            if d > radius or self.hand is None:
                continue
            cust = next((c for c in self.customers if c.get("table_id") == tb["id"]
                         and c.get("state") in ("waiting", "assigned")), None)
            if cust and cust["dish_id"] == self.hand:
                candidates.append((d, 1, id_key(tb["id"]), "table_serve", tb, cust))
        if not candidates:
            return

        candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        _, _, _, action, target, payload = candidates[0]
        if action == "stove_pick":
            dish = target["dish"]
            self.hand = dish
            target.update(dish=None, state="idle", cook_ticks_left=0, ready_ticks=0)
            events.append(("dish_picked", {"stove_id": target["id"], "dish_id": dish}))
        elif action == "stove_cook":
            dish, cust = payload
            for item, qty in self.menu[dish]["recipe"].items():
                self.stock[item] -= qty
                if self.stock[item] <= 0:
                    del self.stock[item]
            if cust is not None:
                self._release(cust)  # phần giữ chỗ đã được tiêu vào nồi
            target.update(state="cooking", dish=dish, ready_ticks=0,
                          cook_ticks_left=int(round(self.menu[dish]["cook_s"] * TICK)))
            events.append(("cook_started", {"stove_id": target["id"], "dish_id": dish}))
        elif action == "table_serve":
            cust = payload
            dish = self.hand
            self.hand = None
            cust["state"] = "eating"
            cust["eat_ticks_left"] = int(round(self.t["eat_s"] * TICK))
            cust["tipped"] = self._tip_ok(cust)
            events.append(("served", {"customer_id": cust["id"], "table_id": target["id"], "dish_id": dish}))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
