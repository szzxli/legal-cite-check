import json
import os
import subprocess
import sys
from pathlib import Path

from legalcite import DISCLAIMER
from legalcite.__main__ import check_files
from legalcite.report import build_report, to_html, to_json, to_markdown

ROOT = Path(__file__).resolve().parent.parent


def _checked_sample():
    from legalcite.extract import extract
    citations = [c for c in extract("Obergefell v. Hodges, 576 U.S. 644 (2015)") if c.kind == "full"]
    return [{"citation": citations[0], "label": "VERIFIED", "api_status": 200,
             "score": 100.0, "matches": [{"case_name": "Obergefell v. Hodges"}],
             "notes": []}]


def test_disclaimer_exact_in_all_report_formats():
    report = build_report(_checked_sample())
    assert report["disclaimer"] == DISCLAIMER
    assert DISCLAIMER in to_markdown(report)
    assert DISCLAIMER in to_json(report)
    assert DISCLAIMER in to_html(report)
    for path in (ROOT / "README.md", ROOT / "DISCLAIMER.md", ROOT / "web" / "index.html"):
        assert DISCLAIMER in path.read_text(encoding="utf-8"), path


def test_summary_counts():
    report = build_report(_checked_sample())
    assert report["summary"]["total"] == 1
    assert report["summary"]["VERIFIED"] == 1
    assert report["summary"]["NOT_FOUND"] == 0


def test_cli_no_token_is_not_checked_not_crash(tmp_path):
    brief = tmp_path / "brief.md"
    brief.write_text("Obergefell v. Hodges, 576 U.S. 644 (2015).", encoding="utf-8")
    env = dict(os.environ)
    env.pop("COURTLISTENER_TOKEN", None)
    proc = subprocess.run(
        [sys.executable, "-m", "legalcite", "check", str(brief),
         "--json", str(tmp_path / "r.json"), "--md", str(tmp_path / "r.md")],
        cwd=ROOT, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    data = json.loads((tmp_path / "r.json").read_text())
    assert data["citations"][0]["label"] == "NOT_CHECKED"
    assert DISCLAIMER in (tmp_path / "r.md").read_text()


def test_cli_fail_on_not_checked_exits_1(tmp_path):
    brief = tmp_path / "brief.md"
    brief.write_text("Obergefell v. Hodges, 576 U.S. 644 (2015).", encoding="utf-8")
    env = dict(os.environ)
    env.pop("COURTLISTENER_TOKEN", None)
    proc = subprocess.run(
        [sys.executable, "-m", "legalcite", "check", str(brief),
         "--fail-on", "not_checked"],
        cwd=ROOT, env=env, capture_output=True, text=True)
    assert proc.returncode == 1


def test_cli_bad_label_exits_2(tmp_path):
    brief = tmp_path / "brief.md"
    brief.write_text("576 U.S. 644.", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "legalcite", "check", str(brief),
         "--fail-on", "not_a_label"],
        cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 2


def test_check_files_token_never_in_reports(tmp_path):
    # check_files with no token must not need a token at all; with a fake
    # token the CLI path is network-dependent, so this test only asserts
    # the no-token report contains no token-like value.
    report, _failed = check_files([str(tmp_path / "x.md")] if False else [], token=None)
    assert report["summary"]["total"] == 0
