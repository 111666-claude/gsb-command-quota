"""命令行入口。"""

import argparse
import json
import sys

from . import core, samples


def main(argv=None):
    ap = argparse.ArgumentParser(prog="quota")
    ap.add_argument("--sample", choices=["window", "overlay", "dup", "work"])
    args = ap.parse_args(argv)

    if args.sample:
        return samples.run(args.sample)

    events = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            events.append(json.loads(line))
    for row in core.decide(events, core.Counter()):
        print(json.dumps(row, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
