"""Vòng ngày `--mode day` (Ticket-02 mục 2, Test Contract v1.1 mục 4.3–4.5).

Ngày: day_start → day_plan → phase_start(gather) → gather … gather_end → phase_start(quan) → quan … quan_end
→ phase_start(shop) → shop … shop_end → (Ngày kế hoặc hết). Ngày chỉ hoàn tất khi Shop đóng.
Tiền, earned, uy tín và cấp nâng cấp giữ qua Ngày; oxy/Máu hồi đầy theo cấp có hiệu lực, giỏ làm mới,
kho dư bị bỏ sau Shop. Cấp vừa mua có hiệu lực từ Ngày kế (sao sang active_upgrades khi dựng Ngày mới).
Pause do runner xử lý chung cho cả ba mode.
"""

from .gather import GatherSim
from .quan import QuanSim

DAY_KEYS = {"money", "earned", "reputation", "upgrades", "day_plan"}
UPGRADE_FIELD = {"oxygen": "oxygen_max_s", "hp": "hp_max"}


def plan_ingredients(menu, dishes):
    out = {}
    for dish, n in dishes.items():
        for k, q in menu[dish]["recipe"].items():
            out[k] = out.get(k, 0) + q * n
    return {k: out[k] for k in sorted(out)}


class DaySim:
    mode = "day"

    def __init__(self, tuning, scenario, streams, ids, days=1):
        self.tuning = tuning
        self.scenario = scenario
        self.rng = streams
        self.ids = ids
        self.days = days
        d = scenario.get("day", {})
        self.money = d.get("money", 0)
        self.earned = d.get("earned", 0)
        self.reputation = float(d.get("reputation", tuning["quan"]["reputation_initial"]))
        self.upgrades = dict(d.get("upgrades", {}))
        self.active_upgrades = {}
        overrides = {e["day"]: e for e in d.get("day_plan", [])}
        self.plan = []
        for e in tuning["day_plan"]:
            o = overrides.get(e["day"], e)
            self.plan.append({"day": e["day"], "dishes": dict(o["dishes"]),
                              "ingredients": plan_ingredients(tuning["menu"], o["dishes"])})
        self.day = 0
        self.days_completed = 0
        self.done = False
        self.reason = None
        self.phase = "gather"
        self.sub = None
        self.shop = None
        self.history = []  # tổng kết từng Ngày (DayResult / Summary, soak)
        self._initial = []
        self._start_day(self._initial)

    # --- trạng thái đọc bởi runner -------------------------------------------------
    @property
    def phase_tick(self):
        return self.shop["phase_tick"] if self.phase == "shop" else self.sub.phase_tick

    @property
    def time_left_ticks(self):
        return self.shop["time_left_ticks"] if self.phase == "shop" else self.sub.time_left_ticks

    def initial_events(self):
        out, self._initial = self._initial, []
        return out

    def day_plan_now(self):
        e = self.plan[(self.day - 1) % len(self.plan)]  # soak: D1–D5 lặp ở Ngày 6–10
        return {"dishes": e["dishes"], "ingredients": e["ingredients"]}

    def snapshot(self) -> dict:
        if self.phase == "shop":
            snap = {"stock": {k: self.shop["stock"][k] for k in sorted(self.shop["stock"])}}
        else:
            snap = self.sub.snapshot()
        snap.update(day=self.day, day_plan=self.day_plan_now(), upgrades=dict(sorted(self.upgrades.items())),
                    active_upgrades=dict(sorted(self.active_upgrades.items())))
        return snap

    # --- một bước ------------------------------------------------------------------
    def step(self, inp):
        events = []
        if self.phase == "gather":
            for name, data in self.sub.step(inp):
                events.append((name, data, "gather", self.day))
            if self.sub.done:
                self._start_quan(self.sub.inventory_items(), events)
        elif self.phase == "quan":
            for name, data in self.sub.step(inp):
                events.append((name, data, "quan", self.day))
            self.money, self.earned, self.reputation = self.sub.money, self.sub.earned, self.sub.reputation
            if self.sub.done:
                self._start_shop(events)
        else:
            self._shop_step(inp, events)
        return events

    # --- dựng pha --------------------------------------------------------------------
    def _level_value(self, kind, default):
        lvl = self.active_upgrades.get(kind, 0)
        for e in self.tuning["shop"]["upgrades"][kind]:
            if e["level"] == lvl:
                return e[UPGRADE_FIELD[kind]]
        return default

    def _start_day(self, events):
        self.day += 1
        self.active_upgrades = dict(self.upgrades)
        g = self.tuning["gather"]
        self.sub = GatherSim(self.tuning, self.scenario.get("gather", {}), self.rng, self.ids, day=self.day,
                             oxygen_max_s=self._level_value("oxygen", g["oxygen_max_s"]),
                             hp_max=self._level_value("hp", g["hp_max"]))
        self.phase = "gather"
        self.shop = None
        events.append(("day_start", {}, "gather", self.day))
        events.append(("day_plan", self.day_plan_now(), "gather", self.day))
        events.append(("phase_start", {}, "gather", self.day))

    def _start_quan(self, items, events):
        tpl = {k: v for k, v in self.scenario.get("quan", {}).items() if k not in ("stock", "reputation")}
        self.sub = QuanSim(self.tuning, tpl, self.rng, self.ids, inventory=items, reputation=self.reputation,
                           money=self.money, earned=self.earned, menu_ids=list(self.day_plan_now()["dishes"]),
                           day=self.day)
        self.phase = "quan"
        events.append(("phase_start", {}, "quan", self.day))

    def _start_shop(self, events):
        q = self.sub
        self.history.append({"day": self.day, "served": q.served_count, "left": q.left_count,
                             "shift_earned": q.shift_earned, "tips": q.tips, "sold": dict(q.sold)})
        self.shop = {"phase_tick": 0, "time_left_ticks": int(self.tuning["shop"]["max_ticks"]),
                     "stock": dict(q.stock)}
        self.phase = "shop"
        events.append(("phase_start", {}, "shop", self.day))

    # --- Shop ------------------------------------------------------------------------
    def _shop_step(self, inp, events):
        sh = self.shop
        sh["phase_tick"] += 1
        sh["time_left_ticks"] = max(0, sh["time_left_ticks"] - 1)
        if inp.buy:
            self._buy(inp.buy, events)
        if inp.pressed("shop_done"):
            self._close_shop("done", events)
        elif sh["time_left_ticks"] <= 0:
            self._close_shop("time", events)

    def _buy(self, action, events):
        ups = self.tuning["shop"]["upgrades"]
        if action not in ups:
            events.append(("buy_failed", {"action": action, "reason": "unknown"}, "shop", self.day))
            return
        level = self.upgrades.get(action, 0) + 1
        entry = next((e for e in ups[action] if e["level"] == level), None)
        if entry is None:
            events.append(("buy_failed", {"action": action, "reason": "max_level"}, "shop", self.day))
            return
        if self.money < entry["price"]:
            events.append(("buy_failed", {"action": action, "reason": "funds"}, "shop", self.day))
            return
        self.money -= entry["price"]
        self.upgrades[action] = level
        events.append(("bought", {"upgrade": action, "level": level, "price": entry["price"], "money": self.money},
                       "shop", self.day))

    def _close_shop(self, reason, events):
        events.append(("shop_end", {"reason": reason}, "shop", self.day))
        self.days_completed += 1
        self.history[-1].update(earned=self.earned, reputation=self.reputation, money=self.money)
        if self.days_completed >= self.days:
            self.done = True
            self.reason = "days_complete"
            return
        self._start_day(events)
