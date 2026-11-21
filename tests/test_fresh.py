"""v1.2 độ tươi (Ticket-03 mục 1): kho cá thể, hao tươi, ươn, giữ theo id, giá theo tươi, bàn giao."""

import json
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import InputPlayer, LiveInputs
from chonoi.runner import Session

from helpers import (Workdir, close, events, fresh_price, frames, items, read_jsonl, run_headless, snapshots,
                     write_json)

TUNING = load_contract()["tuning"]
FR = TUNING["freshness"]
MENU = TUNING["menu"]
STOVE = TUNING["quan"]["stoves"][0]["pos"]
QUIET_GATHER = {"random_fish": False, "monsters": []}


def item(iid, kind, fresh):
    return {"id": iid, "kind": kind, "fresh": fresh}


def gather(scenario, ticks, inputs=()):
    s = Session("gather", TUNING, {**QUIET_GATHER, **scenario}, 1)
    ip, evs = InputPlayer(list(inputs)), []
    while s.tick < ticks and not s.done:
        evs.extend(s.step(ip.advance(s.tick)))
    return s, evs


def quan(scenario, ticks, interact_at=()):
    s = Session("quan", TUNING, {"random_customers": False, **scenario}, 1)
    li, evs = LiveInputs(), []
    for k in range(ticks):
        li.set(interact=k in interact_at)
        evs.extend(s.step(li.advance()))
        li.set(interact=False)
    return s, evs


class Manifest(unittest.TestCase):
    def test_contract_v12(self):
        c = load_contract()
        self.assertEqual(c["contract_version"], "1.2")
        self.assertEqual(FR, {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30})


class HoldDecay(unittest.TestCase):
    def test_vi_du_nguong_cua_ticket(self):
        _, evs = gather({"hold": [item("I1", "ca_linh", 30)]}, 1)
        self.assertEqual([(e["tick"], e["name"], e["data"]) for e in evs],
                         [(1, "spoiled", {"item_id": "I1", "kind": "ca_linh", "location": "hold"})])

    def test_gio_hao_0_5_moi_giay_va_ươn_dung_mot_lan(self):
        s, evs = gather({"hold": [item("I1", "ca_loc", 30.5)]}, 120)
        self.assertTrue(close(s.snapshot()["hold"][0]["fresh"], 30.5 - 1.0, 1e-9))
        self.assertEqual([e["tick"] for e in evs if e["name"] == "spoiled"], [61])  # 30.5 - 61×(0.5/60) < 30

    def test_hang_moi_100_hao_tu_buoc_sau_va_id_noi_tiep(self):
        sc = {"player": {"pos": [20, 0]}, "hold": [item("I7", "ca_loc", 100)],
              "nodes": [{"id": "N1", "kind": "bong_sung", "pos": [21, 0]}]}
        s, _ = gather(sc, 1, [{"tick": 0, "interact": True}])
        hold = s.snapshot()["hold"]
        self.assertEqual([(e["id"], e["kind"]) for e in hold], [("I7", "ca_loc"), ("I8", "bong_sung")])
        self.assertEqual(hold[1]["fresh"], 100)
        self.assertTrue(close(hold[0]["fresh"], 100 - 0.5 / 60, 1e-9))


class QuanStock(unittest.TestCase):
    def test_kho_hao_0_25_moi_giay_ke_ca_hang_giu(self):
        sc = {"stock": [item("I1", "ca_loc", 30.25)], "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]}
        s, evs = quan(sc, 60)
        self.assertTrue(close(s.snapshot()["stock"][0]["fresh"], 30.0, 1e-9))
        self.assertEqual([e for e in evs if e["name"] == "spoiled"], [])
        _, evs = quan(sc, 61)
        sp = [e for e in evs if e["name"] == "spoiled"]
        self.assertEqual([(e["tick"], e["data"]["location"]) for e in sp], [(61, "stock")])

    def test_giu_tuoi_nhat_hoa_theo_id(self):
        sc = {"stock": [item("I1", "ca_loc", 50), item("I2", "ca_loc", 90), item("I3", "ca_loc", 90)],
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]}
        s, _ = quan(sc, 0)
        self.assertEqual(s.snapshot()["customers"][0]["reserved"], ["I2"])

    def test_giu_vua_uon_thi_giu_lai_mot_lan(self):
        sc = {"stock": [item("I1", "ca_loc", 30), item("I2", "ca_loc", 80)],
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]}]}
        s, evs = quan(sc, 1)
        self.assertEqual([e["name"] for e in evs], ["spoiled"])
        c = s.snapshot()["customers"][0]
        self.assertEqual((c["order_status"], c["reserved"]), ("reserved", ["I2"]))

    def test_khong_du_hang_tuoi_thi_unfulfillable_khach_van_cho(self):
        sc = {"stock": [item("I1", "ca_loc", 30)],
              "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]}
        s, _ = quan(sc, 1)
        c = s.snapshot()["customers"][0]
        self.assertEqual((c["state"], c["order_status"], c["reserved"]), ("waiting", "unfulfillable", []))
        self.assertEqual(len(s.snapshot()["stock"]), 1)  # hàng ươn vẫn chiếm chỗ trong kho

    def test_hang_uon_khong_dung_nau(self):
        s, evs = quan({"stock": [item("I1", "ca_loc", 20)], "random_customers": True},
                      TUNING["quan"]["first_customer_tick"])
        self.assertEqual([e["name"] for e in evs], ["no_dish"])

    def test_gia_theo_tuoi_va_items_ca_the(self):
        dish = "lau_ca_linh_dien_dien"
        stock = [item("I1", "ca_linh", 50), item("I2", "ca_linh", 60), item("I3", "ca_linh", 70),
                 item("I4", "bong_dien_dien", 80)]
        sc = {"player": {"pos": STOVE}, "stock": stock, "customers": [{"id": "C1", "table_id": "T1", "dish_id": dish}]}
        s, evs = quan(sc, 1, interact_at={0})
        d = [e for e in evs if e["name"] == "cook_started"][0]["data"]
        units = [int(e["fresh"] * 240) - 1 for e in stock]  # hao 1 đơn vị (1/240 điểm) ở bước 1
        self.assertEqual(d["base_price"], fresh_price(MENU[dish]["price"], units))
        self.assertEqual(d["base_price"], 77)  # floor(120 × 64.99583 / 100)
        self.assertEqual([e["id"] for e in d["items"]], ["I4", "I1", "I2", "I3"])
        self.assertEqual(s.snapshot()["stoves"][0]["dish"]["base_price"], 77)


class Handoff(unittest.TestCase):
    def test_smoke_ban_giao_file(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"gather": {"hold": [item("I1", "ca_linh", 100)], **QUIET_GATHER}})
            inp = write_json(w.path("in.json"), frames({"tick": 0, "interact": True}))
            inv = w.path("kho.json")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1", "--scenario", sc, "--inputs", inp,
                                     "--inventory-out", inv, "--out", w.path("g.jsonl"))
            self.assertEqual(code, 0, err)
            with open(inv, encoding="utf-8") as f:
                saved = json.load(f)["items"]
            self.assertEqual(saved, [item("I1", "ca_linh", 100 - 0.5 / 60)])  # đủ chính xác khi đọc lại
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", inv,
                                     "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            st = snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"]
            self.assertEqual([(e["id"], e["kind"]) for e in st], [("I1", "ca_linh")])
            self.assertTrue(close(st[0]["fresh"], saved[0]["fresh"], 0.01))

    def test_day_ngay_ke_cap_id_moi_va_shop_khong_hao(self):
        sc = {"gather": {"hold": [item("I1", "ca_loc", 100)], **QUIET_GATHER}, "quan": {"time_left_ticks": 1}}
        inputs = [{"tick": 0, "interact": True}, {"tick": 1, "interact": False}, {"tick": 10, "shop_done": True},
                  {"tick": 11, "shop_done": False}]
        with Workdir() as w:
            code, err = run_headless("--mode", "day", "--seed", "1", "--days", "2", "--ticks", "11", "--snapshot-every", "1",
                                     "--scenario", write_json(w.path("sc.json"), sc),
                                     "--inputs", write_json(w.path("in.json"), frames(*inputs)), "--out", w.path("d.jsonl"))
            self.assertEqual(code, 0, err)
            snaps = {s["tick"]: s for s in snapshots(read_jsonl(w.path("d.jsonl")))}
            self.assertEqual(snaps[3]["phase"], "shop")
            self.assertEqual(snaps[3]["stock"], snaps[9]["stock"])  # hàng thô ở Shop không hao
            day2 = snaps[11]
            self.assertEqual((day2["day"], day2["phase"]), (2, "gather"))
            self.assertEqual([(e["id"], e["kind"], e["fresh"]) for e in day2["hold"]], [("I2", "ca_loc", 100)])


class ScenarioExit2(unittest.TestCase):
    BAD = [
        {"gather": {"hold": ["ca_loc"]}},
        {"gather": {"hold": [item("I1", "ca_loc", 120)]}},
        {"quan": {"stock": [item("I1", "ca_loc", 50), item("I1", "ca_loc", 50)]}},
        {"quan": {"stock": [item("I1", "ca_loc", 20)],
                  "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]}]}},
        {"quan": {"stock": [item("I1", "ca_loc", 50)],
                  "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I9"]}]}},
        {"quan": {"stock": [item("I1", "ca_loc", 50)],
                  "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]},
                                {"id": "C2", "table_id": "T2", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]}]}},
    ]

    def test_ma_2(self):
        with Workdir() as w:
            for sc in self.BAD:
                mode = next(iter(sc))
                p = write_json(w.path("sc.json"), sc)
                code, _ = run_headless("--mode", mode, "--seed", "1", "--ticks", "1", "--scenario", p, "--out", w.path("o.jsonl"))
                self.assertEqual(code, 2, sc)


if __name__ == "__main__":
    unittest.main()
