"""Đo hiệu năng (Phase 4, `bench_cmd`): buổi sáng lõi + render phần mềm vào framebuffer.

Chạy: python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json

Cảnh đo: `runner.Session("gather", tuning, {}, seed)`, mỗi khung gọi `step()` với input rỗng (Út Sen đứng
yên ở bến), rồi "render" phần mềm vào `bytearray(1280 * 720 * 3)` (RGB): tô nền, vẽ hình chữ nhật cho nút
hái, đàn cá, Cá Sấu (`monsters`, nếu snapshot có) và người chơi — tất cả đọc từ `session.snapshot()`.
Buổi sáng hết giờ trước khi đo xong thì dựng lại Session cùng seed (việc dựng lại tính vào khung đó).

Làm nóng 3 s rồi đo `--duration` giây. Đồng hồ `time.perf_counter` CHỈ dùng trong bench, không đi vào sim.
Ghi JSON đúng 5 trường: frames, measured_s, avg_fps, p1_low_fps, load_ms.
Chỉ dùng thư viện chuẩn Python.
"""

import time

_T_LAUNCH = time.perf_counter()  # mốc "khởi chạy": càng sớm càng tốt, trước các import nặng

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402

from .contract import load_contract  # noqa: E402
from .inputs import InputState  # noqa: E402
from .runner import Session  # noqa: E402

WIDTH, HEIGHT, BPP = 1280, 720, 3
WARMUP_S = 3.0

# Màu RGB (chỉ để vẽ, không phải số liệu luật)
C_SKY = (150, 200, 235)
C_WATER = (30, 90, 140)
C_NODE_READY = (90, 200, 90)
C_NODE_WAIT = (60, 110, 60)
C_FISH = (240, 190, 60)
C_MONSTER = (120, 140, 60)
C_PLAYER = (230, 70, 70)
C_DOCK = (140, 100, 60)


def empty_input():
    return InputState((0.0, 0.0), set(), set())


class Renderer:
    """Render phần mềm tối giản: tô nền + hình chữ nhật đặc, ghi thẳng vào bytearray RGB."""

    def __init__(self, bounds, surface_depth):
        self.fb = bytearray(WIDTH * HEIGHT * BPP)
        self.x0, self.x1 = bounds["x"]
        self.d0, self.d1 = bounds["d"]
        self.sx = WIDTH / (self.x1 - self.x0)
        self.sy = HEIGHT / (self.d1 - self.d0)
        row_sky, row_water = bytes(C_SKY) * WIDTH, bytes(C_WATER) * WIDTH
        surf = max(0, min(HEIGHT, int(round((surface_depth - self.d0) * self.sy))))
        self._bg = row_sky * surf + row_water * (HEIGHT - surf)
        self._row_cache = {}

    def _to_px(self, pos):
        return (int((pos[0] - self.x0) * self.sx), int((pos[1] - self.d0) * self.sy))

    def rect(self, cx, cy, w, h, color):
        x0, y0 = max(0, cx - w // 2), max(0, cy - h // 2)
        x1, y1 = min(WIDTH, cx - w // 2 + w), min(HEIGHT, cy - h // 2 + h)
        if x1 <= x0 or y1 <= y0:
            return
        n = x1 - x0
        key = (color, n)
        row = self._row_cache.get(key)
        if row is None:
            row = self._row_cache[key] = bytes(color) * n
        fb, stride = self.fb, WIDTH * BPP
        for y in range(y0, y1):
            off = y * stride + x0 * BPP
            fb[off:off + n * BPP] = row

    def draw(self, snap, dock_pos):
        self.fb[:] = self._bg
        self.rect(*self._to_px(dock_pos), 48, 12, C_DOCK)
        for n in snap.get("nodes", []):
            self.rect(*self._to_px(n["pos"]), 20, 20, C_NODE_READY if n.get("ready") else C_NODE_WAIT)
        for f in snap.get("fish", []):
            self.rect(*self._to_px(f["pos"]), 32, 16, C_FISH)
        for m in snap.get("monsters", []):
            self.rect(*self._to_px(m["pos"]), 64, 24, C_MONSTER)
        self.rect(*self._to_px(snap["player"]["pos"]), 24, 36, C_PLAYER)


class Scene:
    """Buổi sáng lõi: Session gather, scenario rỗng, input rỗng; hết buổi thì dựng lại cùng seed."""

    def __init__(self, tuning, seed):
        self.tuning, self.seed = tuning, seed
        g = tuning["gather"]
        self.dock_pos = g["dock_pos"]
        self.renderer = Renderer(g["bounds"], g["surface_depth"])
        self.inp = empty_input()
        self.session = self._new_session()

    def _new_session(self):
        return Session("gather", self.tuning, {}, self.seed)

    def frame(self):
        if self.session.done:
            self.session = self._new_session()
        self.session.step(self.inp)
        self.renderer.draw(self.session.snapshot(), self.dock_pos)


def p1_low(frame_times):
    """1% low: trung bình max(1, ceil(0.01 * N)) khung chậm nhất, rồi nghịch đảo."""
    k = max(1, math.ceil(0.01 * len(frame_times)))
    slowest = sorted(frame_times, reverse=True)[:k]
    return 1.0 / (sum(slowest) / k)


def run_bench(seed, duration, t_launch=_T_LAUNCH):
    clock = time.perf_counter
    tuning = load_contract()["tuning"]
    scene = Scene(tuning, seed)
    scene.frame()  # khung đầu tiên của cảnh đo
    load_ms = (clock() - t_launch) * 1000.0

    warm_end = clock() + WARMUP_S
    while clock() < warm_end:
        scene.frame()

    times = []
    start = clock()
    end_at = start + duration
    prev = start
    while prev < end_at:
        scene.frame()
        now = clock()
        times.append(now - prev)
        prev = now
    measured_s = prev - start
    frames = len(times)
    return {
        "frames": frames,
        "measured_s": measured_s,
        "avg_fps": frames / measured_s,
        "p1_low_fps": p1_low(times),
        "load_ms": load_ms,
    }


def main(argv=None):
    p = argparse.ArgumentParser(prog="python3 -m chonoi.bench", description="Đo FPS buổi sáng lõi (Phase 4)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--duration", type=float, default=30.0, help="số giây đo (sau 3 s làm nóng)")
    p.add_argument("--out", default="bench.json")
    a = p.parse_args(argv)
    if not (a.duration > 0 and math.isfinite(a.duration)):
        p.error("--duration phải là số dương")
    result = run_bench(a.seed, a.duration)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
