"""Buổi tối — Mở Quán. KHUNG: đi lại, chặn biên, đồng hồ, kho nạp từ file/scenario.

Nhóm viết tiếp (PRD-0 mục F, Quán):
  Lát 3 (XONG, HaiVuQ): khách đến theo lịch (_spawn_customers), chọn món nấu được (_cookable_dishes),
                        giữ chỗ nguyên liệu (_available, _release), kiên nhẫn (_tick_patience),
                        bỏ đi (customer_left), no_dish, suy ra reserved và kiểm mâu thuẫn từ scenario.
  TODO(nhóm, lát 4): interact tại bếp/bàn (cook_started, dish_ready, dish_picked, served),
                     ăn xong trả tiền (paid), boa, uy tín, hết ca (quan_end).
"""

from ..errors import BadInput
from ..ids import sort_by_id
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
        # Lát 3: giảm kiên nhẫn khách waiting; hết kiên nhẫn -> customer_left, nhả giữ chỗ, trừ uy tín
        self._tick_patience(events)
        # TODO(nhóm, lát 4): _tick_stoves(events), _tick_eating(events)
        self._move(inp)
        # TODO(nhóm, lát 4): tối đa MỘT interact, chọn đối tượng theo (khoảng cách, bếp trước bàn, id).
        # Lát 3: khách mới theo lịch (first_customer_tick, customer_interval_s), no_dish.
        self._spawn_customers(events)
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
