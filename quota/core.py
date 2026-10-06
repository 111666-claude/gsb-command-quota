"""滑动窗口配额判定。"""

WINDOW_MS = 1000
TOTAL_CAP = 10
UNIT_CAP = 3
CRITICAL = frozenset(["scout"])


class Counter:
    """记录本轮检查过的历史事件条数。"""

    def __init__(self):
        self.scanned = 0


def decide(events, counter):
    kept = []
    out = []
    for ev in events:
        total = 0
        unit = 0
        for past in kept:
            counter.scanned += 1
            if past["commander"] == ev["commander"]:
                total += 1
                if past["unit"] == ev["unit"]:
                    unit += 1
        if total >= TOTAL_CAP:
            out.append({"event_id": ev["event_id"], "decision": "drop",
                        "reason": "quota", "scanned": counter.scanned})
            continue
        if unit >= UNIT_CAP:
            out.append({"event_id": ev["event_id"], "decision": "drop",
                        "reason": "quota", "scanned": counter.scanned})
            continue
        kept.append(ev)
        out.append({"event_id": ev["event_id"], "decision": "keep",
                    "reason": None, "scanned": counter.scanned})
    return out
