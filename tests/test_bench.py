"""Phase 4 — bench_cmd: `python3 -m chonoi.bench` chạy ngắn (--duration 1) và ghi đúng 5 trường số."""

import json
import math
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = {"frames", "measured_s", "avg_fps", "p1_low_fps", "load_ms"}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


class BenchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        out = os.path.join(cls.tmp.name, "bench.json")
        p = subprocess.run([sys.executable, "-m", "chonoi.bench", "--seed", "42", "--duration", "1", "--out", out],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
        cls.returncode, cls.stderr = p.returncode, p.stderr
        cls.data = None
        if p.returncode == 0:
            with open(out, encoding="utf-8") as f:
                cls.data = json.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exit_zero(self):
        self.assertEqual(self.returncode, 0, self.stderr)

    def test_exactly_five_fields(self):
        self.assertIsNotNone(self.data, self.stderr)
        self.assertEqual(set(self.data), FIELDS)

    def test_numeric_types(self):
        self.assertIsNotNone(self.data, self.stderr)
        self.assertIsInstance(self.data["frames"], int)
        self.assertNotIsInstance(self.data["frames"], bool)
        for k in FIELDS:
            self.assertTrue(_num(self.data[k]), f"{k} = {self.data[k]!r} không phải số hữu hạn")

    def test_frames_positive(self):
        self.assertIsNotNone(self.data, self.stderr)
        self.assertGreater(self.data["frames"], 0)
        self.assertGreater(self.data["measured_s"], 0)

    def test_avg_fps_consistent(self):
        d = self.data
        self.assertIsNotNone(d, self.stderr)
        self.assertAlmostEqual(d["avg_fps"], d["frames"] / d["measured_s"], delta=1e-6 * d["avg_fps"])

    def test_p1_low_not_above_avg(self):
        d = self.data
        self.assertIsNotNone(d, self.stderr)
        self.assertGreater(d["p1_low_fps"], 0)
        self.assertLessEqual(d["p1_low_fps"], d["avg_fps"] * (1 + 1e-9))


if __name__ == "__main__":
    unittest.main()
