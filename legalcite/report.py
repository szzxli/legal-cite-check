"""Report writers: JSON (v0.1), Markdown, standalone HTML.

Every report carries the exact disclaimer first. HTML output is escaped;
no token or brief text beyond the citation strings themselves is ever
added by these writers (the caller controls what goes in).
"""

import html
import json
from datetime import datetime, timezone

from . import DISCLAIMER, __version__
from .labels import LABELS, NEXT_ACTION, meaning


def _slug_for(reporter):
    slugs = {"U.S.": "us", "F. App'x": "f-appx", "S.W.3d": "sw3d"}
    return slugs.get(reporter)


def manual_check_url(citation):
    """Manual-check link only. Never fetched or scraped by this tool."""
    if citation.get("volume") and citation.get("reporter") and citation.get("page"):
        slug = _slug_for(citation["reporter"])
        if slug:
            return (f"https://www.courtlistener.com/c/{slug}/"
                    f"{citation['volume']}/{citation['page']}/")
        from urllib.parse import quote

        return (f"https://www.courtlistener.com/c/"
                f"{quote(citation['reporter'])}/{citation['volume']}/{citation['page']}/")
    return ""


def build_report(checked):
    """checked: list of dicts with citation/label/score/match/notes keys."""
    summary = {label: 0 for label in LABELS}
    rows = []
    for i, item in enumerate(checked, 1):
        label = item["label"]
        summary[label] = summary.get(label, 0) + 1
        cit = item["citation"]
        rows.append({
            "index": i,
            "text": cit.text,
            "volume": cit.volume,
            "reporter": cit.reporter,
            "page": cit.page,
            "case_name_in_text": cit.case_name,
            "year_in_text": cit.year,
            "label": label,
            "api_status": item.get("api_status"),
            "normalized": [f"{cit.volume} {cit.reporter} {cit.page}"]
            if cit.volume else [],
            "matches": item.get("matches") or [],
            "name_similarity": item.get("score"),
            "notes": item.get("notes") or [],
            "manual_check_url": manual_check_url({
                "volume": cit.volume, "reporter": cit.reporter, "page": cit.page}),
        })
    return {
        "tool": "legal-cite-check",
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": DISCLAIMER,
        "summary": {"total": len(rows), **summary},
        "citations": rows,
    }


def to_json(report):
    return json.dumps(report, indent=2, ensure_ascii=False)


def to_markdown(report):
    lines = [f"> **{DISCLAIMER}**", "",
             "## Summary",
             f"Total citations: {report['summary']['total']}"]
    for label in LABELS:
        lines.append(f"- {label}: {report['summary'][label]}")
    lines.append("")
    lines.append("## Citations")
    for row in report["citations"]:
        lines.append(
            f"- [ ] **{row['label']}** — {row['text']}"
            + (f" ({row['case_name_in_text']})" if row["case_name_in_text"] else "")
            + f" — {meaning(row['label'])} {NEXT_ACTION[row['label']]}"
            + (f" [Manual check]({row['manual_check_url']})" if row["manual_check_url"] else "")
        )
    return "\n".join(lines) + "\n"


def to_html(report):
    rows = "".join(
        f"<tr><td>{r['index']}</td><td>{html.escape(r['text'])}</td>"
        f"<td>{html.escape(r['case_name_in_text'] or '')}</td>"
        f"<td>{r['label']}</td>"
        f"<td>{html.escape(meaning(r['label']))} {html.escape(NEXT_ACTION[r['label']])}</td>"
        f"<td>{('<a href=\"' + html.escape(r['manual_check_url']) + '\">Manual check</a>') if r['manual_check_url'] else ''}</td></tr>"
        for r in report["citations"]
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>legal-cite-check report</title></head><body>"
        # DISCLAIMER is our own constant (no user input), so it is inserted
        # verbatim: the exact disclaimer text must appear in every report.
        f"<p><strong>{DISCLAIMER}</strong></p>"
        f"<p>Total citations: {report['summary']['total']}</p>"
        "<table><tr><th>#</th><th>Citation</th><th>Case name in text</th>"
        "<th>Label</th><th>What to do next</th><th>Link</th></tr>"
        f"{rows}</table></body></html>"
    )
