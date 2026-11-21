"""Buổi tối — Mở Quán. KHUNG: đi lại, chặn biên, đồng hồ, kho nạp từ file/scenario.

Nhóm viết tiếp (PRD-0 mục F, Quán):
  TODO(nhóm, lát 3): khách đến theo lịch, chọn món nấu được, giữ chỗ nguyên liệu, kiên nhẫn,
                     bỏ đi (customer_left), no_dish, vòng đời khách.
  TODO(nhóm, lát 4): interact tại bếp/bàn (cook_started, dish_ready, dish_picked, served),
                     ăn xong trả tiền (paid), boa, uy tín, hết ca (quan_end).
"""

import math

from ..ids import id_key, sort_by_id
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
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = scenario.get("hand")
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        self.reputation = float(scenario.get("reputation", t["reputation_initial"]))
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        # Khách dựng sẵn từ scenario (customers[]) và suy ra giữ chỗ (reserved).
        patience_default = int(round(t.get("patience_s", 60) * TICK))
        eat_default = int(round(t.get("eat_s", 10) * TICK))
        self.customers = []
        for c in scenario.get("customers", []):
            cust = dict(c)
            cust.setdefault("reserved", {})
            dish = cust.get("dish_id") or cust.get("dish")
            if dish:
                cust["dish_id"] = dish
                cust["dish"] = dish
            cust.setdefault("state", "waiting")
            cust.setdefault("patience_ticks_left", cust.get("patience_ticks", patience_default))
            cust.setdefault("patience_ticks_total", cust.get("patience_ticks_left", patience_default))
            cust.setdefault("eat_ticks_left", cust.get("eat_ticks", eat_default if cust.get("state") == "eating" else 0))
            self.customers.append(cust)
            ids.reserve(cust["id"])
        self.money = int(scenario.get("money", 0))
        self.earned = int(scenario.get("earned", 0))
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                from ..errors import BadInput
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

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
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        # 1. Bếp: nấu xong chuyển ready (dish_ready)
        self._tick_stoves(events)
        # 2. Khách kiên nhẫn (Lát 3)
        self._tick_patience(events)
        # 3. Khách ăn: ăn xong trả tiền, boa, uy tín (paid)
        self._tick_eating(events)
        # 4. Di chuyển
        self._move(inp)
        # 5. Tương tác: bếp/bàn (cook_started, dish_picked, served)
        if inp.pressed("interact"):
            self._interact(events)
        # 6. Khách mới theo lịch (Lát 3)
        self._spawn_customers(events)
        # 7. Hết ca
        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        return events

    def _tick_stoves(self, events):
        """Lát 4: giảm thời gian nấu của bếp; chín -> ready và phát dish_ready."""
        for s in sort_by_id(self.stoves):
            if s.get("state") == "cooking":
                s["cook_ticks_left"] = max(0, s.get("cook_ticks_left", 0) - 1)
                if s["cook_ticks_left"] == 0:
                    s["state"] = "ready"
                    s["ready_ticks"] = 0
                    events.append(("dish_ready", {"stove_id": s["id"], "dish": s.get("dish")}))
            elif s.get("state") == "ready":
                s["ready_ticks"] = s.get("ready_ticks", 0) + 1

    def _tick_patience(self, events):
        """TODO(nhóm, lát 3): khách kiên nhẫn, customer_left."""
        pass

    def _tick_eating(self, events):
        """Lát 4: giảm thời gian ăn; ăn xong trả tiền, tính tip, cộng uy tín, phát paid."""
        finished = []
        for c in sort_by_id(self.customers):
            if c.get("state") == "eating":
                c["eat_ticks_left"] = max(0, c.get("eat_ticks_left", 0) - 1)
                if c["eat_ticks_left"] == 0:
                    finished.append(c)

        for c in finished:
            dish = c.get("dish_id") or c.get("dish")
            price = self.menu[dish]["price"] if dish in self.menu else int(c.get("price", 0))
            if "tipped" in c:
                is_tipped = bool(c["tipped"])
            else:
                p_left = c.get("patience_ticks_left", c.get("patience_ticks", 0))
                p_total = c.get("patience_ticks_total", int(round(self.t["patience_s"] * TICK)))
                is_tipped = (p_total > 0 and (p_left / p_total) >= float(self.t["tip_min_patience_ratio"]))
            tip = int(round(price * float(self.t["tip_rate"]))) if is_tipped else 0
            if "tip" in c:
                tip = int(c["tip"])
            amount = price + tip
            self.money += amount
            self.earned += amount
            self.shift_earned += amount
            if is_tipped:
                self.reputation = min(
                    float(self.t["reputation_max"]),
                    round(self.reputation + float(self.t["tip_reputation"]), 3),
                )
            events.append((
                "paid",
                {
                    "customer_id": c["id"],
                    "table_id": c["table_id"],
                    "dish": dish,
                    "price": price,
                    "tip": tip,
                    "amount": amount,
                },
            ))
            self.customers.remove(c)

    def _can_cook(self, dish: str) -> bool:
        if dish not in self.menu:
            return False
        recipe = self.menu[dish]["recipe"]
        for item, qty in recipe.items():
            if self.stock.get(item, 0) < qty:
                return False
        return True

    def _dish_to_cook(self):
        """Tìm món phù hợp nhất để nấu trên bếp idle."""
        waiting = sort_by_id([c for c in self.customers if c.get("state") == "waiting"])
        # Ưu tiên khách đang chờ mà món chưa có trên bếp hoặc trong tay
        for c in waiting:
            d = c.get("dish_id") or c.get("dish")
            if d and self._can_cook(d):
                cooking_or_ready = sum(1 for s in self.stoves if s.get("dish") == d and s.get("state") in ("cooking", "ready"))
                carrying = 1 if self.hand == d else 0
                needed = sum(1 for other in waiting if (other.get("dish_id") or other.get("dish")) == d)
                if cooking_or_ready + carrying < needed:
                    return d, c
        # Nếu đã có in-flight nhưng vẫn còn khách chờ nấu được
        for c in waiting:
            d = c.get("dish_id") or c.get("dish")
            if d and self._can_cook(d):
                return d, c
        # Nếu không có khách chờ, nấu món đầu tiên theo bảng menu mà kho đủ nguyên liệu
        for d in sorted(self.menu.keys()):
            if self._can_cook(d):
                return d, None
        return None, None

    def _interact(self, events):
        """Lát 4: tối đa MỘT interact, chọn đối tượng theo (khoảng cách, bếp trước bàn, id)."""
        radius = float(self.t["interact_radius"])
        candidates = []

        # 1. Bếp trong bán kính
        for s in self.stoves:
            d = math.dist(self.pos, s["pos"])
            if d <= radius:
                if s.get("state") == "ready" and self.hand is None:
                    candidates.append((d, 0, id_key(s["id"]), "stove_pick", s, None))
                elif s.get("state") == "idle" and self.hand is None:
                    dish, cust = self._dish_to_cook()
                    if dish is not None:
                        candidates.append((d, 0, id_key(s["id"]), "stove_cook", s, (dish, cust)))

        # 2. Bàn trong bán kính
        for tb in self.tables:
            d = math.dist(self.pos, tb["pos"])
            if d <= radius and self.hand is not None:
                cust = next((c for c in self.customers if c.get("table_id") == tb["id"] and c.get("state") == "waiting"), None)
                if cust and (cust.get("dish_id") == self.hand or cust.get("dish") == self.hand):
                    candidates.append((d, 1, id_key(tb["id"]), "table_serve", tb, cust))

        if not candidates:
            return

        candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        _, _, _, action, target, payload = candidates[0]

        if action == "stove_pick":
            dish = target["dish"]
            self.hand = dish
            target["dish"] = None
            target["state"] = "idle"
            target["cook_ticks_left"] = 0
            target["ready_ticks"] = 0
            events.append(("dish_picked", {"stove_id": target["id"], "dish": dish}))

        elif action == "stove_cook":
            dish, cust = payload
            recipe = self.menu[dish]["recipe"]
            for item, qty in recipe.items():
                self.stock[item] -= qty
                if self.stock[item] <= 0:
                    del self.stock[item]
            if cust is not None and "reserved" in cust:
                cust["reserved"] = {}
            cook_ticks = int(round(self.menu[dish]["cook_s"] * TICK))
            target["state"] = "cooking"
            target["dish"] = dish
            target["cook_ticks_left"] = cook_ticks
            target["ready_ticks"] = 0
            events.append(("cook_started", {"stove_id": target["id"], "dish": dish}))

        elif action == "table_serve":
            dish = self.hand
            self.hand = None
            cust = payload
            cust["state"] = "eating"
            cust["eat_ticks_left"] = int(round(self.t["eat_s"] * TICK))
            p_left = cust.get("patience_ticks_left", cust.get("patience_ticks", int(round(self.t["patience_s"] * TICK))))
            p_total = cust.get("patience_ticks_total", int(round(self.t["patience_s"] * TICK)))
            cust["tipped"] = (p_total > 0 and (p_left / p_total) >= float(self.t["tip_min_patience_ratio"]))
            events.append(("served", {"table_id": target["id"], "customer_id": cust["id"], "dish": dish}))

    def _spawn_customers(self, events):
        """TODO(nhóm, lát 3): khách đến theo lịch, chọn món, no_dish."""
        pass

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
