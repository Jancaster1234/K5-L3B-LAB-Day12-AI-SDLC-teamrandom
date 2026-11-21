"""Buổi tối — Mở Quán, theo PRD-0 mục D/E/F (đối chiếu: docs/clarify.md #1, #3, #4, #5, #9, #10).

Lát 3 (HaiVuQ): khách đến theo lịch, chọn món, giữ chỗ nguyên liệu, kiên nhẫn, customer_left, no_dish.
Lát 4 (Hiệu):   bếp, interact bếp/bàn, phục vụ, trả tiền, boa, uy tín.
Tích hợp + viết lại theo PRD-0: Integrator (Jancaster1234).

Mô hình đơn: mỗi khách là MỘT đơn, `order_id` = id khách.
  state        : "waiting" | "eating"
  order_status : "reserved" (đã giữ nguyên liệu) | "assigned" (món đang ở bếp/tay)
                 | "unfulfillable" (chờ, không giữ, không có món) | "served"
Món trên bếp / trên tay là payload {order_id, dish_id, base_price} hoặc null.

Một bước (PRD-0 mục F, clarify #3):
  1. phase_tick +1; giảm đồng hồ ca, thời gian nấu, ăn, kiên nhẫn; món đã ready từ đầu bước: ready_ticks +1
  2. bếp nấu xong -> ready (ready_ticks = 0), dish_ready
  3. đi lại, rồi tối đa MỘT interact: chọn đối tượng gần nhất (bếp trước bàn, id nhỏ);
     đối tượng đó không tương tác được thì bỏ lượt
  4. duyệt bàn theo id: ăn xong -> paid(finished_eating); còn giờ mà hết kiên nhẫn -> customer_left(patience);
     hết ca: đang ăn -> paid(closing), đang chờ -> customer_left(closing, không trừ uy tín); rồi quan_end
  5. còn giờ: khách mới theo lịch
"""

import math

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from ..fresh import UNITS, Freshness, from_json, out
from .ramp import ramp_velocity

TICK = 60.0
CUSTOMER_KEYS = ("id", "table_id", "dish_id", "state", "order_status", "order_tick",
                 "patience_ticks_left", "eat_ticks_left", "reserved", "base_price", "tip")
STATES = ("waiting", "eating")
ORDER_STATUSES = ("reserved", "assigned", "unfulfillable", "served")


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None, reputation=None, money=0, earned=0,
                 menu_ids=None, day=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        self.phase_tick = 0
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # v1.2: kho là cá thể vật lý {id, kind, fresh} (gồm cả phần giữ); --inventory HOẶC scenario.stock
        self.fr = Freshness(tuning)
        raw_stock = inventory if inventory is not None else scenario.get("stock", [])
        self.stock = [from_json(e) for e in raw_stock]
        for it in self.stock:
            ids.reserve(it["id"])
        self.patience_full = int(round(t["patience_s"] * TICK))
        self.burn_ticks = None if t.get("burn_s") is None else int(round(t["burn_s"] * TICK))
        self.random_customers = scenario.get("random_customers", True)
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        self.reputation = float(reputation if reputation is not None else scenario.get("reputation", t["reputation_initial"]))
        # day: khách chọn trong các món của kế hoạch Ngày (Ticket-02 mục 2); quán chạy riêng dùng cả menu
        self.menu_ids = sorted(menu_ids) if menu_ids is not None else sorted(self.menu)
        self.day = day
        self.hand = self._payload(scenario.get("hand"), "hand")
        self.stoves = []
        for s in self._merge(t["stoves"], scenario.get("stoves", [])):
            st = dict(s, state=s.get("state", "idle"), cook_ticks_left=s.get("cook_ticks_left", 0),
                      ready_ticks=s.get("ready_ticks", 0))
            st["dish"] = self._payload(s.get("dish"), f"stoves.{s['id']}.dish")
            self.stoves.append(st)
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        self.customers = self._init_customers(scenario.get("customers", []))
        for c in self.customers:
            ids.reserve(c["id"])
        self.money = money
        self.earned = earned
        self.shift_earned = 0
        self.done = False
        self.reason = None
        # số liệu cho DayResult / Summary (không thuộc Test Contract)
        self.served_count = 0
        self.left_count = 0
        self.tips = 0
        self.sold = {}

    # --- dựng từ scenario (PRD-0 mục D, clarify #10) --------------------------------
    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def _payload(self, v, where):
        """Payload món {order_id, dish_id, base_price} hoặc None."""
        if v is None:
            return None
        if (not isinstance(v, dict) or set(v) != {"order_id", "dish_id", "base_price"}
                or not isinstance(v["order_id"], str) or v["dish_id"] not in self.menu
                or isinstance(v["base_price"], bool) or not isinstance(v["base_price"], int)):
            raise BadInput(f"{where}: phải là null hoặc {{order_id, dish_id, base_price}}")
        return {"order_id": v["order_id"], "dish_id": v["dish_id"], "base_price": v["base_price"]}

    def _init_customers(self, raw):
        out = []
        for c in raw:
            cid = c["id"]
            dish = c.get("dish_id")
            if dish not in self.menu:
                raise BadInput(f"customers.{cid}: dish_id phải thuộc menu")
            state = c.get("state", "waiting")
            if state not in STATES:
                raise BadInput(f"customers.{cid}: state phải là waiting/eating")
            status = c.get("order_status", "served" if state == "eating" else "reserved")
            if status not in ORDER_STATUSES or (state == "eating") != (status == "served"):
                raise BadInput(f"customers.{cid}: order_status {status!r} không hợp với state {state!r}")
            if state == "eating":
                if "base_price" not in c or "tip" not in c:
                    raise BadInput(f"customers.{cid}: khách eating phải có base_price và tip")
                if c.get("eat_ticks_left", 0) <= 0:
                    raise BadInput(f"customers.{cid}: khách eating phải có eat_ticks_left > 0")
            out.append({
                "id": cid, "table_id": c["table_id"], "dish_id": dish, "state": state, "order_status": status,
                "order_tick": c.get("order_tick", 0),
                "patience_ticks_left": c.get("patience_ticks_left", self.patience_full),
                "eat_ticks_left": c.get("eat_ticks_left", 0),
                "reserved": list(c["reserved"]) if "reserved" in c else None,
                "base_price": c.get("base_price", self.menu[dish]["price"]),
                "tip": c.get("tip", 0),
            })
        by_id = {c["id"]: c for c in out}

        # món đang ở bếp / tay phải thuộc đúng một đơn assigned, khớp món
        holders = {}
        for s in self.stoves:
            if s["state"] == "idle" and s["dish"] is not None:
                raise BadInput(f"stoves.{s['id']}: bếp idle không có món")
            if s["state"] in ("cooking", "ready") and s["dish"] is None:
                raise BadInput(f"stoves.{s['id']}: bếp {s['state']} phải có món")
            if s["state"] == "cooking" and s["cook_ticks_left"] <= 0:
                raise BadInput(f"stoves.{s['id']}: bếp cooking phải có cook_ticks_left > 0")
        for pl in [s["dish"] for s in self.stoves] + [self.hand]:
            if pl is None:
                continue
            c = by_id.get(pl["order_id"])
            if c is None or c["order_status"] != "assigned" or c["dish_id"] != pl["dish_id"]:
                raise BadInput(f"món của đơn {pl['order_id']} không khớp đơn assigned nào")
            holders[c["id"]] = holders.get(c["id"], 0) + 1
        for c in out:
            if c["order_status"] == "assigned" and holders.get(c["id"], 0) != 1:
                raise BadInput(f"customers.{c['id']}: đơn assigned phải có đúng một món ở bếp hoặc tay")
            if c["order_status"] != "reserved":
                if c["reserved"]:
                    raise BadInput(f"customers.{c['id']}: đơn {c['order_status']} không giữ nguyên liệu")
                c["reserved"] = []

        # v1.2: giữ theo id — phần giữ trỏ tới cá thể chưa ươn trong kho, đủ công thức, không dùng chung.
        # Đơn reserved thiếu `reserved` được cấp theo (order_tick, id bàn), lấy tươi nhất rồi id nhỏ.
        by_id = {it["id"]: it for it in self.stock}
        taken = set()
        pending = []
        for c in out:
            if c["order_status"] != "reserved":
                continue
            if c["reserved"] is None:
                pending.append(c)
                continue
            recipe = self.menu[c["dish_id"]]["recipe"]
            counts = {}
            for iid in c["reserved"]:
                it = by_id.get(iid)
                if it is None or iid in taken or self.fr.spoiled(it):
                    raise BadInput(f"customers.{c['id']}: reserved {iid} không có trong kho, đã ươn hoặc bị giữ chung")
                taken.add(iid)
                counts[it["kind"]] = counts.get(it["kind"], 0) + 1
            if counts != recipe:
                raise BadInput(f"customers.{c['id']}: reserved phải đúng công thức món")
        for c in sorted(pending, key=lambda c: (c["order_tick"], id_key(c["table_id"]))):
            picked = self._pick(self.menu[c["dish_id"]]["recipe"], taken)
            if picked is None:
                raise BadInput(f"customers.{c['id']}: không đủ kho để giữ chỗ")
            taken.update(picked)
            c["reserved"] = picked
        return sort_by_id(out)

    def _pick(self, recipe, taken):
        """Mỗi loại trong công thức lấy các cá thể khả dụng (chưa ươn, chưa bị giữ) tươi nhất, hòa theo id."""
        picked = []
        for kind in sorted(recipe):
            cands = sorted((it for it in self.stock if it["kind"] == kind and it["id"] not in taken
                            and not self.fr.spoiled(it)), key=lambda it: (-it["u"], id_key(it["id"])))
            if len(cands) < recipe[kind]:
                return None
            picked += [it["id"] for it in cands[:recipe[kind]]]
        return sorted(picked, key=id_key)

    def _reserved_ids(self):
        return {iid for c in self.customers for iid in c["reserved"]}

    # --- giao diện cho runner -------------------------------------------------------
    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos, "vel": self.vel},
            "stock": [out(it) for it in sort_by_id(self.stock)],
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in sort_by_id(self.stoves)],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": [{k: c[k] for k in CUSTOMER_KEYS} for c in sort_by_id(self.customers)],
        }

    def step(self, inp):
        events = []
        # 1. đồng hồ và bộ đếm
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        for s in self.stoves:
            if s["state"] == "cooking":
                s["cook_ticks_left"] = max(0, s["cook_ticks_left"] - 1)
            elif s["state"] == "ready":
                s["ready_ticks"] += 1
        for c in self.customers:
            if c["state"] == "eating":
                c["eat_ticks_left"] = max(0, c["eat_ticks_left"] - 1)
            else:
                c["patience_ticks_left"] = max(0, c["patience_ticks_left"] - 1)
        # 1b. v1.2: kho thô hao tươi (kể cả hàng đang giữ), phát hết spoiled theo id rồi mới xử lý giữ chỗ bị ươn
        newly = set(self.fr.decay(self.stock, self.fr.quan_dec, "stock", events, sort_by_id))
        if newly:
            hit = [c for c in self.customers if c["order_status"] == "reserved" and newly & set(c["reserved"])]
            for c in sorted(hit, key=lambda c: (c["order_tick"], id_key(c["table_id"]))):
                c["reserved"] = []  # nhả toàn bộ phần giữ, thử giữ lại đúng một lần
                picked = self._pick(self.menu[c["dish_id"]]["recipe"], self._reserved_ids())
                if picked is None:
                    c["order_status"] = "unfulfillable"
                else:
                    c["reserved"] = picked
        # 2. bếp nấu xong; mở rộng burn: món chín quá burn_s thì cháy (xét theo id bếp, trước di chuyển)
        for s in sort_by_id(self.stoves):
            if s["state"] == "cooking" and s["cook_ticks_left"] == 0:
                s["state"] = "ready"
                s["ready_ticks"] = 0
                events.append(("dish_ready", {"stove_id": s["id"], "order_id": s["dish"]["order_id"],
                                              "dish_id": s["dish"]["dish_id"]}))
            elif s["state"] == "ready" and self.burn_ticks is not None and s["ready_ticks"] > self.burn_ticks:
                self._burn(s, events)
        # 3. đi lại + tối đa một interact
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)
        # 4. bàn theo id; hết ca thì dọn rồi quan_end
        closing = self.time_left_ticks <= 0
        self._resolve_tables(events, closing)
        if closing:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
            return events
        # 5. khách mới
        self._spawn_customers(events)
        return events

    # --- lát 3: kho khả dụng, khách mới (HaiVuQ) ------------------------------------
    def _available(self) -> dict:
        """Kho khả dụng theo loại = cá thể chưa ươn, chưa bị giữ (tồn vật lý trừ phần giữ)."""
        taken = self._reserved_ids()
        avail = {}
        for it in self.stock:
            if it["id"] not in taken and not self.fr.spoiled(it):
                avail[it["kind"]] = avail.get(it["kind"], 0) + 1
        return {k: avail[k] for k in sorted(avail)}

    def _cookable_dishes(self) -> list:
        avail = self._available()
        return [d for d in self.menu_ids
                if all(avail.get(k, 0) >= q for k, q in self.menu[d]["recipe"].items())]

    def _spawn_customers(self, events):
        if not self.random_customers:
            return
        first = int(self.t["first_customer_tick"])
        interval = int(round(self.t["customer_interval_s"] * TICK))
        if self.phase_tick < first or (interval > 0 and (self.phase_tick - first) % interval != 0):
            return
        occupied = {c["table_id"] for c in self.customers}
        free = [tb for tb in sort_by_id(self.tables) if tb["id"] not in occupied]
        if not free:
            return  # hết bàn: bỏ lượt
        cookable = self._cookable_dishes()
        if not cookable:
            events.append(("no_dish", {}))
            return
        table = free[0]
        dish = self.rng.get("customer").choice(cookable)
        cid = self.ids.new("C")
        self.customers.append({
            "id": cid, "table_id": table["id"], "dish_id": dish, "state": "waiting",
            "order_status": "reserved", "order_tick": self.phase_tick,
            "patience_ticks_left": self.patience_full, "eat_ticks_left": 0,
            "reserved": self._pick(self.menu[dish]["recipe"], self._reserved_ids()),
            "base_price": self.menu[dish]["price"], "tip": 0,
        })
        events.append(("customer_arrived", {"order_id": cid, "table_id": table["id"], "dish_id": dish}))

    # --- lát 4: interact bếp/bàn, phục vụ, trả tiền (Hiệu) -------------------------
    def _interact(self, events):
        """Chọn MỘT đối tượng gần nhất trong interact_radius theo (khoảng cách, bếp trước bàn, id).
        Đối tượng được chọn không tương tác được thì bỏ lượt (không thử đối tượng khác)."""
        radius = float(self.t["interact_radius"])
        cands = []
        for s in self.stoves:
            d = math.dist(self.pos, s["pos"])
            if d <= radius:
                cands.append((d, 0, id_key(s["id"]), s))
        for tb in self.tables:
            d = math.dist(self.pos, tb["pos"])
            if d <= radius:
                cands.append((d, 1, id_key(tb["id"]), tb))
        if not cands:
            return
        _, kind, _, target = min(cands, key=lambda x: x[:3])
        if kind == 0:
            self._use_stove(target, events)
        else:
            self._use_table(target, events)

    def _use_stove(self, s, events):
        if s["state"] == "ready" and self.hand is None:
            self.hand = s["dish"]
            s.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
            events.append(("dish_picked", {"stove_id": s["id"], "order_id": self.hand["order_id"],
                                           "dish_id": self.hand["dish_id"]}))
            return
        if s["state"] != "idle":
            return
        orders = [c for c in self.customers if c["order_status"] == "reserved"]
        if not orders:
            return
        c = min(orders, key=lambda c: (c["order_tick"], id_key(c["table_id"])))
        # v1.2: tiêu đúng các id đang giữ, chốt base_price = floor(giá niêm yết × trung bình fresh / 100)
        ids_used = set(c["reserved"])
        used = [it for it in self.stock if it["id"] in ids_used]
        self.stock = [it for it in self.stock if it["id"] not in ids_used]
        price = self.menu[c["dish_id"]]["price"]
        c["base_price"] = (price * sum(it["u"] for it in used)) // (len(used) * 100 * UNITS) if used else price
        items = [out(it) for it in sorted(used, key=lambda it: (it["kind"], id_key(it["id"])))]
        c["reserved"] = []
        c["order_status"] = "assigned"
        s.update(state="cooking", ready_ticks=0, cook_ticks_left=int(round(self.menu[c["dish_id"]]["cook_s"] * TICK)),
                 dish={"order_id": c["id"], "dish_id": c["dish_id"], "base_price": c["base_price"]})
        events.append(("cook_started", {"stove_id": s["id"], "order_id": c["id"], "dish_id": c["dish_id"],
                                        "items": items, "base_price": c["base_price"]}))

    def _use_table(self, tb, events):
        c = next((c for c in self.customers if c["table_id"] == tb["id"]), None)
        if self.hand is None or c is None or c["state"] != "waiting" or self.hand["order_id"] != c["id"]:
            return
        ratio = c["patience_ticks_left"] / self.patience_full if self.patience_full else 0
        tip = math.floor(c["base_price"] * float(self.t["tip_rate"]) + 1e-9) \
            if ratio >= float(self.t["tip_min_patience_ratio"]) else 0
        c.update(state="eating", order_status="served", tip=tip,
                 eat_ticks_left=int(round(self.t["eat_s"] * TICK)))
        self.hand = None
        events.append(("served", {"order_id": c["id"], "table_id": tb["id"], "dish_id": c["dish_id"],
                                  "patience_ticks_left": c["patience_ticks_left"],
                                  "base_price": c["base_price"], "tip": tip}))

    def _resolve_tables(self, events, closing):
        by_table = {c["table_id"]: c for c in self.customers}
        for tb in sort_by_id(self.tables):
            c = by_table.get(tb["id"])
            if c is None:
                continue
            if c["state"] == "eating":
                if c["eat_ticks_left"] == 0:
                    self._pay(c, "finished_eating", events)
                elif closing:
                    self._pay(c, "closing", events)
            elif closing:
                self._leave(c, "closing", events)
            elif c["patience_ticks_left"] == 0:
                self._leave(c, "patience", events)

    def _pay(self, c, reason, events):
        amount = c["base_price"] + c["tip"]
        self.money += amount
        self.earned += amount
        self.shift_earned += amount
        self.served_count += 1
        self.tips += c["tip"]
        self.sold[c["dish_id"]] = self.sold.get(c["dish_id"], 0) + 1
        if c["tip"] > 0:
            self.reputation = self._clamp_rep(self.reputation + float(self.t["tip_reputation"]))
        self.customers.remove(c)
        events.append(("paid", {"order_id": c["id"], "table_id": c["table_id"], "base_price": c["base_price"],
                                "tip": c["tip"], "amount": amount, "reason": reason}))

    def _leave(self, c, reason, events):
        self.left_count += 1
        if reason == "patience":
            self.reputation = self._clamp_rep(self.reputation + float(self.t["left_reputation_delta"]))
        c["reserved"] = []  # nhả phần giữ
        for s in self.stoves:  # hủy món của đơn trên bếp
            if s["dish"] is not None and s["dish"]["order_id"] == c["id"]:
                s.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
        if self.hand is not None and self.hand["order_id"] == c["id"]:
            self.hand = None
        self.customers.remove(c)
        events.append(("customer_left", {"order_id": c["id"], "table_id": c["table_id"], "reason": reason,
                                         "reputation": self.reputation}))

    def _burn(self, s, events):
        """Mở rộng burn (Ticket-02 mục 3): bỏ món, nguyên liệu mất, bếp rảnh ngay; thử giữ lại ngay cho đơn —
        đủ thì reserved, thiếu thì unfulfillable (khách tiếp tục chờ tới hết kiên nhẫn). Đúng burn_s vẫn bưng được."""
        pl = s["dish"]
        s.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
        c = next((c for c in self.customers if c["id"] == pl["order_id"]), None)
        status = None
        if c is not None:
            picked = self._pick(self.menu[c["dish_id"]]["recipe"], self._reserved_ids())
            if picked is not None:
                c.update(order_status="reserved", reserved=picked)
            else:
                c.update(order_status="unfulfillable", reserved=[])
            status = c["order_status"]
        events.append(("dish_burnt", {"stove_id": s["id"], "order_id": pl["order_id"], "dish_id": pl["dish_id"],
                                      "order_status": status}))

    def _clamp_rep(self, value) -> float:
        lo, hi = float(self.t.get("reputation_min", 0)), float(self.t.get("reputation_max", 5))
        return max(lo, min(hi, round(value, 3)))

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
