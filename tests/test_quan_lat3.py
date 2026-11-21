"""Quán lát 3: khách đến theo lịch, chọn món nấu được, giữ chỗ nguyên liệu,
giảm kiên nhẫn, bỏ đi (customer_left), no_dish, suy ra reserved và kiểm mâu thuẫn scenario.

Kiểm cả qua Session (trong tiến trình) và hộp đen qua headless_cmd.
Số liệu đọc từ game.contract.json.
"""

import json
import os
import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.inputs import InputPlayer
from chonoi.runner import Session

from helpers import Workdir, events, read_jsonl, run_headless, snapshots, write_json

TUNING = load_contract()["tuning"]
Q = TUNING["quan"]
MENU = TUNING["menu"]
TICK = 60
FIRST_TICK = int(Q["first_customer_tick"])
INTERVAL_TICKS = int(round(Q["customer_interval_s"] * TICK))
PATIENCE_TICKS = int(round(Q["patience_s"] * TICK))


def play_quan(scenario, ticks, seed=1, frames=()):
    """Chạy `ticks` bước chế độ quan qua Session. Trả (session, danh sách event)."""
    s = Session("quan", TUNING, dict(scenario), seed)
    ip = InputPlayer(list(frames))
    evs = []
    while s.tick < ticks and not s.done:
        evs.extend(s.step(ip.advance(s.tick)))
    return s, evs


def names(evs):
    return [e["name"] for e in evs]


class SpawnAndReserve(unittest.TestCase):
    def test_khach_den_dung_first_customer_tick_va_giu_cho(self):
        s, evs = play_quan({"stock": {"ca_loc": 1}}, FIRST_TICK)
        arr = [e for e in evs if e["name"] == "customer_arrived"]
        self.assertEqual(len(arr), 1)
        self.assertEqual(arr[0]["tick"], FIRST_TICK)
        self.assertEqual(arr[0]["data"], {
            "order_id": "C1",
            "table_id": "T1",
            "dish_id": "ca_loc_nuong_trui",
        })
        self.assertEqual(len(s.sim.customers), 1)
        c1 = s.sim.customers[0]
        self.assertEqual(c1["state"], "waiting")
        self.assertEqual(c1["patience_ticks_left"], PATIENCE_TICKS)
        self.assertEqual(c1["reserved"], {"ca_loc": 1})
        # Kho gốc vẫn còn nguyên (chưa nấu), nhưng kho khả dụng đã bằng 0
        self.assertEqual(s.sim.stock, {"ca_loc": 1})
        self.assertEqual(s.sim._available(), {})

    def test_khong_du_nguyen_lieu_phat_no_dish(self):
        s, evs = play_quan({"stock": {"bong_sung": 1}}, FIRST_TICK)  # gỏi bông súng cần 2
        self.assertEqual(names(evs), ["no_dish"])
        self.assertEqual(evs[0]["tick"], FIRST_TICK)
        self.assertEqual(evs[0]["data"], {})
        self.assertEqual(s.sim.customers, [])

    def test_giu_cho_lam_khach_sau_het_mon_phat_no_dish(self):
        # Mở rộng bàn T1 (hoặc giải phóng bàn không giải phóng kho): dùng 1 cá lóc, C1 giữ chỗ ở tick 120;
        # giả sử C1 chuyển sang eating mà kho chỉ có 1 cá lóc đã giữ chỗ -> kiểm _available() chặn món
        s = Session("quan", TUNING, {"stock": {"ca_loc": 1, "bong_sung": 2}}, seed=1)
        self.assertEqual(s.sim._cookable_dishes(), ["ca_loc_nuong_trui", "goi_bong_sung"])
        ip = InputPlayer([])
        while s.tick < FIRST_TICK:
            s.step(ip.advance(s.tick))
        self.assertEqual(len(s.sim.customers), 1)
        chosen = s.sim.customers[0]["dish_id"]
        remaining = [d for d in ("ca_loc_nuong_trui", "goi_bong_sung") if d != chosen]
        self.assertEqual(s.sim._cookable_dishes(), remaining)

    def test_het_ban_trong_khong_sinh_them_va_khong_phat_no_dish(self):
        # v1.1 có 4 bàn: cho khách ngồi kín cả 4 bàn, kho còn dư 1 cá lóc -> tới lượt khách không sinh, không no_dish
        tables = [t["id"] for t in Q["tables"]]
        custs = [{"id": f"C{i + 1}", "table_id": tb, "dish_id": "ca_loc_nuong_trui"} for i, tb in enumerate(tables)]
        s, evs = play_quan({"stock": {"ca_loc": len(tables) + 1}, "customers": custs}, FIRST_TICK + 1)
        self.assertEqual(evs, [])
        self.assertEqual(len(s.sim.customers), len(tables))

    def test_random_customers_false_tat_sinh_khach_theo_lich(self):
        s, evs = play_quan({"stock": {"ca_loc": 2}, "random_customers": False}, FIRST_TICK + INTERVAL_TICKS)
        self.assertEqual(evs, [])
        self.assertEqual(s.sim.customers, [])


class PatienceAndLeave(unittest.TestCase):
    def test_giam_kien_nhan_moi_tick_va_bo_di_khi_ve_0(self):
        sc = {
            "stock": {"ca_loc": 1},
            "random_customers": False,
            "customers": [{
                "id": "C1",
                "table_id": "T1",
                "dish_id": "ca_loc_nuong_trui",
                "state": "waiting",
                "patience_ticks_left": 3,
            }],
        }
        s, evs = play_quan(sc, 2)
        self.assertEqual(evs, [])
        self.assertEqual(s.sim.customers[0]["patience_ticks_left"], 1)
        self.assertEqual(s.sim._available(), {})  # vẫn đang giữ chỗ

        # Bước thứ 3: patience về 0 -> customer_left, nhả giữ chỗ, trừ uy tín
        evs_step3 = s.step(InputPlayer([]).advance(2))
        self.assertEqual(names(evs_step3), ["customer_left"])
        self.assertEqual(evs_step3[0]["tick"], 3)
        self.assertEqual(evs_step3[0]["data"], {"order_id": "C1", "table_id": "T1", "reason": "patience",
                                                 "reputation": Q["reputation_initial"] + Q["left_reputation_delta"]})
        self.assertEqual(s.sim.customers, [])
        self.assertEqual(s.sim._available(), {"ca_loc": 1})
        self.assertAlmostEqual(s.sim.reputation, Q["reputation_initial"] + Q["left_reputation_delta"])

    def test_uy_tin_kep_khong_am_khi_nhieu_khach_bo_di(self):
        sc = {
            "stock": {"ca_loc": 1},
            "random_customers": False,
            "reputation": 0.2,
            "customers": [{
                "id": "C1",
                "table_id": "T1",
                "dish_id": "ca_loc_nuong_trui",
                "state": "waiting",
                "patience_ticks_left": 1,
            }],
        }
        s, evs = play_quan(sc, 1)
        self.assertEqual(names(evs), ["customer_left"])
        self.assertEqual(s.sim.reputation, float(Q["reputation_min"]))

    def test_khach_eating_khong_bi_tru_kien_nhan(self):
        sc = {
            "random_customers": False,
            "customers": [{
                "id": "C1",
                "table_id": "T1",
                "dish_id": "ca_loc_nuong_trui",
                "state": "eating",
                "patience_ticks_left": 2,
                "eat_ticks_left": 100,
                "base_price": 60,
                "tip": 0,
            }],
        }
        s, evs = play_quan(sc, 5)
        self.assertEqual(evs, [])
        self.assertEqual(s.sim.customers[0]["patience_ticks_left"], 2)

    def test_khach_cu_bo_di_nha_ban_va_kho_kip_cho_khach_moi_cung_tick(self):
        # C1 đến ở tick 120 (patience 3600 = 4 * 900); ở tick 3720 C1 bỏ đi ở bước 2, C2 đến ở bước 7 cùng tick
        s, evs = play_quan({"stock": {"ca_loc": 1}}, FIRST_TICK + PATIENCE_TICKS)
        ev_3720 = [e for e in evs if e["tick"] == FIRST_TICK + PATIENCE_TICKS]
        self.assertEqual([e["name"] for e in ev_3720], ["customer_left", "customer_arrived"])
        self.assertEqual(ev_3720[0]["data"]["order_id"], "C1")
        self.assertEqual(ev_3720[1]["data"]["order_id"], "C2")
        self.assertEqual(len(s.sim.customers), 1)
        self.assertEqual(s.sim.customers[0]["id"], "C2")
        self.assertEqual(s.sim.customers[0]["reserved"], {"ca_loc": 1})


class ScenarioValidationAndHeadless(unittest.TestCase):
    def test_khach_waiting_giu_cho_qua_kho_exit_2(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            # Kho rỗng, không có món trên bếp/tay mà có khách waiting -> mâu thuẫn mức luật -> mã 2
            sc = write_json(w.path("sc.json"), {
                "quan": {
                    "stock": {},
                    "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "state": "waiting"}],
                }
            })
            code, _ = run_headless("--mode", "quan", "--seed", "1", "--ticks", "5", "--scenario", sc, "--out", out)
            self.assertEqual(code, 2)
            self.assertFalse(os.path.exists(out))

    def test_khach_waiting_hop_le_khi_mon_da_o_tren_bep_hoac_tay(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            sc = write_json(w.path("sc.json"), {
                "quan": {
                    # PRD-0 mục D: hand là payload món; đơn có món trên tay là "assigned", reserved rỗng
                    "hand": {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60},
                    "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "state": "waiting",
                                   "order_status": "assigned"}],
                }
            })
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "1", "--scenario", sc, "--out", out)
            self.assertEqual(code, 0, err)
            s0 = snapshots(read_jsonl(out))[0]
            self.assertEqual(s0["customers"][0]["reserved"], {})

    def test_headless_tat_dinh_cung_seed(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {
                "quan": {"stock": {"ca_loc": 2, "bong_sung": 4, "ca_linh": 3, "bong_dien_dien": 1}}
            })
            for i in (1, 2):
                code, err = run_headless("--mode", "quan", "--seed", "7", "--ticks", "300",
                                         "--scenario", sc, "--out", w.path(f"q{i}.jsonl"))
                self.assertEqual(code, 0, err)
            with open(w.path("q1.jsonl"), "rb") as a, open(w.path("q2.jsonl"), "rb") as b:
                self.assertEqual(a.read(), b.read())
            arr = events(read_jsonl(w.path("q1.jsonl")), "customer_arrived")
            self.assertEqual(len(arr), 1)
            self.assertEqual(arr[0]["tick"], FIRST_TICK)


if __name__ == "__main__":
    unittest.main()
