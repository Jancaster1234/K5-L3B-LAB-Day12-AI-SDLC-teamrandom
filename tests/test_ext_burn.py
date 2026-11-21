"""Mở rộng `burn` (Ticket-02 mục 3): burn_s 20 — ready_ticks > 1200 thì món cháy, bếp rảnh, đơn thử giữ lại."""

import json
import unittest

from helpers import stock_items

from chonoi.contract import load_contract
from chonoi.inputs import LiveInputs
from chonoi.runner import Session

C = load_contract()
TUNING = C["tuning"]
BURN = int(TUNING["quan"]["burn_s"] * 60)
DISH = "ca_loc_nuong_trui"
PAY = {"order_id": "C1", "dish_id": DISH, "base_price": 60}


def run(scenario, ticks):
    s = Session("quan", TUNING, {"random_customers": False, **scenario}, 1)
    evs = []
    for _ in range(ticks):
        evs.extend(s.step(LiveInputs().advance()))
    return s, evs


def ready_stove(age):
    return [{"id": "B1", "state": "ready", "ready_ticks": age, "dish": PAY}]


ORDER = [{"id": "C1", "table_id": "T1", "dish_id": DISH, "order_status": "assigned"}]


class Burn(unittest.TestCase):
    def test_khai_trong_manifest(self):
        self.assertIn("burn", C["extensions"])
        self.assertEqual(TUNING["quan"]["burn_s"], 20)

    def test_dung_1200_tick_van_con_qua_1200_thi_chay(self):
        s, evs = run({"stoves": ready_stove(BURN - 1), "customers": ORDER}, 1)  # sau bước 1: đúng 1200
        self.assertEqual(evs, [])
        self.assertEqual(s.sim.stoves[0]["state"], "ready")
        evs = s.step(LiveInputs().advance())  # 1201
        self.assertEqual([e["name"] for e in evs], ["dish_burnt"])
        self.assertEqual(s.sim.stoves[0]["state"], "idle")

    def test_chay_giu_lai_du_kho_thi_reserved(self):
        s, evs = run({"stock": stock_items({"ca_loc": 1}), "stoves": ready_stove(BURN), "customers": ORDER}, 1)
        self.assertEqual(evs[0]["data"], {"stove_id": "B1", "order_id": "C1", "dish_id": DISH, "order_status": "reserved"})
        c = s.sim.customers[0]
        self.assertEqual((c["order_status"], c["reserved"]), ("reserved", ["I1"]))

    def test_chay_thieu_kho_thi_unfulfillable_khach_van_cho(self):
        s, evs = run({"stoves": ready_stove(BURN), "customers": ORDER}, 1)
        self.assertEqual(evs[0]["data"]["order_status"], "unfulfillable")
        self.assertEqual(s.sim.customers[0]["state"], "waiting")


if __name__ == "__main__":
    unittest.main()
