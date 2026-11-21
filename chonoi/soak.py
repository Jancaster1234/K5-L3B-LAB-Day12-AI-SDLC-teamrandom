"""Soak headless (Ticket-04 mục 2): python3 -m chonoi.soak --seed 7 --days 10 --out soak.json

Chạy N Ngày trong một tiến trình bằng bot tất định; mỗi Ngày đi qua gather → quan → shop, kế hoạch D1–D5 lặp
ở Ngày 6–10; tiền, earned, uy tín, cấp nâng cấp, số Ngày và id cá thể tiếp tục xuyên suốt.
Ghi {days, days_completed, crashes, results[{day, earned, reputation, score}], duration_s}.
Mã thoát: 0 chạy xong (kể cả có crash, ghi trong crashes), 2 tham số sai, 1 lỗi ghi file.
"""

import argparse
import json
import math
import sys
import time

from .contract import load_contract
from .errors import BadInput
from .inputs import InputState
from .runner import Session


class Bot:
    """Bot tất định chỉ đọc trạng thái sim: hái nút gần bến rồi cập bến, nấu–bưng–phục vụ ở quán, mua nâng cấp."""

    def __init__(self):
        self._held = set()

    def _press(self, want):
        edges = {b for b in want if b not in self._held}
        self._held = set(want)
        return edges

    def act(self, sim):
        phase = sim.phase
        sub = sim.sub
        move = (0.0, 0.0)
        want = set()
        buy = None
        if phase == "gather":
            nodes = [n for n in sub.nodes if n["regrow_ticks"] == 0]
            near = min(nodes, key=lambda n: (abs(n["pos"][0] - sub.pos[0]), n["id"]), default=None)
            if near and len(sub.hold) < sub.t["hold_capacity"] and sub.time_left_ticks > 1200:
                dx = near["pos"][0] - sub.pos[0]
                if abs(dx) > 1.0:
                    move = (1.0 if dx > 0 else -1.0, -1.0 if sub.pos[1] > 0 else 0.0)
                else:
                    want = {"interact"} if sub.phase_tick % 2 == 0 else set()
            else:
                dx = sub.t["dock_pos"][0] - sub.pos[0]
                move = (max(-1.0, min(1.0, dx)), -1.0 if sub.pos[1] > 0 else 0.0)
                if math.dist(sub.pos, sub.t["dock_pos"]) <= sub.t["dock_radius"] and sub.phase_tick % 2 == 0:
                    want = {"interact"}
        elif phase == "quan":
            target = None
            if sub.hand is not None:
                target = next((tb["pos"] for c in sub.customers if c["id"] == sub.hand["order_id"]
                               for tb in sub.tables if tb["id"] == c["table_id"]), None)
            else:
                ready = [s for s in sub.stoves if s["state"] == "ready"]
                idle = [s for s in sub.stoves if s["state"] == "idle"]
                if ready:
                    target = ready[0]["pos"]
                elif idle and any(c["order_status"] == "reserved" for c in sub.customers):
                    target = idle[0]["pos"]
            if target is not None:
                dx, dz = target[0] - sub.pos[0], target[1] - sub.pos[1]
                if math.hypot(dx, dz) > 0.5:
                    move = (dx, dz)
                elif sub.phase_tick % 2 == 0:
                    want = {"interact"}
        else:  # shop: mua cấp kế tiếp nếu đủ tiền, rồi đóng
            ups = sim.tuning["shop"]["upgrades"]
            for kind in sorted(ups):
                lvl = sim.upgrades.get(kind, 0) + 1
                entry = next((e for e in ups[kind] if e["level"] == lvl), None)
                if entry and sim.money >= entry["price"] and sub is not None:
                    buy = kind
                    break
            if buy is None and sim.shop["phase_tick"] >= 1:
                want = {"shop_done"}
        n = math.hypot(*move)
        if n > 1:
            move = (move[0] / n, move[1] / n)
        edges = self._press(want)
        return InputState(move, {b: b in self._held for b in ("interact", "shop_done")}, edges, buy=buy)


def soak(seed, days, tuning=None):
    tuning = tuning or load_contract()["tuning"]
    t0 = time.perf_counter()
    results, crashes, completed = [], 0, 0
    try:
        s = Session("day", tuning, {}, seed, days=days)
        bot = Bot()
        last = 0
        limit = days * 30000
        while not s.done and s.tick < limit:
            s.step(bot.act(s.sim))
            sim = s.sim
            if sim.days_completed > last:
                last = sim.days_completed
                results.append({"day": last, "earned": sim.earned, "reputation": sim.reputation,
                                "score": sim.earned + tuning["score"]["reputation_multiplier"] * math.floor(sim.reputation)})
        completed = s.sim.days_completed
    except Exception:  # noqa: BLE001 — soak đếm crash thay vì dừng runner của lớp
        crashes += 1
    return {"days": days, "days_completed": completed, "crashes": crashes, "results": results,
            "duration_s": round(time.perf_counter() - t0, 3)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.soak")
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--days", required=True, type=int)
    p.add_argument("--out", required=True)
    try:
        a = p.parse_args(argv)
    except SystemExit:
        return 2
    try:
        if a.days < 1:
            raise BadInput("--days phải >= 1")
        tuning = load_contract()["tuning"]
    except BadInput as e:
        sys.stderr.write(f"đầu vào sai: {e}\n")
        return 2
    rep = soak(a.seed, a.days, tuning)
    try:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(rep, f, ensure_ascii=False)
            f.write("\n")
    except OSError as e:
        sys.stderr.write(f"lỗi ghi: {e}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
