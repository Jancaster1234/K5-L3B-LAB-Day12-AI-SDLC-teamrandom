"""Gather v1.1 (Ticket-02 mục 1.1, 1.2, 4.5): cá bơi + sinh theo lịch, Cá Sấu (patrol/chase/hit/recoil), bất tử."""

import math
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import InputPlayer
from chonoi.runner import Session

from helpers import Workdir, run_headless, write_json

TUNING = load_contract()["tuning"]
G = TUNING["gather"]
CA_SAU = G["monsters"]["species"]["ca_sau"]
DOCK = G["dock_pos"]


def play(scenario, ticks, frames=()):
    s = Session("gather", TUNING, scenario, 1)
    ip, evs = InputPlayer(list(frames)), []
    while s.tick < ticks and not s.done:
        evs.extend(s.step(ip.advance(s.tick)))
    return s, evs


def fish(fid, kind, x, d, h=0, age=0):
    return {"id": fid, "kind": kind, "pos": [x, d], "heading_deg": h, "age_ticks": age}


def croc(mid="M1", pos=(50, 15), wps=((50, 15), (54, 15)), **kw):
    return {"id": mid, "kind": "ca_sau", "pos": list(pos), "waypoints": [list(w) for w in wps], **kw}


def names(evs):
    return [e["name"] for e in evs]


class FishSwim(unittest.TestCase):
    def test_ca_boi_dung_toc_do(self):
        s, _ = play({"fish": [fish("F1", "ca_linh", 50, 5)], "monsters": []}, 60)
        f = s.sim.fish[0]
        self.assertAlmostEqual(f["pos"][0], 50 + G["fish_speed"], places=6)
        self.assertEqual(f["age_ticks"], 60)

    def test_ca_fixture_dung_yen_khi_tat_random_fish(self):
        s, _ = play({"random_fish": False, "fish": [fish("F1", "ca_linh", 50, 5)], "monsters": []}, 60)
        self.assertEqual(s.sim.fish[0]["pos"], [50.0, 5.0])

    def test_phan_xa_o_mep_x(self):
        hi = G["fish_x"][1]
        s, _ = play({"fish": [fish("F1", "ca_linh", hi - 0.5, 5)], "monsters": []}, 60)
        f = s.sim.fish[0]
        self.assertAlmostEqual(f["pos"][0], hi - (G["fish_speed"] - 0.5), places=6)
        self.assertAlmostEqual(f["heading_deg"], 180.0, places=6)

    def test_doi_huong_o_buoc_boi_thu_120(self):
        turn = G["fish_turn_ticks"]
        s, _ = play({"fish": [fish("F1", "ca_linh", 50, 5)], "monsters": []}, turn - 1)
        self.assertEqual(s.sim.fish[0]["heading_deg"], 0.0)
        s.step(InputPlayer([]).advance(s.tick))
        self.assertNotEqual(s.sim.fish[0]["heading_deg"], 0.0)

    def test_ca_o_trong_dai_do_sau_cua_loai(self):
        s, _ = play({"monsters": []}, 2000)
        for f in s.sim.fish:
            lo, hi = G["fish_depths"][f["kind"]]
            self.assertTrue(lo <= f["pos"][1] <= hi, f)
            self.assertTrue(G["fish_x"][0] <= f["pos"][0] <= G["fish_x"][1], f)


class FishSpawn(unittest.TestCase):
    def test_sinh_mot_dan_tai_phase_tick_360(self):
        k = G["fish_spawn_ticks"]
        s, evs = play({"monsters": []}, k)
        sp = [e for e in evs if e["name"] == "fish_spawned"]
        self.assertEqual(len(sp), 1)
        self.assertEqual(sp[0]["tick"], k)
        d = sp[0]["data"]
        self.assertEqual(d["id"], f"F{len(G['fish_initial']) + 1}")
        self.assertIn(d["pos"][0], G["fish_spawn_x"])
        self.assertIn(d["pos"][1], G["fish_spawn_depths"][d["kind"]])
        self.assertEqual(len(s.sim.fish), len(G["fish_initial"]) + 1)

    def test_khong_sinh_khi_dat_tran(self):
        full = [fish(f"F{i + 1}", "ca_linh", 5 + i * 7, 4) for i in range(G["fish_max"])]
        _, evs = play({"fish": full, "monsters": []}, G["fish_spawn_ticks"])
        self.assertNotIn("fish_spawned", names(evs))

    def test_tat_dinh_cung_seed(self):
        a = play({}, 1500)[1]
        b = play({}, 1500)[1]
        self.assertEqual(a, b)


class Crocodile(unittest.TestCase):
    def test_gather_doc_lap_dung_bo_tri_ngay_1(self):
        s, _ = play({}, 0)
        self.assertEqual([m["id"] for m in s.sim.monsters],
                         [m["id"] for m in G["monsters"]["spawns"] if m["from_day"] <= 1])

    def test_tuan_tra_1_m_s_toi_waypoint(self):
        s, _ = play({"random_fish": False, "monsters": [croc(pos=(50, 24), wps=((50, 24), (54, 24)))]}, 60)
        m = s.sim.monsters[0]
        self.assertAlmostEqual(m["pos"][0], 50 + CA_SAU["patrol_speed"], places=6)
        self.assertEqual(m["state"], "patrol")

    def test_phat_hien_thi_duoi_3_m_s(self):
        sc = {"random_fish": False, "player": {"pos": [56, 24]}, "monsters": [croc(pos=(60, 24), wps=((60, 24), (64, 24)))]}
        s, _ = play(sc, 1)
        m = s.sim.monsters[0]
        self.assertEqual(m["state"], "chase")
        self.assertAlmostEqual(m["pos"][0], 60 - CA_SAU["chase_speed"] / 60, places=6)

    def test_nguoi_choi_nong_khong_bi_phat_hien(self):
        sc = {"random_fish": False, "player": {"pos": [58, 9]}, "monsters": [croc(pos=(60, 10), wps=((60, 10), (64, 10)))]}
        s, evs = play(sc, 5)
        self.assertEqual(s.sim.monsters[0]["state"], "patrol")
        self.assertNotIn("monster_hit", names(evs))

    def test_cham_mat_mau_rot_hang_lifo_bat_tu_recoil(self):
        hold = ["ca_loc", "bong_sung", "ca_linh", "keo_neo", "ca_keo"]
        sc = {"random_fish": False, "hold": hold, "player": {"pos": [51, 15]}, "monsters": [croc()]}
        s, evs = play(sc, 1)
        hit = [e for e in evs if e["name"] == "monster_hit"]
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0]["data"]["monster_id"], "M1")
        self.assertEqual(hit[0]["data"]["hp"], G["hp_max"] - 1)
        self.assertEqual(hit[0]["data"]["lost"], ["ca_keo", "keo_neo"])  # floor(5/2) = 2, nhặt sau mất trước
        self.assertEqual(s.sim.hold, hold[:3])
        self.assertEqual(s.sim.invuln_ticks, G["monsters"]["invuln_ticks"])
        m = s.sim.monsters[0]
        self.assertEqual((m["state"], m["state_ticks_left"]), ("recoil", CA_SAU["recoil_ticks"]))
        self.assertAlmostEqual(m["recoil_dir"][0], -1.0, places=6)  # xa người chơi (người chơi ở +x)

    def test_recoil_lui_2_m_trong_60_buoc_roi_ve_patrol(self):
        sc = {"random_fish": False, "player": {"pos": [51, 15]}, "monsters": [croc()]}
        s, _ = play(sc, 1)
        x0 = s.sim.monsters[0]["pos"][0]
        for _ in range(CA_SAU["recoil_ticks"]):
            s.step(InputPlayer([]).advance(s.tick))
        m = s.sim.monsters[0]
        self.assertAlmostEqual(m["pos"][0], x0 - CA_SAU["recoil_dist"], places=6)
        self.assertEqual(m["state"], "patrol")

    def test_bat_tu_thi_khong_hit(self):
        sc = {"random_fish": False, "player": {"pos": [51, 15], "invuln_ticks": 10}, "monsters": [croc()]}
        s, evs = play(sc, 5)
        self.assertNotIn("monster_hit", names(evs))
        self.assertNotEqual(s.sim.monsters[0]["state"], "recoil")

    def test_mau_ve_0_do_quai_thi_ngat(self):
        sc = {"random_fish": False, "hold": ["ca_loc", "bong_sung", "ca_linh"],
              "player": {"pos": [51, 15], "hp": 1}, "monsters": [croc()]}
        s, evs = play(sc, 3)
        self.assertEqual(names(evs), ["monster_hit", "faint", "gather_end"])
        self.assertEqual(evs[0]["data"]["lost"], ["ca_linh"])
        self.assertEqual(evs[1]["data"], {"cause": "monster", "lost": ["bong_sung", "ca_loc"], "hp": 0})
        self.assertEqual(evs[2]["data"]["reason"], "fainted")
        self.assertEqual(evs[2]["data"]["inventory"], {"items": {}})

    def test_snapshot_co_monsters(self):
        snap = play({}, 0)[0].snapshot()
        self.assertEqual(set(snap["monsters"][0]), {"id", "kind", "pos", "waypoints", "target_idx", "state",
                                                    "state_ticks_left", "recoil_dir"})
        self.assertEqual(snap["monsters"][0]["target_idx"], 1)


class ScenarioExit2(unittest.TestCase):
    def test_monster_sai_thi_ma_2(self):
        bad = [croc(kind="ca_map"), croc(wps=((50, 15),)), croc(state="recoil", state_ticks_left=0),
               croc(state="recoil", state_ticks_left=5, recoil_dir=[3, 0]), croc(target_idx=2)]
        with Workdir() as w:
            for m in bad:
                sc = write_json(w.path("sc.json"), {"gather": {"monsters": [m]}})
                code, _ = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1", "--scenario", sc,
                                       "--out", w.path("o.jsonl"))
                self.assertEqual(code, 2, m)


if __name__ == "__main__":
    unittest.main()
