"""Tích hợp quán lát 3 + lát 4: khách do lát 3 sinh ra được lát 4 nấu, bưng, phục vụ, trả tiền.

Điều khiển người chơi bằng LiveInputs qua Session (cùng lớp sim với headless); số liệu từ game.contract.json.
"""

import math
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import LiveInputs
from chonoi.runner import Session

TUNING = load_contract()["tuning"]
Q = TUNING["quan"]
MENU = TUNING["menu"]
STOVE = Q["stoves"][0]["pos"]
TABLE = Q["tables"][0]["pos"]
DISH = "ca_loc_nuong_trui"


class Flow:
    def __init__(self, scenario):
        self.s = Session("quan", TUNING, scenario, 1)
        self.li = LiveInputs()
        self.events = []

    def step(self, **buttons):
        self.li.set(**buttons)
        self.events.extend(self.s.step(self.li.advance()))
        self.li.set(interact=False)

    def wait_for(self, name, limit):
        for _ in range(limit):
            if any(e["name"] == name for e in self.events):
                return
            self.step()
        raise AssertionError(f"không thấy sự kiện {name} sau {limit} tick")

    def walk_to(self, target, limit=600):
        for _ in range(limit):
            p = self.s.sim.pos
            dx, dz = target[0] - p[0], target[1] - p[1]
            if math.hypot(dx, dz) <= Q["interact_radius"] * 0.5:
                break
            self.step(move=[dx, dz])
        self.li.set(move=[0, 0])
        for _ in range(Q["ramp_max_ticks"] + 1):  # dừng hẳn
            self.step()

    def names(self):
        return [e["name"] for e in self.events]

    def first(self, name):
        return next(e for e in self.events if e["name"] == name)


class QuanFlow(unittest.TestCase):
    def test_khach_lat3_duoc_lat4_phuc_vu_va_tra_tien(self):
        f = Flow({"stock": {"ca_loc": 1}, "player": {"pos": STOVE}})
        f.wait_for("customer_arrived", Q["first_customer_tick"] + 1)
        arrived = f.first("customer_arrived")
        self.assertEqual(arrived["data"]["dish_id"], DISH)  # món duy nhất nấu được từ kho
        cid = arrived["data"]["customer_id"]
        self.assertEqual(f.s.sim.customers[0]["reserved"], MENU[DISH]["recipe"])

        f.step(interact=True)
        self.assertEqual(f.events[-1]["name"], "cook_started")
        self.assertEqual(f.events[-1]["data"], {"stove_id": "B1", "dish_id": DISH})
        self.assertEqual(f.s.sim.stock, {})
        self.assertEqual(f.s.sim.customers[0]["reserved"], {})  # phần giữ chỗ đã vào nồi

        f.wait_for("dish_ready", int(MENU[DISH]["cook_s"] * 60) + 1)
        f.step(interact=True)
        self.assertEqual(f.events[-1]["name"], "dish_picked")
        self.assertEqual(f.s.sim.hand, DISH)

        f.walk_to(TABLE)
        f.step(interact=True)
        served = f.first("served")
        self.assertEqual(served["data"], {"customer_id": cid, "table_id": "T1", "dish_id": DISH})
        self.assertIsNone(f.s.sim.hand)

        f.wait_for("paid", int(Q["eat_s"] * 60) + 1)
        paid = f.first("paid")
        price = MENU[DISH]["price"]
        tip = round(price * Q["tip_rate"])  # phục vụ nhanh -> còn > tip_min_patience_ratio
        self.assertEqual((paid["data"]["price"], paid["data"]["tip"]), (price, tip))
        self.assertEqual(f.s.sim.money, price + tip)
        self.assertAlmostEqual(f.s.sim.reputation, Q["reputation_initial"] + Q["tip_reputation"])
        self.assertNotIn("customer_left", f.names())
        order = [n for n in f.names() if n in ("customer_arrived", "cook_started", "dish_ready",
                                                  "dish_picked", "served", "paid")]
        self.assertEqual(order, ["customer_arrived", "cook_started", "dish_ready", "dish_picked", "served", "paid"])

    def test_cung_dau_vao_cung_ket_qua(self):
        runs = []
        for _ in range(2):
            f = Flow({"stock": {"ca_loc": 1, "bong_sung": 2}, "player": {"pos": STOVE}})
            for t in range(900):
                f.step(interact=(t % 50 == 0))
            runs.append(f.events)
        self.assertEqual(runs[0], runs[1])


if __name__ == "__main__":
    unittest.main()
