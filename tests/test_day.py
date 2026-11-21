"""--mode day, Shop, pause (Ticket-02 mục 2, Test Contract v1.1 mục 4.1–4.5). Hộp đen qua headless_cmd."""

import json
import unittest

from helpers import count, items, Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

with open("game.contract.json", encoding="utf-8") as _f:
    TUNING = json.load(_f)["tuning"]
G, Q, SHOP = TUNING["gather"], TUNING["quan"], TUNING["shop"]
GATHER_T = int(G["duration_s"] * 60)
QUAN_T = int(Q["duration_s"] * 60)
DAY_T = GATHER_T + QUAN_T + SHOP["max_ticks"]
DOCK_NOW = {"tick": 0, "interact": True}


def day(w, scenario=None, inputs=None, days=None, ticks=DAY_T + 5, every=1000):
    args = ["--mode", "day", "--seed", "1", "--ticks", str(ticks), "--out", w.path("d.jsonl"), "--snapshot-every", str(every)]
    if days is not None:
        args += ["--days", str(days)]
    if scenario is not None:
        args += ["--scenario", write_json(w.path("sc.json"), scenario)]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    code, err = run_headless(*args)
    return code, err, (read_jsonl(w.path("d.jsonl")) if code == 0 else None)


def ev_names(rows):
    return [(r["tick"], r["phase"], r["name"]) for r in events(rows)
            if r["name"] not in ("fish_spawned", "no_dish", "customer_arrived", "customer_left")]


class DayLoop(unittest.TestCase):
    def test_mot_ngay_tron_ven(self):
        with Workdir() as w:
            code, err, rows = day(w)
            self.assertEqual(code, 0, err)
            self.assertEqual(ev_names(rows), [
                (0, "gather", "day_start"), (0, "gather", "day_plan"), (0, "gather", "phase_start"),
                (GATHER_T, "gather", "gather_end"), (GATHER_T, "quan", "phase_start"),
                (GATHER_T + QUAN_T, "quan", "quan_end"), (GATHER_T + QUAN_T, "shop", "phase_start"),
                (DAY_T, "shop", "shop_end")])
            self.assertTrue(all(r["day"] == 1 for r in events(rows)))
            plan = events(rows, "day_plan")[0]["data"]
            self.assertEqual(plan, {k: TUNING["day_plan"][0][k] for k in ("dishes", "ingredients")})
            end = rows[-1]
            self.assertEqual((end["reason"], end["days_completed"], end["ticks"]), ("days_complete", 1, DAY_T))

    def test_cap_ben_mo_quan_voi_kho_ban_giao(self):
        with Workdir() as w:
            sc = {"gather": {"hold": items("ca_loc", "bong_sung", "bong_sung"), "random_fish": False}}
            code, err, rows = day(w, sc, [DOCK_NOW], ticks=1, every=1)
            self.assertEqual(code, 0, err)
            self.assertEqual([(r["phase"], r["name"]) for r in events(rows) if r["tick"] == 1],
                             [("gather", "gather_end"), ("quan", "phase_start")])
            s = snapshots(rows)[-1]
            self.assertEqual((s["phase"], s["phase_tick"]), ("quan", 0))
            self.assertEqual(count(s["stock"]), {"bong_sung": 2, "ca_loc": 1})
            self.assertEqual([e["id"] for e in s["stock"]], ["I1", "I2", "I3"])  # bàn giao giữ id
            for k in ("day", "day_plan", "upgrades", "active_upgrades"):
                self.assertIn(k, s)

    def test_khach_chi_goi_mon_trong_ke_hoach(self):
        with Workdir() as w:
            hold = items(*["ca_loc"] * 3 + ["ca_keo"] * 4)  # ca_keo_nuong không thuộc kế hoạch D1
            code, err, rows = day(w, {"gather": {"hold": hold, "random_fish": False}}, [DOCK_NOW],
                                  ticks=1 + Q["first_customer_tick"] + 900 * 3)
            self.assertEqual(code, 0, err)
            dishes = {e["data"]["dish_id"] for e in events(rows, "customer_arrived")}
            self.assertTrue(dishes)
            self.assertTrue(dishes <= set(TUNING["day_plan"][0]["dishes"]), dishes)


class Shop(unittest.TestCase):
    SC = {"day": {"money": 200, "earned": 200}, "gather": {"random_fish": False}, "quan": {"time_left_ticks": 1}}

    def test_mua_nang_cap_va_hieu_luc_tu_ngay_ke(self):
        # tick 1 cập bến -> quán 1 tick -> Shop từ tick 2
        inputs = [DOCK_NOW, {"tick": 2, "buy": "oxygen"}, {"tick": 3, "buy": "hp"}, {"tick": 4, "buy": "xyz"},
                  {"tick": 5, "buy": "oxygen", "shop_done": True}]
        with Workdir() as w:
            code, err, rows = day(w, self.SC, inputs, days=2, ticks=7, every=1)
            self.assertEqual(code, 0, err)
            up = SHOP["upgrades"]
            self.assertEqual(events(rows, "bought")[0]["data"],
                             {"upgrade": "oxygen", "level": 1, "price": up["oxygen"][0]["price"], "money": 0})
            self.assertEqual([e["data"] for e in events(rows, "buy_failed")],
                             [{"action": "hp", "reason": "funds"}, {"action": "xyz", "reason": "unknown"},
                              {"action": "oxygen", "reason": "funds"}])
            self.assertEqual(events(rows, "shop_end")[0]["data"], {"reason": "done"})
            self.assertEqual(events(rows, "shop_end")[0]["tick"], 6)
            day2 = [r for r in events(rows) if r["tick"] == 6]
            self.assertEqual([(r["day"], r["name"]) for r in day2],
                             [(1, "buy_failed"), (1, "shop_end"), (2, "day_start"), (2, "day_plan"),
                              (2, "phase_start")])  # buy xử lý trước cạnh shop_done (mục 4.5)
            s = snapshots(rows)[-1]
            self.assertEqual((s["day"], s["upgrades"], s["active_upgrades"]), (2, {"oxygen": 1}, {"oxygen": 1}))
            self.assertEqual(s["player"]["oxygen_max_ticks"], int(up["oxygen"][0]["oxygen_max_s"] * 60))
            self.assertEqual(s["money"], 0)
            self.assertEqual(s["earned"], 200)

    def test_cap_vua_mua_chua_hieu_luc_trong_shop(self):
        with Workdir() as w:
            code, err, rows = day(w, self.SC, [DOCK_NOW, {"tick": 2, "buy": "oxygen"}], ticks=4, every=1)
            self.assertEqual(code, 0, err)
            s = snapshots(rows)[-1]
            self.assertEqual((s["phase"], s["upgrades"], s["active_upgrades"]), ("shop", {"oxygen": 1}, {}))

    def test_da_toi_da(self):
        sc = dict(self.SC, day={"money": 999, "earned": 999, "upgrades": {"hp": len(SHOP["upgrades"]["hp"])}})
        with Workdir() as w:
            code, err, rows = day(w, sc, [DOCK_NOW, {"tick": 2, "buy": "hp"}], ticks=4, every=1)
            self.assertEqual(code, 0, err)
            self.assertEqual(events(rows, "buy_failed")[0]["data"], {"action": "hp", "reason": "max_level"})

    def test_ngay_3_co_m2(self):
        with Workdir() as w:
            inputs = []
            for d in range(3):  # mỗi Ngày 3 tick: cập bến ngay, quán 1 tick, đóng Shop ngay
                t0 = 3 * d
                inputs += [{"tick": t0, "interact": True, "shop_done": False}, {"tick": t0 + 1, "interact": False},
                           {"tick": t0 + 2, "shop_done": True}]
            code, err, rows = day(w, self.SC, inputs, days=3, ticks=6, every=1)  # tick 6: Ngày 3 vừa dựng gather
            self.assertEqual(code, 0, err)
            s = snapshots(rows)[-1]
            self.assertEqual(s["day"], 3)
            self.assertEqual([m["id"] for m in s["monsters"]], ["M1", "M2"])


class Pause(unittest.TestCase):
    def test_pause_dung_moi_timer(self):
        inputs = [{"tick": 5, "pause": True}, {"tick": 6, "pause": False}, {"tick": 10, "pause": True}]
        with Workdir() as w:
            code, err, rows = day(w, None, inputs, ticks=12, every=1)
            self.assertEqual(code, 0, err)
            self.assertEqual([(e["tick"], e["name"]) for e in events(rows) if e["name"] in ("paused", "resumed")],
                             [(6, "paused"), (11, "resumed")])
            by_tick = {s["tick"]: s for s in snapshots(rows)}
            self.assertEqual(by_tick[8]["state"], "paused")
            self.assertEqual(by_tick[8]["sim_tick"], 5)
            self.assertEqual(by_tick[8]["time_left_ticks"], GATHER_T - 5)
            self.assertEqual(by_tick[11]["sim_tick"], 6)  # cạnh resume chạy gameplay ngay bước đó
            self.assertEqual(rows[-1]["sim_tick"], 7)

    def test_pause_o_mode_gather(self):
        with Workdir() as w:
            sc = write_json(w.path("in.json"), frames({"tick": 0, "pause": True}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "3", "--inputs", sc,
                                     "--out", w.path("g.jsonl"), "--snapshot-every", "1")
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("g.jsonl"))
            self.assertEqual(snapshots(rows)[-1]["state"], "paused")
            self.assertEqual(rows[-1]["sim_tick"], 0)


class Exit2(unittest.TestCase):
    def test_tham_so_va_scenario_sai(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            for extra in (["--days", "0"], ["--days", "6"]):
                self.assertEqual(run_headless("--mode", "day", "--seed", "1", "--ticks", "1", "--out", out, *extra)[0], 2)
            self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "1", "--out", out, "--days", "2")[0], 2)
            for sc in ({"quan": {"stock": {"ca_loc": 1}}}, {"quan": {"reputation": 4}},
                       {"day": {"money": 300, "earned": 200}}, {"day": {"upgrades": {"oxygen": 9}}},
                       {"day": {"day_plan": [{"day": 1, "dishes": {"ca_loc_nuong_trui": 1}, "ingredients": {"ca_loc": 2}}]}}):
                p = write_json(w.path("sc.json"), sc)
                self.assertEqual(run_headless("--mode", "day", "--seed", "1", "--ticks", "1", "--scenario", p,
                                              "--out", out)[0], 2, sc)
            self.assertEqual(run_headless("--mode", "day", "--seed", "1", "--ticks", "1", "--inventory-out",
                                          w.path("k.json"), "--out", out)[0], 2)


class Determinism(unittest.TestCase):
    def test_hai_ngay_giong_tung_byte(self):
        outs = []
        for _ in range(2):
            with Workdir() as w:
                code, err, _ = day(w, None, None, days=2, ticks=2 * DAY_T, every=500)
                self.assertEqual(code, 0, err)
                outs.append(open(w.path("d.jsonl"), encoding="utf-8").read())
        self.assertEqual(outs[0], outs[1])


if __name__ == "__main__":
    unittest.main()
