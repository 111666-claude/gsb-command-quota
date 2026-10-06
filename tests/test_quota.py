import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quota import core


def ev(ts, commander="c1", unit="infantry", event_id="e"):
    return {"ts": ts, "commander": commander, "unit": unit, "event_id": event_id}


class QuotaTest(unittest.TestCase):
    def test_first_command_is_kept(self):
        out = core.decide([ev(0)], core.Counter())
        self.assertEqual(out[0]["decision"], "keep")

    def test_under_caps_stays_kept(self):
        events = [ev(i, unit="u%d" % i, event_id="e%d" % i) for i in range(3)]
        out = core.decide(events, core.Counter())
        self.assertTrue(all(row["decision"] == "keep" for row in out))

    def test_over_total_cap_is_dropped(self):
        events = [ev(0, unit="u%d" % i, event_id="e%d" % i) for i in range(11)]
        out = core.decide(events, core.Counter())
        self.assertEqual(out[-1]["decision"], "drop")
        self.assertEqual(out[-1]["reason"], "quota")

    def test_empty_stream(self):
        self.assertEqual(core.decide([], core.Counter()), [])

    def test_scanned_is_reported(self):
        out = core.decide([ev(0), ev(1, event_id="e2")], core.Counter())
        self.assertGreaterEqual(out[-1]["scanned"], 0)


if __name__ == "__main__":
    unittest.main()
