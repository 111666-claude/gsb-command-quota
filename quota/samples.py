"""固定场景，用来复现题面里的锚点。"""

import json

from . import core


def _line(obj):
    print(json.dumps(obj, ensure_ascii=False))


def _ev(ts, commander="c1", unit="infantry", event_id="e"):
    return {"ts": ts, "commander": commander, "unit": unit, "event_id": event_id}


def _last(out):
    return {"decision": out[-1]["decision"], "reason": out[-1]["reason"]}


def run(name):
    if name == "window":
        events = [_ev(i, event_id="e%d" % i) for i in range(12)]
        events.append(_ev(5000, event_id="late"))
        _line(_last(core.decide(events, core.Counter())))
        return 0
    if name == "overlay":
        events = [_ev(i, unit="scout", event_id="s%d" % i) for i in range(4)]
        _line(_last(core.decide(events, core.Counter())))
        return 0
    if name == "dup":
        events = [_ev(0, event_id="same"), _ev(1, event_id="same")]
        out = core.decide(events, core.Counter())
        _line({"decisions": [row["decision"] for row in out]})
        return 0
    if name == "work":
        events = [_ev(i, commander="c%d" % (i % 400), event_id="e%d" % i) for i in range(2000)]
        out = core.decide(events, core.Counter())
        _line({"events": 2000, "scanned": out[-1]["scanned"]})
        return 0
    raise SystemExit("未知场景：" + name)
