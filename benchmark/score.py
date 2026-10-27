"""Score a benchmark run file. Prints counts with sample sizes and
lists every miss / false alarm by id. Never reports a rate without n.
"""

import json
import sys
from pathlib import Path

PROBLEM = {"NOT_FOUND", "INVALID_REPORTER", "MISMATCH"}


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("benchmark/results/latest.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data["entries"]
    bad = [e for e in entries if e["kind"] == "bad" and e["pass"] is not None]
    real = [e for e in entries if e["kind"] == "real" and e["pass"] is not None]
    pending = [e for e in entries if e["pass"] is None]
    caught = [e for e in bad if e["label"] in PROBLEM]
    false_alarms = [e for e in real if e["label"] in PROBLEM]
    uncovered = [e for e in entries
                 if e["label"] in ("NOT_CHECKED", "RATE_LIMITED") and e["pass"] is not None]
    print(f"mode: {data['mode']} | version: {data['version']}")
    print(f"bad: {len(caught)}/{len(bad)} caught as a problem label")
    print(f"real: {len(false_alarms)}/{len(real)} false alarms (problem label on a real case)")
    print(f"coverage gap: {len(uncovered)}/{len(bad) + len(real)} NOT_CHECKED/RATE_LIMITED")
    print(f"pending (excluded from scoring): {len(pending)}")
    misses = [e for e in bad if e["pass"] is False]
    real_misses = [e for e in real if e["pass"] is False]
    if misses:
        print("misses (bad, not caught):")
        for e in misses:
            print(f"  - {e['id']}: got {e['label']}, expected one of {e['expected_labels']}")
    if real_misses:
        print("false alarms / misses (real, not VERIFIED as expected):")
        for e in real_misses:
            print(f"  - {e['id']}: got {e['label']}, expected one of {e['expected_labels']}")
    if not misses and not real_misses:
        print("no misses or false alarms in the scored set")
    print("Note: replay numbers are signals, not rates (small n, mock fixtures).")


if __name__ == "__main__":
    main()
