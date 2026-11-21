"""Độ tươi v1.2 (Ticket-03 mục 1): cá thể {id, kind, fresh}, hao tươi chính xác bằng số nguyên.

Nội bộ lưu `u` = fresh × 240 (240 đơn vị mỗi điểm tươi, như gợi ý của Ticket-03): giỏ trừ 0.5/s = 2 đơn vị/tick,
kho quán 0.25/s = 1 đơn vị/tick; so ngưỡng ươn (fresh < 30 ⇔ u < 7200) và floor giá đều chính xác.
"""

UNITS = 240


def per_tick(decay_per_s, tick_hz=60):
    """Đơn vị hao mỗi tick; báo lỗi nếu manifest cho số không biểu diễn chính xác."""
    v = decay_per_s * UNITS / tick_hz
    if abs(v - round(v)) > 1e-9:
        raise ValueError(f"decay {decay_per_s}/s không chia hết thành đơn vị/tick")
    return int(round(v))


def to_units(fresh):
    return int(round(fresh * UNITS))


def make(iid, kind, fresh_units):
    return {"id": iid, "kind": kind, "u": int(fresh_units)}


def out(item):
    """Dạng JSON {id, kind, fresh} của một cá thể."""
    return {"id": item["id"], "kind": item["kind"], "fresh": item["u"] / UNITS}


def from_json(e):
    return make(e["id"], e["kind"], to_units(e["fresh"]))


class Freshness:
    def __init__(self, tuning):
        f = tuning["freshness"]
        hz = tuning.get("tick_hz", 60)
        self.initial = to_units(f["initial"])
        self.gather_dec = per_tick(f["gather_decay_per_s"], hz)
        self.quan_dec = per_tick(f["quan_decay_per_s"], hz)
        self.threshold = to_units(f["spoiled_below"])

    def spoiled(self, item):
        return item["u"] < self.threshold

    def decay(self, items, per_tick_units, location, events, sort_by_id):
        """Trừ hao cho mọi cá thể; phát spoiled đúng một lần khi đi từ >= ngưỡng xuống < ngưỡng, theo id.
        Trả danh sách id vừa ươn."""
        newly = []
        for it in sort_by_id(items):
            before = it["u"]
            it["u"] = max(0, before - per_tick_units)
            if before >= self.threshold > it["u"]:
                newly.append(it["id"])
                events.append(("spoiled", {"item_id": it["id"], "kind": it["kind"], "location": location}))
        return newly
