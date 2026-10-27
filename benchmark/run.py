"""Benchmark runner.

Modes:
  replay: use benchmark/recorded/mock.json (labelled MOCK, no network).
  live:   use CourtListener via legalcite (requires COURTLISTENER_TOKEN;
          sends only citation strings). Never invents a token.
  auto:   live if a token is set, otherwise replay. Output states the mode.

Output JSON: {mode, version, generated_at, entries: [{id, kind, label,
api_status, expected_labels, pass, ...}]}. Pending placeholders are
reported with label PENDING and pass=null (excluded from scoring).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from legalcite.extract import extract  # noqa: E402
from legalcite.labels import label_from_api  # noqa: E402
from legalcite.lookup import CourtListenerClient  # noqa: E402
from legalcite.names import compare_names  # noqa: E402

BENCH = Path(__file__).resolve().parent


def _load_jsonl(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="auto", choices=["auto", "replay", "live"])
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    token = os.environ.get("COURTLISTENER_TOKEN") or None
    mode = args.mode
    if mode == "auto":
        mode = "live" if token else "replay"
    if mode == "live" and not token:
        print("live mode requires COURTLISTENER_TOKEN; refusing to invent one. "
              "Run --mode replay instead.", file=sys.stderr)
        return 2
    mocks = {}
    client = None
    if mode == "replay":
        mocks = json.loads((BENCH / "recorded" / "mock.json").read_text(encoding="utf-8"))
    else:
        client = CourtListenerClient(token)
    entries = []
    for kind, filename in (("bad", "seed/bad.jsonl"), ("real", "seed/real.jsonl")):
        for row in _load_jsonl(BENCH / filename):
            if row.get("expected_labels") == ["PENDING"] or not row.get("citation_as_filed"):
                entries.append({"id": row["id"], "kind": kind, "label": "PENDING",
                                "api_status": None, "expected_labels": ["PENDING"],
                                "pass": None, "note": row.get("note", "")})
                continue
            text = f"{row['case_name_as_filed']}, {row['citation_as_filed']}"
            citations = [c for c in extract(text) if c.kind == "full"]
            if not citations:
                entries.append({"id": row["id"], "kind": kind, "label": "NOT_CHECKED",
                                "api_status": None, "expected_labels": row["expected_labels"],
                                "pass": False, "note": "extraction failed on seed text"})
                continue
            c = citations[0]
            if mode == "replay":
                mock = mocks.get(row["id"])
                if mock is None:
                    entries.append({"id": row["id"], "kind": kind, "label": "PENDING",
                                    "api_status": None, "expected_labels": row["expected_labels"],
                                    "pass": None, "note": "no mock fixture"})
                    continue
                api_status, matches = mock["api_status"], mock["matches"]
            else:
                result = client.lookup([c])
                r = result.get(id(c), {"api_status": None, "matches": []})
                api_status, matches = r["api_status"], r["matches"]
            label, _score, _best, _notes = label_from_api(
                api_status, c.case_name, matches, compare_names)
            entries.append({"id": row["id"], "kind": kind, "label": label,
                            "api_status": api_status,
                            "expected_labels": row["expected_labels"],
                            "pass": label in row["expected_labels"],
                            "citation": row["citation_as_filed"],
                            "case_name": row["case_name_as_filed"]})
    out = {
        "mode": "replay (mock)" if mode == "replay" else "live",
        "version": "v0.1 — 2026-10-26",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }
    text = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
