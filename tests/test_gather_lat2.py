"""Gather lát 2 (hộp đen): hái nút ở mặt nước, mọc lại, bắt cá (dưới nước, hồi chiêu), giỏ LIFO + hold_full.

Chỉ chạy `headless_cmd` và đọc JSONL; số liệu đọc từ game.contract.json.
Giả định đang chờ PO (docs/clarify.md): #1 tên trường `data`, #2 giỏ thiếu chỗ -> nhận một phần,
#8 vung `catch` hụt vẫn tính hồi chiêu.
"""

import json
import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

with open("game.contract.json", encoding="utf-8") as _f:
    G = json.load(_f)["tuning"]["gather"]
TICK = 60


def run(w, scenario, inputs, ticks=5, name="o"):
    sc = write_json(w.path(f"{name}_sc.json"), {"gather": {"random_fish": False, "nodes": [], **scenario}})
    inp = write_json(w.path(f"{name}_in.json"), frames(*inputs))
    out = w.path(f"{name}.jsonl")
    code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", str(ticks), "--scenario", sc,
                             "--inputs", inp, "--out", out)
    assert code == 0, err
    return read_jsonl(out)


def node(id_, kind, x, **kw):
    return {"id": id_, "kind": kind, "pos": [x, 0], **kw}


def fish(id_, kind, x, d):
    return {"id": id_, "kind": kind, "pos": [x, d], "heading_deg": 0}


PRESS_E = {"tick": 0, "interact": True}
PRESS_CATCH = {"tick": 0, "catch": True}


class Harvest(unittest.TestCase):
    def test_hai_nut_o_mat_nuoc(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [20, 0]}, "nodes": [node("N1", "bong_sung", 21)]}, [PRESS_E])
            ev = events(rows, "gather")
            self.assertEqual(len(ev), 1)
            self.assertEqual(ev[0]["data"], {"node_id": "N1", "kind": "bong_sung", "count": G["node_yield"]})
            s = snapshots(rows)[-1]
            self.assertEqual(s["hold"], ["bong_sung"] * G["node_yield"])
            n1 = s["nodes"][0]
            self.assertFalse(n1["ready"])
            self.assertGreater(n1["regrow_ticks"], G["regrow_s"] * TICK - 10)

    def test_chon_nut_gan_nhat_hoa_thi_id_nho(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [20, 0]},
                           "nodes": [node("N2", "bong_sung", 19), node("N1", "bong_dien_dien", 21)]}, [PRESS_E])
            self.assertEqual(events(rows, "gather")[0]["data"]["node_id"], "N1")
            rows = run(w, {"player": {"pos": [20, 0]},
                           "nodes": [node("N1", "bong_sung", 21.5), node("N2", "bong_dien_dien", 20.5)]},
                       [PRESS_E], name="b")
            self.assertEqual(events(rows, "gather")[0]["data"]["node_id"], "N2")

    def test_ngoai_ban_kinh_khong_hai(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [20, 0]},
                           "nodes": [node("N1", "bong_sung", 20 + G["interact_radius"] + 0.5)]}, [PRESS_E])
            self.assertEqual(events(rows, "gather"), [])

    def test_duoi_nuoc_khong_hai(self):
        with Workdir() as w:
            d = G["surface_depth"] + 0.5
            rows = run(w, {"player": {"pos": [20, d]}, "nodes": [node("N1", "bong_sung", 20)]}, [PRESS_E])
            self.assertEqual(events(rows, "gather"), [])
            self.assertEqual(snapshots(rows)[-1]["hold"], [])

    def test_nut_chua_moc_khong_hai_moc_xong_thi_hai(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [20, 0]}, "nodes": [node("N1", "bong_sung", 21, regrow_ticks=5)]},
                       [PRESS_E, {"tick": 1, "interact": False}, {"tick": 10, "interact": True}], ticks=15)
            self.assertEqual(len(events(rows, "node_regrown")), 1)
            ev = events(rows, "gather")
            self.assertEqual(len(ev), 1)
            self.assertGreater(ev[0]["tick"], events(rows, "node_regrown")[0]["tick"])

    def test_gio_day_hold_full_nut_giu_nguyen(self):
        with Workdir() as w:
            full = ["ca_loc"] * G["hold_capacity"]
            rows = run(w, {"player": {"pos": [20, 0]}, "hold": full, "nodes": [node("N1", "bong_sung", 21)]},
                       [PRESS_E])
            self.assertEqual(events(rows, "gather"), [])
            self.assertEqual([e["data"] for e in events(rows, "hold_full")], [{"kind": "bong_sung"}])
            s = snapshots(rows)[-1]
            self.assertEqual(s["hold"], full)
            self.assertTrue(s["nodes"][0]["ready"])

    def test_ben_xet_truoc_hai(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": G["dock_pos"]}, "nodes": [node("N1", "bong_sung", G["dock_pos"][0] + 1)]},
                       [PRESS_E])
            self.assertEqual(events(rows, "gather"), [])
            self.assertEqual(events(rows, "gather_end")[0]["data"]["reason"], "docked")

    def test_gio_lifo_va_kho_khi_cap_ben(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [20, 0]}, "hold": ["ca_loc"], "nodes": [node("N1", "bong_sung", 21)]},
                       [PRESS_E])
            self.assertEqual(snapshots(rows)[-1]["hold"], ["ca_loc", "bong_sung"])  # mới nhất ở cuối


class Catch(unittest.TestCase):
    def test_bat_ca_duoi_nuoc(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [30, 10]},
                           "fish": [fish("F1", "ca_linh", 31, 10), fish("F2", "ca_loc", 60, 16)]}, [PRESS_CATCH])
            ev = events(rows, "fish_caught")
            self.assertEqual([e["data"] for e in ev],
                             [{"fish_id": "F1", "kind": "ca_linh", "count": G["fish_yield"]["ca_linh"]}])
            s = snapshots(rows)[-1]
            self.assertEqual(s["hold"], ["ca_linh"] * G["fish_yield"]["ca_linh"])
            self.assertEqual([f["id"] for f in s["fish"]], ["F2"])  # đàn bị bắt biến mất
            self.assertGreater(s["player"]["catch_cd_ticks"], 0)

    def test_o_mat_nuoc_khong_bat(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [30, 0]}, "fish": [fish("F1", "ca_loc", 30, 1)]}, [PRESS_CATCH])
            self.assertEqual(events(rows, "fish_caught"), [])
            self.assertEqual(snapshots(rows)[-1]["player"]["catch_cd_ticks"], 0)

    def test_ngoai_ban_kinh_khong_bat(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [30, 10]},
                           "fish": [fish("F1", "ca_loc", 30 + G["catch_radius"] + 0.5, 10)]}, [PRESS_CATCH])
            self.assertEqual(events(rows, "fish_caught"), [])

    def test_hoi_chieu(self):
        cd = int(round(G["catch_cooldown_s"] * TICK))
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [30, 10]},
                           "fish": [fish("F1", "ca_loc", 30, 10), fish("F2", "ca_loc", 31, 10)]},
                       [PRESS_CATCH, {"tick": 1, "catch": False},
                        {"tick": cd // 2, "catch": True}, {"tick": cd // 2 + 1, "catch": False},
                        {"tick": cd + 5, "catch": True}], ticks=cd + 10)
            ev = events(rows, "fish_caught")
            self.assertEqual([e["data"]["fish_id"] for e in ev], ["F1", "F2"])
            self.assertGreaterEqual(ev[1]["tick"] - ev[0]["tick"], cd)

    def test_ca_nhieu_hon_cho_trong_nhan_mot_phan(self):
        with Workdir() as w:
            hold = ["bong_sung"] * (G["hold_capacity"] - 2)
            rows = run(w, {"player": {"pos": [30, 10]}, "hold": hold, "fish": [fish("F1", "ca_linh", 30, 10)]},
                       [PRESS_CATCH])
            names = [r["name"] for r in events(rows) if r["name"] in ("fish_caught", "hold_full")]
            self.assertEqual(names, ["fish_caught", "hold_full"])
            self.assertEqual(events(rows, "fish_caught")[0]["data"]["count"], 2)
            self.assertEqual(snapshots(rows)[-1]["hold"], hold + ["ca_linh", "ca_linh"])

    def test_gio_day_ca_o_lai(self):
        with Workdir() as w:
            rows = run(w, {"player": {"pos": [30, 10]}, "hold": ["bong_sung"] * G["hold_capacity"],
                           "fish": [fish("F1", "ca_loc", 30, 10)]}, [PRESS_CATCH])
            self.assertEqual(events(rows, "fish_caught"), [])
            self.assertEqual(len(events(rows, "hold_full")), 1)
            self.assertEqual([f["id"] for f in snapshots(rows)[-1]["fish"]], ["F1"])


if __name__ == "__main__":
    unittest.main()
