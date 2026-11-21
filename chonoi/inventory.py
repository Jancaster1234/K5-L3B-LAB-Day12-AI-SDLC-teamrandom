"""File kho v1.2 (Ticket-03 mục 1): {"items": [{"id", "kind", "fresh"}, ...]}.

Đọc: từ chối kho đếm (v1.0/1.1) hoặc sai schema, kind lạ, id trùng, fresh ngoài [0, 100] (BadInput -> mã 2).
Ghi: sắp theo id, đủ chính xác khi đọc lại, qua file tạm cùng thư mục rồi thay thế nguyên tử, byte-ổn-định.
"""

import json
import math
import os
import tempfile

from .errors import BadInput
from .ids import sort_by_id

KINDS_P1 = ("ca_loc", "ca_linh", "ca_keo", "bong_dien_dien", "bong_sung", "keo_neo")  # v1.1: 6 nguyên liệu


def validate_item_list(items, where="items", kinds=KINDS_P1):
    """Mảng cá thể {id, kind, fresh}; trả về chính mảng đó (đã kiểm)."""
    if not isinstance(items, list):
        raise BadInput(f"{where} phải là mảng cá thể {{id, kind, fresh}} (v1.2)")
    seen = set()
    for e in items:
        if not isinstance(e, dict) or set(e) != {"id", "kind", "fresh"}:
            raise BadInput(f"{where}: mỗi cá thể có đúng id, kind, fresh")
        if not isinstance(e["id"], str) or not e["id"] or e["id"] in seen:
            raise BadInput(f"{where}: id rỗng hoặc trùng ({e.get('id')!r})")
        seen.add(e["id"])
        if e["kind"] not in kinds:
            raise BadInput(f"{where}: nguyên liệu lạ {e['kind']!r}")
        f = e["fresh"]
        if isinstance(f, bool) or not isinstance(f, (int, float)) or not math.isfinite(f) or not 0 <= f <= 100:
            raise BadInput(f"{where}: fresh của {e['id']} phải trong [0, 100]")
    return items


def read_inventory(path: str, kinds=KINDS_P1) -> list:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được file kho {path}: {e}")
    if not isinstance(data, dict) or set(data.keys()) != {"items"}:
        raise BadInput("file kho chỉ được có khóa gốc 'items'")
    return validate_item_list(data["items"], "file kho", kinds)


def write_inventory(path: str, items: list):
    items = sort_by_id(items)
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".inv-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"items": items}, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
