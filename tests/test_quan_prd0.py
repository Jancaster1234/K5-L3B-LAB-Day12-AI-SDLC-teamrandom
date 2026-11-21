"""Quán theo PRD-0 mục D/E/F (docs/clarify.md #1, #3, #4, #5, #9, #10): những luật mới so với bản nháp.

Chạy trong tiến trình qua Session; phần mâu thuẫn scenario chạy hộp đen qua headless_cmd (mã thoát 2).
"""

import math
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import LiveInputs
from chonoi.runner import Session

from helpers import Workdir, run_headless, write_json

TUNING = load_contract()["tuning"]
Q = TUNING["quan"]
MENU = TUNING["menu"]
DISH = "ca_loc_nuong_trui"
PRICE = MENU[DISH]["price"]
TABLE = Q["tables"][0]["pos"]
STOVE = Q["stoves"][0]["pos"]


def pay(order="C1", dish=DISH, base=PRICE):
    return {"order_id": order, "dish_id": dish, "base_price": base}


def run(scenario, ticks, interact_at=()):
    s = Session("quan", TUNING, {"random_customers": False, **scenario}, 1)
    li, evs = LiveInputs(), []
    for k in range(ticks):
        if s.done:
            break
        li.set(interact=k in interact_at)
        evs.extend(s.step(li.advance()))
        li.set(interact=False)
    return s, evs


def names(evs):
    return [e["name"] for e in evs]


def ev(evs, name):
    return next(e for e in evs if e["name"] == name)


class Closing(unittest.TestCase):
    def test_het_ca_khach_dang_an_tra_tien_closing_roi_quan_end(self):
        sc = {"time_left_ticks": 2, "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "state": "eating",
                                                   "eat_ticks_left": 100, "base_price": PRICE, "tip": 12}]}
        s, evs = run(sc, 5)
        self.assertEqual(names(evs), ["paid", "quan_end"])
        self.assertEqual(ev(evs, "paid")["data"], {"order_id": "C1", "table_id": "T1", "base_price": PRICE, "tip": 12,
                                                    "amount": PRICE + 12, "reason": "closing"})
        self.assertEqual(ev(evs, "quan_end")["data"]["money"], PRICE + 12)
        self.assertAlmostEqual(s.sim.reputation, Q["reputation_initial"] + Q["tip_reputation"])

    def test_het_ca_khach_cho_roi_closing_khong_tru_uy_tin(self):
        sc = {"time_left_ticks": 1, "stock": {"ca_loc": 1},
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH}]}
        s, evs = run(sc, 3)
        self.assertEqual(names(evs), ["customer_left", "quan_end"])
        self.assertEqual(ev(evs, "customer_left")["data"], {"order_id": "C1", "table_id": "T1", "reason": "closing",
                                                             "reputation": Q["reputation_initial"]})
        self.assertEqual(s.sim.reputation, Q["reputation_initial"])

    def test_het_ca_khong_sinh_khach_moi(self):
        sc = {"time_left_ticks": Q["first_customer_tick"], "stock": {"ca_loc": 1}, "random_customers": True}
        _, evs = run(sc, Q["first_customer_tick"] + 5)
        self.assertEqual(names(evs), ["quan_end"])


class LeaveCancelsDish(unittest.TestCase):
    def test_het_kien_nhan_huy_mon_tren_bep(self):
        sc = {"stoves": [{"id": "B1", "state": "cooking", "cook_ticks_left": 100, "dish": pay()}],
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "order_status": "assigned",
                             "patience_ticks_left": 1}]}
        s, evs = run(sc, 1)
        self.assertEqual(names(evs), ["customer_left"])
        self.assertEqual(ev(evs, "customer_left")["data"]["reason"], "patience")
        self.assertEqual(s.sim.stoves[0]["state"], "idle")
        self.assertIsNone(s.sim.stoves[0]["dish"])

    def test_het_kien_nhan_huy_mon_tren_tay(self):
        sc = {"hand": pay(), "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH,
                                            "order_status": "assigned", "patience_ticks_left": 1}]}
        s, _ = run(sc, 1)
        self.assertIsNone(s.sim.hand)


class Interact(unittest.TestCase):
    def test_doi_tuong_gan_nhat_khong_dung_duoc_thi_bo_luot(self):
        # bếp idle (không còn đơn reserved) gần hơn bàn; bàn phục vụ được nhưng KHÔNG được thử
        sc = {"player": {"pos": [5, 5]}, "hand": pay(),
              "stoves": [{"id": "B1", "pos": [5, 6]}], "tables": [{"id": "T1", "pos": [5, 3.6]}],
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "order_status": "assigned"}]}
        s, evs = run(sc, 1, interact_at={0})
        self.assertEqual(evs, [])
        self.assertEqual(s.sim.hand, pay())

    def test_phuc_vu_dung_tick_kien_nhan_ve_0_van_hop_le(self):
        sc = {"player": {"pos": TABLE}, "hand": pay(),
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "order_status": "assigned",
                             "patience_ticks_left": 1}]}
        s, evs = run(sc, 1, interact_at={0})
        self.assertEqual(names(evs), ["served"])
        self.assertEqual(ev(evs, "served")["data"], {"order_id": "C1", "table_id": "T1", "dish_id": DISH,
                                                      "patience_ticks_left": 0, "base_price": PRICE, "tip": 0})
        self.assertEqual(s.sim.customers[0]["state"], "eating")

    def test_boa_dung_floor(self):
        base = 59  # 59 * 0.2 = 11.8 -> floor 11 (round sẽ ra 12)
        sc = {"player": {"pos": TABLE}, "hand": pay(base=base),
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "order_status": "assigned",
                             "base_price": base}]}
        _, evs = run(sc, 1, interact_at={0})
        self.assertEqual(ev(evs, "served")["data"]["tip"], math.floor(base * Q["tip_rate"]))

    def test_nau_dung_phan_giu_cho_cua_don(self):
        sc = {"player": {"pos": STOVE}, "stock": {"ca_loc": 2},
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "order_tick": 7}]}
        s, evs = run(sc, 1, interact_at={0})
        self.assertEqual(ev(evs, "cook_started")["data"], {"stove_id": "B1", "order_id": "C1", "dish_id": DISH,
                                                            "items": {"ca_loc": 1}, "base_price": PRICE})
        c = s.sim.customers[0]
        self.assertEqual((c["order_status"], c["reserved"]), ("assigned", {}))
        self.assertEqual(s.sim.stock, {"ca_loc": 1})
        self.assertEqual(s.sim.stoves[0]["dish"], pay())


class Timers(unittest.TestCase):
    def test_ready_ticks_chi_tang_cho_mon_da_ready_tu_dau_buoc(self):
        sc = {"stoves": [{"id": "B1", "state": "cooking", "cook_ticks_left": 1, "dish": pay()}],
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "order_status": "assigned"}]}
        s, evs = run(sc, 1)
        self.assertEqual(ev(evs, "dish_ready")["data"], {"stove_id": "B1", "order_id": "C1", "dish_id": DISH})
        self.assertEqual(s.sim.stoves[0]["ready_ticks"], 0)
        s.step(LiveInputs().advance())
        self.assertEqual(s.sim.stoves[0]["ready_ticks"], 1)

    def test_khach_moi_co_order_tick_va_order_status(self):
        s, evs = run({"stock": {"ca_loc": 1}, "random_customers": True}, Q["first_customer_tick"])
        self.assertEqual(ev(evs, "customer_arrived")["data"], {"order_id": "C1", "table_id": "T1", "dish_id": DISH})
        c = s.sim.snapshot()["customers"][0]
        self.assertEqual((c["order_tick"], c["order_status"], c["base_price"], c["tip"]),
                         (Q["first_customer_tick"], "reserved", PRICE, 0))
        self.assertEqual(c["patience_ticks_left"], int(Q["patience_s"] * 60))


class ScenarioExit2(unittest.TestCase):
    BAD = {
        "giữ khác công thức": {"stock": {"ca_loc": 2},
                               "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "reserved": {"ca_loc": 2}}]},
        "bếp và tay giữ cùng đơn": {"hand": pay(), "stoves": [{"id": "B1", "state": "ready", "dish": pay()}],
                                    "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH,
                                                   "order_status": "assigned"}]},
        "bếp cooking timer <= 0": {"stoves": [{"id": "B1", "state": "cooking", "cook_ticks_left": 0, "dish": pay()}],
                                   "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH,
                                                  "order_status": "assigned"}]},
        "eating thiếu base_price/tip": {"customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH,
                                                       "state": "eating", "eat_ticks_left": 5}]},
        "assigned không có món": {"customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH,
                                                 "order_status": "assigned"}]},
        "món không khớp đơn": {"hand": pay(dish="goi_bong_sung"),
                               "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH,
                                              "order_status": "assigned"}]},
        "hand là chuỗi (bản cũ)": {"hand": DISH},
    }

    def test_mau_thuan_scenario_ma_2(self):
        with Workdir() as w:
            for why, block in self.BAD.items():
                sc = write_json(w.path("sc.json"), {"quan": block})
                code, _ = run_headless("--mode", "quan", "--seed", "1", "--ticks", "1", "--scenario", sc,
                                       "--out", w.path("o.jsonl"))
                self.assertEqual(code, 2, why)

    def test_don_unfulfillable_hop_le(self):
        s, evs = run({"customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH,
                                     "order_status": "unfulfillable"}]}, 1)
        self.assertEqual(evs, [])
        self.assertEqual(s.sim.customers[0]["reserved"], {})


if __name__ == "__main__":
    unittest.main()
