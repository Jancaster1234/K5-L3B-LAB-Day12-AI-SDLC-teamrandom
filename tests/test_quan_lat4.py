"""Unit tests cho Quán Lát 4 (bếp, bàn, trả tiền, boa, uy tín, kết thúc ca).
Tự test bằng scenario dựng sẵn, không phụ thuộc vào lát 3.
"""

import json
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import LiveInputs
from chonoi.runner import Session


class TestQuanLat4(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()
        self.tuning = self.contract["tuning"]

    def _make_session(self, scenario):
        return Session("quan", self.tuning, scenario, seed=1)

    def test_stove_cooking_ready_and_pick(self):
        """Kiểm tra quy trình bếp: nấu (cook_started) -> chín (dish_ready) -> bốc món (dish_picked)."""
        scenario = {
            "player": {"pos": [2, 8]},  # Đứng sát bếp B1 [2, 8]
            "stock": {"ca_loc": 1},
            "customers": [
                {
                    "id": "C1",
                    "table_id": "T1",
                    "dish_id": "ca_loc_nuong_trui",
                    "state": "waiting",
                    "patience_ticks_left": 3600,
                    "patience_ticks_total": 3600,
                }
            ],
        }
        sess = self._make_session(scenario)
        li = LiveInputs()

        # Tick 1: Bấm interact -> Bắt đầu nấu
        li.set(interact=True)
        evs = sess.step(li.advance())
        names = [e["name"] for e in evs]
        self.assertIn("cook_started", names)
        cook_ev = next(e for e in evs if e["name"] == "cook_started")
        self.assertEqual(cook_ev["data"]["stove_id"], "B1")
        self.assertEqual(cook_ev["data"]["dish_id"], "ca_loc_nuong_trui")
        self.assertNotIn("ca_loc", sess.sim.stock)
        b1 = next(s for s in sess.sim.stoves if s["id"] == "B1")
        self.assertEqual(b1["state"], "cooking")
        self.assertEqual(b1["cook_ticks_left"], 360)  # 6s * 60

        # Nấu trong 359 tick tiếp theo: bếp vẫn đang nấu
        li.set(interact=False)
        for _ in range(359):
            evs = sess.step(li.advance())
            self.assertFalse(any(e["name"] == "dish_ready" for e in evs))
        self.assertEqual(b1["cook_ticks_left"], 1)

        # Tick 361: Hoàn thành nấu -> dish_ready
        evs = sess.step(li.advance())
        names = [e["name"] for e in evs]
        self.assertIn("dish_ready", names)
        ready_ev = next(e for e in evs if e["name"] == "dish_ready")
        self.assertEqual(ready_ev["data"]["stove_id"], "B1")
        self.assertEqual(b1["state"], "ready")

        # Bấm interact -> Bốc món (dish_picked)
        li.set(interact=True)
        evs = sess.step(li.advance())
        names = [e["name"] for e in evs]
        self.assertIn("dish_picked", names)
        pick_ev = next(e for e in evs if e["name"] == "dish_picked")
        self.assertEqual(pick_ev["data"]["dish_id"], "ca_loc_nuong_trui")
        self.assertEqual(sess.sim.hand, "ca_loc_nuong_trui")
        self.assertEqual(b1["state"], "idle")
        self.assertIsNone(b1["dish"])

    def test_serve_eating_and_paid_with_tip(self):
        """Phục vụ khách kiên nhẫn cao (>=50%): ăn xong trả tiền + boa 20% + tăng 0.2 uy tín."""
        scenario = {
            "player": {"pos": [9, 2]},  # Đứng sát bàn T1 [9, 2]
            "hand": "ca_loc_nuong_trui",
            "reputation": 3.0,
            "customers": [
                {
                    "id": "C1",
                    "table_id": "T1",
                    "dish_id": "ca_loc_nuong_trui",
                    "state": "waiting",
                    "patience_ticks_left": 3000,
                    "patience_ticks_total": 3600,  # 3000/3600 = 83.3% >= 50% -> đủ điều kiện boa
                }
            ],
        }
        sess = self._make_session(scenario)
        li = LiveInputs()

        # Tick 1: Bấm interact -> Phục vụ món
        li.set(interact=True)
        evs = sess.step(li.advance())
        names = [e["name"] for e in evs]
        self.assertIn("served", names)
        served_ev = next(e for e in evs if e["name"] == "served")
        self.assertEqual(served_ev["data"]["table_id"], "T1")
        self.assertEqual(served_ev["data"]["customer_id"], "C1")
        self.assertEqual(served_ev["data"]["dish_id"], "ca_loc_nuong_trui")
        self.assertIsNone(sess.sim.hand)

        c1 = sess.sim.customers[0]
        self.assertEqual(c1["state"], "eating")
        self.assertEqual(c1["eat_ticks_left"], 600)  # 10s * 60
        self.assertTrue(c1["tipped"])

        # Khách ăn trong 599 tick tiếp theo
        li.set(interact=False)
        for _ in range(599):
            evs = sess.step(li.advance())
            self.assertFalse(any(e["name"] == "paid" for e in evs))

        # Tick ăn xong: trả tiền (price=60, tip=12, amount=72)
        evs = sess.step(li.advance())
        names = [e["name"] for e in evs]
        self.assertIn("paid", names)
        paid_ev = next(e for e in evs if e["name"] == "paid")
        self.assertEqual(paid_ev["data"]["price"], 60)
        self.assertEqual(paid_ev["data"]["tip"], 12)
        self.assertEqual(paid_ev["data"]["amount"], 72)
        self.assertEqual(sess.sim.money, 72)
        self.assertEqual(sess.sim.earned, 72)
        self.assertAlmostEqual(sess.sim.reputation, 3.2, places=2)
        self.assertEqual(len(sess.sim.customers), 0)  # Khách đã rời bàn

    def test_serve_eating_and_paid_no_tip(self):
        """Phục vụ khách kiên nhẫn thấp (<50%): ăn xong trả tiền nhưng không có boa, uy tín giữ nguyên."""
        scenario = {
            "player": {"pos": [9, 2]},
            "hand": "goi_bong_sung",
            "reputation": 3.0,
            "customers": [
                {
                    "id": "C2",
                    "table_id": "T1",
                    "dish_id": "goi_bong_sung",
                    "state": "waiting",
                    "patience_ticks_left": 1000,
                    "patience_ticks_total": 3600,  # 1000/3600 = 27.7% < 50%
                }
            ],
        }
        sess = self._make_session(scenario)
        li = LiveInputs()

        li.set(interact=True)
        sess.step(li.advance())
        c2 = sess.sim.customers[0]
        self.assertFalse(c2["tipped"])

        # Cho khách ăn xong
        li.set(interact=False)
        for _ in range(int(c2["eat_ticks_left"]) - 1):
            sess.step(li.advance())

        evs = sess.step(li.advance())
        names = [e["name"] for e in evs]
        self.assertIn("paid", names)
        paid_ev = next(e for e in evs if e["name"] == "paid")
        self.assertEqual(paid_ev["data"]["price"], 40)
        self.assertEqual(paid_ev["data"]["tip"], 0)
        self.assertEqual(paid_ev["data"]["amount"], 40)
        self.assertEqual(sess.sim.money, 40)
        self.assertAlmostEqual(sess.sim.reputation, 3.0, places=2)

    def test_carry_limit_cannot_pick_second_dish(self):
        """Đang cầm món trong tay thì không thể bốc thêm món từ bếp khác (carry_limit: 1)."""
        scenario = {
            "player": {"pos": [2, 8]},
            "hand": "goi_bong_sung",
            "stoves": [{"id": "B1", "state": "ready", "dish": "ca_loc_nuong_trui"}],
        }
        sess = self._make_session(scenario)
        li = LiveInputs()

        li.set(interact=True)
        evs = sess.step(li.advance())
        self.assertFalse(any(e["name"] == "dish_picked" for e in evs))
        self.assertEqual(sess.sim.hand, "goi_bong_sung")

    def test_interact_tie_break_stove_before_table(self):
        """Nếu bếp và bàn cùng khoảng cách, bếp được ưu tiên trước bàn."""
        # Player ở [5, 5], đặt bếp tại [5, 6] (kc 1.0) và bàn tại [5, 4] (kc 1.0)
        scenario = {
            "player": {"pos": [5, 5]},
            "hand": None,
            "stock": {"ca_loc": 1},
            "stoves": [{"id": "B1", "pos": [5, 6], "state": "idle"}],
            "tables": [{"id": "T1", "pos": [5, 4]}],
            "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "state": "waiting"}],
        }
        sess = self._make_session(scenario)
        li = LiveInputs()

        li.set(interact=True)
        evs = sess.step(li.advance())
        names = [e["name"] for e in evs]
        self.assertIn("cook_started", names)

    def test_quan_end_when_time_up(self):
        """Hết giờ thì buổi mở quán kết thúc (quan_end) với đầy đủ thông số."""
        scenario = {
            "time_left_ticks": 2,
            "reputation": 4.2,
        }
        sess = self._make_session(scenario)
        li = LiveInputs()

        sess.step(li.advance())  # tick 1, time_left=1
        self.assertFalse(sess.done)

        evs = sess.step(li.advance())  # tick 2, time_left=0 -> done
        self.assertTrue(sess.done)
        self.assertEqual(sess.sim.reason, "time")
        names = [e["name"] for e in evs]
        self.assertIn("quan_end", names)
        end_ev = next(e for e in evs if e["name"] == "quan_end")
        self.assertEqual(end_ev["data"]["reason"], "time")
        self.assertAlmostEqual(end_ev["data"]["reputation"], 4.2, places=2)


if __name__ == "__main__":
    unittest.main()
