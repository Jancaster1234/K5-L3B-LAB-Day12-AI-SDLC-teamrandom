"""Tiện ích test: chạy headless, đọc JSONL, dựng fixture, so sánh có dung sai."""

import json
import math
import os
import shlex
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return path


def frames(*fr):
    return {"frames": list(fr)}


def headless_cmd():
    """Lệnh headless khai trong game.contract.json — test chạy qua đây nên dùng được với MỌI ngôn ngữ."""
    with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
        cmd = shlex.split(json.load(f)["headless_cmd"])
    if os.name == "nt" and cmd and cmd[0] == "python3":
        import sys
        cmd[0] = sys.executable
    return cmd


def run_headless(*args, cwd=ROOT):
    """Chạy `<headless_cmd> <args>`; trả (mã thoát, stderr)."""
    p = subprocess.run([*headless_cmd(), *args], cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stderr


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def snapshots(rows):
    return [r for r in rows if r["type"] == "snapshot"]


def events(rows, name=None):
    return [r for r in rows if r["type"] == "event" and (name is None or r["name"] == name)]


def close(a, b, tol=0.1):
    return abs(a - b) <= tol


def dist(p, q):
    return math.dist(p, q)


class Workdir:
    """Thư mục tạm tự dọn: with Workdir() as w: w.path('x.json')."""

    def __enter__(self):
        self._d = tempfile.TemporaryDirectory()
        return self

    def __exit__(self, *a):
        self._d.cleanup()

    def path(self, name):
        return os.path.join(self._d.name, name)


# --- v1.2: kho/giỏ là mảng cá thể {id, kind, fresh} --------------------------------
def items(*kinds, fresh=100, start=1):
    """Dựng mảng cá thể I<start>, I<start+1>, … theo thứ tự (thứ tự vào giỏ)."""
    return [{"id": f"I{start + i}", "kind": k, "fresh": fresh} for i, k in enumerate(kinds)]


def kinds(lst):
    """Mảng cá thể -> danh sách kind theo thứ tự (để so thứ tự giỏ / LIFO)."""
    return [e["kind"] for e in lst]


def count(lst):
    """Mảng cá thể -> {kind: số} sắp theo kind (để so tổng hàng)."""
    out = {}
    for e in lst:
        out[e["kind"]] = out.get(e["kind"], 0) + 1
    return {k: out[k] for k in sorted(out)}


def stock_items(counts, fresh=100, start=1):
    """{kind: số} -> mảng cá thể (kind theo thứ tự khai báo, id I<start>…), cho scenario quan.stock v1.2."""
    return items(*[k for k, n in counts.items() for _ in range(n)], fresh=fresh, start=start)


def fresh_price(price, units_list):
    """Giá chốt v1.2: floor(giá niêm yết × trung bình fresh / 100), fresh lưu theo đơn vị 1/240."""
    return (price * sum(units_list)) // (len(units_list) * 100 * 240)
