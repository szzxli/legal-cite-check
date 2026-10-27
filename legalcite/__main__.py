"""CLI: python -m legalcite check FILE... [options]

Exit codes: 1 if any citation has a --fail-on label, 0 otherwise,
2 on usage error. A missing CourtListener token is NOT a crash: every
citation becomes NOT_CHECKED with a clear message.
"""

import argparse
import os
import sys

from . import __version__
from .extract import extract
from .io import read_text_file
from .labels import LABELS, label_from_api
from .lookup import AuthError, CourtListenerClient
from .names import compare_names
from .report import build_report, to_html, to_json, to_markdown


def _parse_fail_on(raw):
    labels = []
    for part in raw.split(","):
        part = part.strip().upper()
        if not part:
            continue
        if part not in LABELS:
            raise ValueError(f"unknown label in --fail-on: {part}")
        labels.append(part)
    return labels


def check_files(files, token=None, fail_on=(), send_full_text=False):
    """Run the full pipeline. Returns (report_dict, failed_bool)."""
    checked = []
    for path in files:
        text = read_text_file(path)
        citations = extract(text)
        lookup_results = {}
        client = None
        auth_failed = False
        if token and any(c.kind == "full" for c in citations):
            client = CourtListenerClient(token)
            try:
                lookup_results = client.lookup(
                    citations, send_full_text=send_full_text, full_text=text)
            except AuthError:
                print("CourtListener authentication failed: check COURTLISTENER_TOKEN.",
                      file=sys.stderr)
                lookup_results = {}
                client = None
                auth_failed = True
        for c in citations:
            if c.kind != "full":
                checked.append({"citation": c, "label": "NOT_CHECKED",
                                "api_status": None, "score": None,
                                "matches": [], "notes": c.notes})
                continue
            if client is None:
                checked.append({"citation": c, "label": "NOT_CHECKED",
                                "api_status": None, "score": None,
                                "matches": [],
                                "notes": ["CourtListener authentication failed; not checked"]
                                if auth_failed else
                                ["no CourtListener token; not checked"]})
                continue
            result = lookup_results.get(id(c), {"api_status": None, "matches": [], "notes": []})
            label, score, _best, notes = label_from_api(
                result["api_status"], c.case_name, result["matches"], compare_names)
            checked.append({"citation": c, "label": label,
                            "api_status": result["api_status"], "score": score,
                            "matches": result["matches"],
                            "notes": list(result["notes"]) + notes})
    report = build_report(checked)
    failed = any(row["label"] in fail_on for row in report["citations"])
    return report, failed


def main(argv=None):
    parser = argparse.ArgumentParser(prog="legalcite")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="check citations in files")
    check.add_argument("files", nargs="+")
    check.add_argument("--md", default=None)
    check.add_argument("--json", default=None)
    check.add_argument("--html", default=None)
    check.add_argument("--fail-on", default="not_found,invalid_reporter,mismatch")
    check.add_argument("--send-full-text", action="store_true",
                       help="send full brief text to CourtListener (OFF by default; "
                            "default sends only extracted citation strings)")
    args = parser.parse_args(argv)
    if args.command != "check":
        parser.error("unknown command")
    try:
        fail_on = _parse_fail_on(args.fail_on)
    except ValueError as e:
        parser.error(str(e))
    token = os.environ.get("COURTLISTENER_TOKEN") or None
    if not token:
        print("No COURTLISTENER_TOKEN set: citations will be NOT_CHECKED "
              "(extraction only). Set the variable to run the full lookup.",
              file=sys.stderr)
    try:
        report, failed = check_files(args.files, token=token, fail_on=fail_on,
                                     send_full_text=args.send_full_text)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(to_markdown(report))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(to_json(report))
    if args.html:
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(to_html(report))
    if not (args.md or args.json or args.html):
        print(to_markdown(report))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
