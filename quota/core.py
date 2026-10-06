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
    windows = {}
    totals = {}
    unit_counts = {}
    out = []
    for ev in events:
        event_id = ev["event_id"]
        if event_id in seen:
            out.append({"event_id": event_id, "decision": "drop",
                        "reason": "duplicate", "scanned": counter.scanned})
            continue
        seen.add(event_id)

        commander = ev["commander"]
        unit = ev["unit"]
        history = windows.get(commander)
        if history is None:
            history = deque()
            windows[commander] = history

        cutoff = ev["ts"] - WINDOW_MS
        while history and history[0][0] <= cutoff:
            counter.scanned += 1
            _, old_unit = history.popleft()
            totals[commander] -= 1
            if old_unit not in CRITICAL:
                unit_counts[(commander, old_unit)] -= 1

        if totals.get(commander, 0) >= TOTAL_CAP:
            out.append({"event_id": event_id, "decision": "drop",
                        "reason": "quota", "scanned": counter.scanned})
            continue
        if unit not in CRITICAL and unit_counts.get((commander, unit), 0) >= UNIT_CAP:
            out.append({"event_id": event_id, "decision": "drop",
                        "reason": "quota", "scanned": counter.scanned})
            continue

        history.append((ev["ts"], unit))
        totals[commander] = totals.get(commander, 0) + 1
        if unit not in CRITICAL:
            key = (commander, unit)
            unit_counts[key] = unit_counts.get(key, 0) + 1
        out.append({"event_id": event_id, "decision": "keep",
                    "reason": None, "scanned": counter.scanned})
    return out
