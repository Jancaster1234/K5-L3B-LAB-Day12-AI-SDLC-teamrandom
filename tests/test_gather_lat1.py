"""Gather lát 1: dive/surface, oxy, oxygen_empty, ngạt (choke), Máu, ngất (faint).

Chạy trong tiến trình qua `Session` (cùng lớp sim với headless), số liệu đọc từ game.contract.json.
"""

import json
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import InputPlayer
from chonoi.runner import Session

from helpers import Workdir

TUNING = load_contract()["tuning"]
G = TUNING["gather"]
OXY_MAX = int(round(G["oxygen_max_s"] * 60))
CHOKE = G["choke_interval_ticks"]
DEEP = [50, 10]  # xa bến, dưới nước, không có nút/cá mặc định trong bán kính


def play(scenario, ticks, frames=()):
    """Chạy `ticks` bước (dừng sớm nếu kết thúc). Trả (session, danh sách event)."""
    s = Session("gather", TUNING, {"random_fish": False, **scenario}, 1)
    ip = InputPlayer(list(frames))
    evs = []
    while s.tick < ticks and not s.done:
        evs.extend(s.step(ip.advance(s.tick)))
    return s, evs


def names(evs):
    return [e["name"] for e in evs]


class Oxygen(unittest.TestCase):
    def test_duoi_nuoc_tru_1_moi_tick(self):
        s, evs = play({"player": {"pos": DEEP}}, 10)
        self.assertEqual(s.sim.oxygen_ticks, OXY_MAX - 10)
        self.assertEqual(evs, [])

    def test_mat_nuoc_hoi_oxy_va_kep_tran(self):
        s, _ = play({"player": {"pos": [50, 0], "oxygen_ticks": 100}}, 1)
        self.assertEqual(s.sim.oxygen_ticks, 100 + G["oxygen_refill_per_tick"])
        s, _ = play({"player": {"pos": [50, 0], "oxygen_ticks": OXY_MAX - 1}}, 1)
        self.assertEqual(s.sim.oxygen_ticks, OXY_MAX)

    def test_oxygen_empty_dung_mot_lan(self):
        _, evs = play({"player": {"pos": DEEP, "oxygen_ticks": 1}}, 5)
        oe = [e for e in evs if e["name"] == "oxygen_empty"]
        self.assertEqual(len(oe), 1)
        self.assertEqual(oe[0]["tick"], 1)
        self.assertEqual(oe[0]["data"], {"oxygen_ticks": 0})


class Choke(unittest.TestCase):
    def test_du_chu_ky_thi_tru_mau(self):
        s, evs = play({"player": {"pos": DEEP, "oxygen_ticks": 0, "zero_oxy_ticks": CHOKE - 1}}, 1)
        self.assertEqual(names(evs), ["choke"])
        self.assertEqual(evs[0]["data"], {"hp": G["hp_max"] - 1})
        self.assertEqual(s.sim.hp, G["hp_max"] - 1)
        self.assertEqual(s.sim.zero_oxy_ticks, 0)

    def test_moc_thoi_gian_choke_tu_luc_het_oxy(self):
        # oxy về 0 ở tick 1 (tính là bước ngạt thứ nhất) -> choke ở tick CHOKE, lần hai ở 2*CHOKE
        _, evs = play({"player": {"pos": DEEP, "oxygen_ticks": 1}}, 2 * CHOKE)
        self.assertEqual([e["tick"] for e in evs if e["name"] == "choke"], [CHOKE, 2 * CHOKE])

    def test_noi_len_reset_dem_ngat(self):
        s, evs = play({"player": {"pos": [50, 1], "oxygen_ticks": 0, "zero_oxy_ticks": 30}}, 30,
                      [{"tick": 0, "move": [0, -1]}])
        self.assertTrue(s.sim._at_surface())
        self.assertEqual(s.sim.zero_oxy_ticks, 0)
        self.assertGreater(s.sim.oxygen_ticks, 0)
        self.assertEqual(names(evs).count("surface"), 1)
        self.assertNotIn("choke", names(evs))


class Zones(unittest.TestCase):
    def test_dive_khi_xuong_duoi_mat_nuoc(self):
        _, evs = play({"player": {"pos": [50, 0]}}, 30, [{"tick": 0, "move": [0, 1]}])
        dive = [e for e in evs if e["name"] == "dive"]
        self.assertEqual(len(dive), 1)
        self.assertGreater(dive[0]["data"]["pos"][1], G["surface_depth"])
        self.assertNotIn("surface", names(evs))

    def test_dung_yen_khong_phat_dive_surface(self):
        _, evs = play({"player": {"pos": [50, 0]}}, 10)
        self.assertEqual(evs, [])


class Faint(unittest.TestCase):
    SC = {"hold": ["ca_loc", "bong_sung"],
          "player": {"pos": DEEP, "hp": 1, "oxygen_ticks": 0, "zero_oxy_ticks": CHOKE - 1}}

    def test_mau_ve_0_thi_ngat_mat_gio(self):
        s, evs = play(self.SC, 10)
        self.assertEqual(names(evs), ["choke", "faint", "gather_end"])
        # PRD-0 mục E: lost theo LIFO (mới nhặt trước); giỏ ["ca_loc", "bong_sung"]
        self.assertEqual(evs[1]["data"], {"cause": "choke", "lost": ["bong_sung", "ca_loc"], "hp": 0})
        self.assertEqual(evs[-1]["data"], {"reason": "fainted", "inventory": {"items": {}}})
        self.assertTrue(s.done)
        self.assertEqual(s.end_row()["reason"], "fainted")
        self.assertEqual(s.sim.hold, [])

    def test_ngat_ghi_kho_rong(self):
        with Workdir() as w:
            s, _ = play(self.SC, 10)
            s.write_inventory_if_done(w.path("inv.json"))
            with open(w.path("inv.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {}})

    def test_ngat_xet_truoc_cap_ben(self):
        sc = {**self.SC, "player": {**self.SC["player"], "pos": [2, 2]}}  # trong vùng bến, dưới nước
        _, evs = play(sc, 1, [{"tick": 0, "interact": True}])
        self.assertEqual(evs[-1]["data"]["reason"], "fainted")


class Determinism(unittest.TestCase):
    def test_cung_dau_vao_cung_ket_qua(self):
        fr = [{"tick": 0, "move": [1, 1]}, {"tick": 200, "move": [0, -1]}]
        a = play({"player": {"pos": [5, 0], "oxygen_ticks": 120}}, 400, fr)[1]
        b = play({"player": {"pos": [5, 0], "oxygen_ticks": 120}}, 400, fr)[1]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
