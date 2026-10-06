"""滑动窗口配额判定。"""

from collections import deque

WINDOW_MS = 1000
TOTAL_CAP = 10
UNIT_CAP = 3
CRITICAL = frozenset(["scout"])


class Counter:
    """记录本轮检查过的历史事件条数。"""

    def __init__(self):
        self.scanned = 0


def decide(events, counter):
    seen = set()
    totals = {}
    units = {}
    out = []
    for ev in events:
        event_id = ev["event_id"]
        if event_id in seen:
            out.append({"event_id": ev["event_id"], "decision": "drop",
                        "reason": "duplicate", "scanned": counter.scanned})
            continue
        seen.add(event_id)
        ts = ev["ts"]
        commander = ev["commander"]
        unit = ev["unit"]
        total_q = totals.setdefault(commander, deque())
        while total_q and ts - total_q[0] >= WINDOW_MS:
            total_q.popleft()
        unit_q = units.setdefault((commander, unit), deque())
        while unit_q and ts - unit_q[0] >= WINDOW_MS:
            unit_q.popleft()
        counter.scanned += len(total_q) + len(unit_q)
        if len(total_q) >= TOTAL_CAP:
            out.append({"event_id": ev["event_id"], "decision": "drop",
                        "reason": "quota", "scanned": counter.scanned})
            continue
        if unit not in CRITICAL and len(unit_q) >= UNIT_CAP:
            out.append({"event_id": ev["event_id"], "decision": "drop",
                        "reason": "quota", "scanned": counter.scanned})
            continue
        total_q.append(ts)
        unit_q.append(ts)
        out.append({"event_id": ev["event_id"], "decision": "keep",
                    "reason": None, "scanned": counter.scanned})
    return out
