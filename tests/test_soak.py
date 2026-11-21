"""Soak (Ticket-04 mục 2) + manifest v1.3: soak_cmd chạy nhiều Ngày, 0 crash, lặp lại giống nhau."""

import json
import shlex
import subprocess
import unittest

from helpers import ROOT, Workdir

with open(f"{ROOT}/game.contract.json", encoding="utf-8") as _f:
    C = json.load(_f)


def soak(*args):
    p = subprocess.run([*shlex.split(C["soak_cmd"]), *args], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stderr


class Manifest(unittest.TestCase):
    def test_v13_khai_bench_va_soak(self):
        self.assertEqual(C["contract_version"], "1.3")
        self.assertTrue(C["bench_cmd"])
        self.assertTrue(C["soak_cmd"])


class Soak(unittest.TestCase):
    def test_soak_6_ngay_lap_d1_d5_va_lap_lai(self):
        outs = []
        with Workdir() as w:
            for i in range(2):
                code, err = soak("--seed", "7", "--days", "6", "--out", w.path(f"s{i}.json"))
                self.assertEqual(code, 0, err)
                with open(w.path(f"s{i}.json"), encoding="utf-8") as f:
                    outs.append(json.load(f))
        r = outs[0]
        self.assertEqual(set(r), {"days", "days_completed", "crashes", "results", "duration_s"})
        self.assertEqual((r["days"], r["days_completed"], r["crashes"]), (6, 6, 0))
        self.assertEqual([x["day"] for x in r["results"]], list(range(1, 7)))
        for x in r["results"]:
            self.assertEqual(set(x), {"day", "earned", "reputation", "score"})
        for o in outs:
            o.pop("duration_s")
        self.assertEqual(outs[0], outs[1])  # so tính lặp ở trường gameplay

    def test_tham_so_sai_ma_2(self):
        with Workdir() as w:
            self.assertEqual(soak("--seed", "7", "--days", "0", "--out", w.path("s.json"))[0], 2)
            self.assertEqual(soak("--seed", "x", "--days", "1", "--out", w.path("s.json"))[0], 2)


if __name__ == "__main__":
    unittest.main()
