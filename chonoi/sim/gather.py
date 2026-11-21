"""Buổi sáng — Lặn & Hái (`gather`). KHUNG: bơi, chặn mép, đồng hồ, cập bến, xuất kho.

Mặt cắt dòng sông nhìn NGANG: vị trí `[x, d]` (x sang phải, `d` độ sâu hướng xuống, d = 0 là mặt nước).
`move = [x, d]`: thành phần thứ hai DƯƠNG = bơi xuống. Hướng mặt là góc từ +x, dương = xuống.

Đã làm sẵn để smoke test chạy được: bơi + tăng/giảm tốc, chặn mép (d không âm), đồng hồ và hết giờ,
cập bến (`interact` trong vùng bến -> `gather_end` reason `docked`), xuất kho, snapshot đầy đủ trường gather.

Nhóm viết tiếp (đúng thứ tự một bước trong PRD mục 13.8, "Gather"):
  Lát 1 (XONG, `_update_oxygen`): bơi + oxy + biên + giỏ
      - oxy: dưới nước (d > surface_depth) trừ 1 tick/tick, mặt nước hồi oxygen_refill_per_tick, kẹp [0, max]
      - ngạt: oxy = 0 và đang dưới nước -> đếm zero_oxy_ticks, đủ choke_interval_ticks thì -1 Máu (choke)
      - Máu về 0 -> ngất (faint, gather_end reason `fainted`, mất toàn bộ giỏ, kho rỗng)
      - sự kiện dive / surface / oxygen_empty / choke / faint
      - giỏ: thứ tự nhặt (LIFO), sức chứa hold_capacity (thêm vào giỏ: `_hold_add` của lát 2)
  XONG (lát 2, ndhai255): hái + bắt cá + cập bến + kho — `_harvest`, `_catch`, `_hold_add`
      - hái nút ở mặt nước (gather, hold_full), nút mọc lại (node_regrown đã có phần đếm ngược)
      - bắt đàn cá bằng `catch` (fish_caught, hold_full, hồi chiêu catch_cd_ticks, chỉ khi dưới nước)
      - cập bến xét TRƯỚC hái (đã có); ghi kho đúng một lần do runner lo
      - giả định chờ PO: docs/clarify.md #2 (giỏ thiếu chỗ -> nhận một phần), #8 (vung hụt vẫn hồi chiêu)
Các tính năng của phase sau chưa nằm trong khung này.
"""

import math

from ..ids import id_key, sort_by_id
from ..fresh import Freshness, from_json, make, out
from .ramp import ramp_velocity

TICK = 60.0
AXES = ("x", "d")
MONSTER_KEYS = ("id", "kind", "pos", "waypoints", "target_idx", "state", "state_ticks_left", "recoil_dir")


class GatherSim:
    mode = "gather"
    phase = "gather"

    def __init__(self, tuning, scenario, streams, ids, day=1, oxygen_max_s=None, hp_max=None, renumber_hold=False):
        t = tuning["gather"]
        self.t = t
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        self.heading = float(p.get("heading_deg", t["start_heading_deg"]))
        self.phase_tick = 0
        self.day = day
        self.oxygen_max = int(round((oxygen_max_s if oxygen_max_s is not None else t["oxygen_max_s"]) * TICK))
        self.hp_max = hp_max if hp_max is not None else t["hp_max"]
        self.oxygen_ticks = p.get("oxygen_ticks", self.oxygen_max)
        self.hp = p.get("hp", self.hp_max)
        self.zero_oxy_ticks = p.get("zero_oxy_ticks", 0)
        self.invuln_ticks = p.get("invuln_ticks", 0)
        self.catch_cd_ticks = p.get("catch_cd_ticks", 0)
        # v1.2: giỏ là mảng cá thể theo thứ tự vào giỏ (cuối mảng là mới nhất). Trong day, Ngày đầu giữ id mẫu,
        # các Ngày kế cấp id mới theo thứ tự mảng với kind/fresh ban đầu (renumber_hold).
        self.fr = Freshness(tuning)
        self.hold = []
        for e in scenario.get("hold", []):
            it = from_json(e)
            if renumber_hold:
                it["id"] = ids.new("I")
            else:
                ids.reserve(it["id"])
            self.hold.append(it)
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        # nút và đàn cá: scenario THAY THẾ danh sách mặc định; random_fish=false tắt cá mặc định
        src_nodes = scenario["nodes"] if "nodes" in scenario else t["nodes"]
        self.nodes = [{"id": n["id"], "kind": n["kind"], "pos": [float(c) for c in n["pos"]],
                       "regrow_ticks": n.get("regrow_ticks", 0)} for n in src_nodes]
        # v1.1: random_fish=false tắt cá mặc định, bơi và sinh (cá fixture đứng yên);
        # khai fish khi cờ bật thì thay đàn ban đầu, vẫn bơi/sinh.
        self.random_fish = scenario.get("random_fish", True)
        if "fish" in scenario:
            src_fish = scenario["fish"]
        elif self.random_fish:
            src_fish = t["fish_initial"]
        else:
            src_fish = []
        self.fish = [{"id": f["id"], "kind": f["kind"], "pos": [float(c) for c in f["pos"]],
                      "heading_deg": float(f.get("heading_deg", 0)), "age_ticks": f.get("age_ticks", 0)}
                     for f in src_fish]
        # Thủy quái: scenario.monsters thay danh sách; bỏ mảng thì dùng bố trí đúng Ngày (from_day <= day)
        mt = t["monsters"]
        src_mon = scenario["monsters"] if "monsters" in scenario else \
            [m for m in mt["spawns"] if m.get("from_day", 1) <= day]
        self.monsters = []
        for m in src_mon:
            st = m.get("state", "patrol")
            self.monsters.append({"id": m["id"], "kind": m["kind"], "pos": [float(c) for c in m["pos"]],
                                  "waypoints": [[float(c) for c in w] for w in m["waypoints"]],
                                  "target_idx": m.get("target_idx", 1), "state": st,
                                  "state_ticks_left": m.get("state_ticks_left", 0),
                                  "recoil_dir": m.get("recoil_dir") if st == "recoil" else None})
        for coll in (self.nodes, self.fish, self.monsters):
            for e in coll:
                ids.reserve(e["id"])
        self.money = 0
        self.earned = 0
        self.reputation = tuning["quan"]["reputation_initial"]
        self.done = False
        self.reason = None

    # --- giao diện cho runner -------------------------------------------------
    def inventory_items(self) -> list:
        return [out(it) for it in sort_by_id(self.hold)]

    def snapshot(self) -> dict:
        return {
            "player": {"pos": self.pos, "vel": self.vel, "heading_deg": self.heading,
                       "oxygen_ticks": self.oxygen_ticks, "oxygen_max_ticks": self.oxygen_max,
                       "hp": self.hp, "hp_max": self.hp_max, "zero_oxy_ticks": self.zero_oxy_ticks,
                       "invuln_ticks": self.invuln_ticks, "catch_cd_ticks": self.catch_cd_ticks,
                       "at_surface": self._at_surface()},
            "hold": [out(it) for it in self.hold], "hold_count": len(self.hold),
            "hold_capacity": self.t["hold_capacity"],
            "nodes": [{"id": n["id"], "pos": n["pos"], "kind": n["kind"],
                       "ready": n["regrow_ticks"] == 0, "regrow_ticks": n["regrow_ticks"]}
                      for n in sort_by_id(self.nodes)],
            "fish": [{"id": f["id"], "pos": f["pos"], "kind": f["kind"], "heading_deg": f["heading_deg"],
                      "age_ticks": f["age_ticks"]} for f in sort_by_id(self.fish)],
            "monsters": [{k: m[k] for k in MONSTER_KEYS} for m in sort_by_id(self.monsters)],
        }

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        events = []
        # 1. đồng hồ và hàng có sẵn: giảm bộ đếm, nút mọc lại
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self.invuln_ticks = max(0, self.invuln_ticks - 1)
        self.catch_cd_ticks = max(0, self.catch_cd_ticks - 1)
        for n in sort_by_id(self.nodes):
            if n["regrow_ticks"] > 0:
                n["regrow_ticks"] -= 1
                if n["regrow_ticks"] == 0:
                    events.append(("node_regrown", {"node_id": n["id"]}))
        # v1.2: hàng có sẵn trong giỏ hao tươi ở đầu bước (hàng mới bắt/hái hao từ bước sau)
        self.fr.decay(self.hold, self.fr.gather_dec, "hold", events, sort_by_id)
        # 2. bơi + chặn mép
        prev_d = self.pos[1]
        self._move(inp)
        # lát 1: dive/surface, oxy, ngạt, Máu, ngất
        if self._update_oxygen(prev_d, events):
            return events
        # 2b. thủy quái theo id, rồi tối đa một hit (Ticket-02 mục 1.2, 4.5)
        if self._update_monsters(events):
            return events
        # 3. interact: bến trước, rồi hái
        if inp.pressed("interact"):
            if self._in_dock():
                self._finish("docked", events)
                return events
            self._harvest(events)
        # 4. bắt cá
        if inp.pressed("catch"):
            self._catch(events)
        # 5. hết giờ
        if self.time_left_ticks <= 0:
            self._finish("time", events)
            return events
        # 6. còn giờ: cá bơi rồi sinh thêm theo lịch (cá mới tham gia từ bước sau)
        if self.random_fish:
            self._fish_swim()
            self._fish_spawn(events)
        return events

    # --- v1.1: cá bơi + sinh (Ticket-02 mục 1.1) -------------------------------------
    def _fish_swim(self):
        t = self.t
        step = float(t["fish_speed"]) / TICK
        xlo, xhi = t["fish_x"]
        rng = self.rng.get("fish_turn")
        for f in sort_by_id(self.fish):
            f["age_ticks"] += 1
            if f["age_ticks"] % int(t["fish_turn_ticks"]) == 0:
                f["heading_deg"] = rng.uniform(0.0, 360.0)  # đổi hướng trước khi di chuyển
            dlo, dhi = t["fish_depths"][f["kind"]]
            h = math.radians(f["heading_deg"])
            vx, vd = math.cos(h), math.sin(h)
            nx, fx = _reflect(f["pos"][0] + vx * step, xlo, xhi)
            nd, fd = _reflect(f["pos"][1] + vd * step, dlo, dhi)
            f["pos"] = [nx, nd]
            if fx or fd:  # đảo thành phần hướng vuông góc với mép; chạm góc đảo cả hai
                f["heading_deg"] = math.degrees(math.atan2(-vd if fd else vd, -vx if fx else vx)) % 360

    def _fish_spawn(self, events):
        t = self.t
        if self.phase_tick % int(t["fish_spawn_ticks"]) != 0 or len(self.fish) >= int(t["fish_max"]):
            return
        clear = float(t["fish_spawn_clearance"])
        points = {}
        for kind in sorted(t["fish_spawn_depths"]):
            pts = [[float(x), float(d)] for x in t["fish_spawn_x"] for d in t["fish_spawn_depths"][kind]]
            pts = [q for q in pts if all(math.dist(q, f["pos"]) > clear for f in self.fish)]
            if pts:
                points[kind] = pts
        if not points:
            return  # hết điểm: bỏ lượt
        rng = self.rng.get("fish_spawn")
        kinds = sorted(points)
        weights = [float(t["fish_weights"][k]) for k in kinds]  # chuẩn hóa lại theo loài còn điểm
        r = rng.random() * sum(weights)
        kind = kinds[-1]
        for k, w in zip(kinds, weights):
            if r < w:
                kind = k
                break
            r -= w
        pos = list(rng.choice(points[kind]))
        fid = self.ids.new("F")
        self.fish.append({"id": fid, "kind": kind, "pos": pos, "heading_deg": rng.uniform(0.0, 360.0),
                          "age_ticks": 0})
        events.append(("fish_spawned", {"id": fid, "kind": kind, "pos": list(pos)}))

    # --- v1.1: thủy quái, chạm, recoil (Ticket-02 mục 1.2) -----------------------------
    def _update_monsters(self, events) -> bool:
        """Cập nhật quái theo id, rồi xét tối đa một hit. Trả True nếu người chơi ngất."""
        if not self.monsters:
            return False
        species = self.t["monsters"]["species"]
        b = self.t["bounds"]
        recovered = set()  # vừa hết recoil: xét phát hiện/chạm từ bước kế
        for m in sort_by_id(self.monsters):
            sp = species[m["kind"]]
            if m["state"] == "recoil":
                step = float(sp["recoil_dist"]) / int(sp["recoil_ticks"])
                m["pos"] = _clamp_monster([m["pos"][0] + m["recoil_dir"][0] * step,
                                           m["pos"][1] + m["recoil_dir"][1] * step], sp, b)
                m["state_ticks_left"] -= 1
                if m["state_ticks_left"] <= 0:
                    m.update(state="patrol", state_ticks_left=0, recoil_dir=None)
                    recovered.add(m["id"])
                continue
            deep = self.pos[1] >= sp["depths"][0]
            dist = math.dist(self.pos, m["pos"])
            if m["state"] == "patrol" and deep and dist <= sp["detect_radius"]:
                m["state"] = "chase"
            elif m["state"] == "chase" and (dist > sp["exit_radius"] or not deep):
                m["state"] = "patrol"
            if m["state"] == "chase":
                m["pos"] = _clamp_monster(_toward(m["pos"], self.pos, float(sp["chase_speed"]) / TICK), sp, b)
            else:
                target = m["waypoints"][m["target_idx"]]
                step = float(sp["patrol_speed"]) / TICK
                if math.dist(m["pos"], target) <= step:  # đến waypoint: đổi mục tiêu cho bước sau
                    m["pos"] = _clamp_monster(list(target), sp, b)
                    m["target_idx"] = 1 - m["target_idx"]
                else:
                    m["pos"] = _clamp_monster(_toward(m["pos"], target, step), sp, b)
        if self.invuln_ticks > 0:
            return False
        cands = []
        for m in self.monsters:
            sp = species[m["kind"]]
            if m["state"] not in ("patrol", "chase") or m["id"] in recovered:
                continue
            d = math.dist(self.pos, m["pos"])
            if d <= sp["hit_radius"] and self.pos[1] >= sp["depths"][0]:
                cands.append((d, id_key(m["id"]), m))
        if not cands:
            return False
        m = min(cands, key=lambda c: c[:2])[2]
        sp = species[m["kind"]]
        self.hp = max(0, self.hp - 1)
        n_lost = math.floor(len(self.hold) * float(self.t["monsters"]["loss_ratio"]))
        lost = [out(self.hold.pop()) for _ in range(n_lost)]  # LIFO: nhặt sau mất trước
        self.invuln_ticks = int(self.t["monsters"]["invuln_ticks"])
        dx, dd = m["pos"][0] - self.pos[0], m["pos"][1] - self.pos[1]
        n = math.hypot(dx, dd)
        m.update(state="recoil", state_ticks_left=int(sp["recoil_ticks"]),
                 recoil_dir=[dx / n, dd / n] if n > 0 else [1.0, 0.0])
        events.append(("monster_hit", {"monster_id": m["id"], "hp": self.hp, "lost": lost, "pos": list(self.pos)}))
        if self.hp > 0:
            return False
        rest = [out(it) for it in reversed(self.hold)]
        self.hold = []
        events.append(("faint", {"cause": "monster", "lost": rest, "hp": 0}))
        self._finish("fainted", events)
        return True

    # --- lát 2: hái + bắt cá + giỏ (chủ: ndhai255) -------------------------------
    def _nearest(self, entities, radius):
        """Thực thể gần nhất trong `radius`; hòa khoảng cách thì id nhỏ (sort_by_id + min ổn định)."""
        best, best_d = None, None
        for e in sort_by_id(entities):
            d = math.dist(self.pos, e["pos"])
            if d <= radius and (best_d is None or d < best_d):
                best, best_d = e, d
        return best

    def _hold_add(self, action, ref_key, ref_id, kind, n, events) -> bool:
        """PRD-0 (clarify #2): nhận CẢ lượt hoặc không nhận gì. Đủ chỗ cho cả `n` thì thêm vào CUỐI giỏ
        (LIFO) và trả True; thiếu chỗ thì phát hold_full {action, node_id|fish_id, required, free}, trả False."""
        free = max(0, int(self.t["hold_capacity"]) - len(self.hold))
        if n > free:
            events.append(("hold_full", {"action": action, ref_key: ref_id, "required": n, "free": free}))
            return False
        for _ in range(n):
            self.hold.append(make(self.ids.new("I"), kind, self.fr.initial))
        return True

    def _harvest(self, events):
        """`interact` ngoài bến: chỉ ở mặt nước, hái nút `ready` gần nhất trong interact_radius.
        Giỏ thiếu chỗ: hold_full, nút giữ nguyên."""
        if not self._at_surface():
            return
        ready = [n for n in self.nodes if n["regrow_ticks"] == 0]
        node = self._nearest(ready, self.t["interact_radius"])
        if node is None:
            return
        n = int(self.t["node_yield"])
        if self._hold_add("gather", "node_id", node["id"], node["kind"], n, events):
            node["regrow_ticks"] = int(round(self.t["regrow_s"] * TICK))
            events.append(("gather", {"node_id": node["id"], "kind": node["kind"], "amount": n}))

    def _catch(self, events):
        """`catch`: chỉ dưới nước và hết hồi chiêu. PRD-0 (clarify #8): không có đàn trong tầm thì không
        sự kiện, không hồi chiêu. Giỏ thiếu chỗ cho cả `yield`: hold_full, giữ đàn, không hồi chiêu.
        Bắt được: đàn biến mất (cá sinh lại là việc phase sau) và bắt đầu hồi chiêu."""
        if self._at_surface() or self.catch_cd_ticks > 0:
            return
        fish = self._nearest(self.fish, self.t["catch_radius"])
        if fish is None:
            return
        n = int(self.t["fish_yield"][fish["kind"]])
        if not self._hold_add("catch", "fish_id", fish["id"], fish["kind"], n, events):
            return
        self.fish.remove(fish)
        self.catch_cd_ticks = int(round(self.t["catch_cooldown_s"] * TICK))
        events.append(("fish_caught", {"fish_id": fish["id"], "kind": fish["kind"], "yield": n}))

    # --- lát 1: oxy, ngạt, Máu, ngất (chủ: Jancaster1234) ---------------------------
    def _update_oxygen(self, prev_d, events) -> bool:
        """Cập nhật theo `d` CUỐI bước. Trả True nếu vừa ngất (đã phát faint + gather_end, giỏ rỗng)."""
        sd = self.t["surface_depth"]
        was_under = prev_d > sd
        under = not self._at_surface()
        if under and not was_under:
            events.append(("dive", {"pos": list(self.pos)}))
        elif was_under and not under:
            events.append(("surface", {"pos": list(self.pos)}))

        if not under:
            self.oxygen_ticks = min(self.oxygen_max, self.oxygen_ticks + self.t["oxygen_refill_per_tick"])
            self.zero_oxy_ticks = 0
            return False

        before = self.oxygen_ticks
        self.oxygen_ticks = max(0, self.oxygen_ticks - 1)
        if before > 0 and self.oxygen_ticks == 0:
            events.append(("oxygen_empty", {"oxygen_ticks": 0}))
        if self.oxygen_ticks > 0:
            return False

        # oxy = 0 và đang dưới nước: đếm ngạt (tính cả bước oxy vừa về 0)
        self.zero_oxy_ticks += 1
        if self.zero_oxy_ticks < self.t["choke_interval_ticks"]:
            return False
        self.zero_oxy_ticks = 0
        self.hp = max(0, self.hp - 1)
        events.append(("choke", {"hp": self.hp}))
        if self.hp > 0:
            return False
        # ngất: mất toàn bộ giỏ -> kho rỗng; `lost` liệt kê theo LIFO (mới nhặt trước) — PRD-0 mục E
        lost = [out(it) for it in reversed(self.hold)]
        self.hold = []
        events.append(("faint", {"cause": "choke", "lost": lost, "hp": 0}))
        self._finish("fainted", events)
        return True

    # --- tiện ích ---------------------------------------------------------------
    def _at_surface(self) -> bool:
        return self.pos[1] <= self.t["surface_depth"]

    def _in_dock(self) -> bool:
        return math.dist(self.pos, self.t["dock_pos"]) <= self.t["dock_radius"]

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        events.append(("gather_end", {"reason": reason, "inventory": {"items": self.inventory_items()}}))

    def _move(self, inp):
        speed = self.t["swim_speed"]
        mx, md = inp.move
        self.vel = ramp_velocity(self, (mx * speed, md * speed), int(self.t["ramp_max_ticks"]))
        if (mx, md) != (0.0, 0.0):
            self.heading = math.degrees(math.atan2(md, mx)) % 360
        b = self.t["bounds"]
        for i, axis in enumerate(AXES):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i] = lo
                self.vel[i] = max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i] = hi
                self.vel[i] = min(0.0, self.vel[i])


def _toward(src, dst, step):
    dx, dd = dst[0] - src[0], dst[1] - src[1]
    n = math.hypot(dx, dd)
    if n <= step:
        return [float(dst[0]), float(dst[1])]
    return [src[0] + dx / n * step, src[1] + dd / n * step]


def _clamp_monster(pos, sp, b):
    """Chặn thủy quái theo biên map và dải độ sâu của loài."""
    return [min(max(pos[0], b["x"][0]), b["x"][1]), min(max(pos[1], sp["depths"][0]), sp["depths"][1])]


def _reflect(v, lo, hi):
    """Phản xạ phần quãng đường vượt mép. Trả (giá trị, có chạm mép)."""
    hit = False
    while v < lo or v > hi:
        hit = True
        v = 2 * lo - v if v < lo else 2 * hi - v
    return v, hit
