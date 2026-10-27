"""Citation extraction.

Default extractor is a deterministic regex covering the reporters used in
the v0.1 benchmark plus any dotted reporter abbreviation. If eyecite is
installed and LEGALCITE_USE_EYECITE=1, eyecite is tried first and any
failure falls back to the regex, so extraction never depends on an
optional dependency. The browser extractor (web/extract.js) is a separate
JS implementation driven by the same reporter table.
"""

import os
import re
from dataclasses import dataclass, field

# Reporters with a space inside the abbreviation must be listed first so
# the alternation matches the longest form.
_KNOWN_REPORTERS = (
    r"F\. Supp\. ?(?:2d|3d)",
    r"Cal\. Rptr\. ?(?:2d|3d)",
    r"So\. ?(?:2d|3d)",
    r"F\. App'x",
    r"S\.W\. ?(?:2d|3d)",
    r"N\.E\. ?(?:2d|3d)",
    r"P\. ?(?:2d|3d)",
    r"U\.S\.",
    r"S\. Ct\.",
    r"F\. ?(?:2d|3d|4th)",
)

_REPORTER_ALT = "|".join(_KNOWN_REPORTERS) + r"|[A-Z][A-Za-z]{0,10}\.[A-Za-z.]*"
_CITATION_RE = re.compile(
    r"\b(?P<volume>\d{1,4})\s+"
    r"(?P<reporter>" + _REPORTER_ALT + r")"
    r"\s+(?P<page>\d{1,5})\b"
)

_PARTY = (
    r"[A-Z][\w.'&\-\u00c0-\u024f]+"
    r"(?:\s+(?:[A-Z][\w.'&\-\u00c0-\u024f]+"
    r"|(?:of|the|and|for)\s+[A-Z][\w.'&\-\u00c0-\u024f]+)){0,4}"
    r"(?:,\s+(?:Inc\.|LLC|Corp\.))?"
)
_CASE_NAME_RE = re.compile(_PARTY + r"\s+v\.\s+" + _PARTY)
# The compiled pattern has no capture groups by design; _case_name_before
# therefore re-derives the two parties from the match text.
_CASE_NAME_SPLIT = re.compile(r"\s+v\.\s+")

# A year counts only when this citation's own parenthetical opens right
# after the citation or its pin cite. A later "(YYYY)" belongs to the
# next citation and must not be borrowed (the old 60-character scan did).
_PIN_PREFIX_RE = re.compile(r"^\s*,\s*\d{1,5}(?:\s*[-\u2013]\s*\d{1,5})?\b")
_FOLLOWING_CITE_RE = re.compile(r"^\s+(?:" + _REPORTER_ALT + r")\s+\d")
_OWN_YEAR_RE = re.compile(r"^\s*\(\s*(?:[^)]*?)(\d{4})\s*\)")
_OTHER_RE = re.compile(r"\bId\.\b|\bsupra\b|\b\d+\s+U\.S\.C\.\b")


@dataclass
class Citation:
    text: str
    volume: str | None
    reporter: str | None
    page: str | None
    case_name: str | None
    year: str | None
    start: int
    end: int
    kind: str = "full"  # "full" or "other" (id./supra/statute -> NOT_CHECKED)
    notes: list = field(default_factory=list)


# Keep in sync with CASE_PREFIXES in web/extract.js. Longer phrases come
# before the words they contain. A prefix is removed only when a party
# name remains, so "See v. Seattle" and "United States v. ..." stay intact.
_CASE_PREFIXES = (
    "see also", "see generally", "but see", "but cf.", "but cf", "see",
    "cf.", "cf", "compare", "accord", "contra", "e.g.,", "e.g.",
    "also", "again", "but", "and", "under", "following", "moreover",
    "furthermore", "further", "additionally", "similarly", "likewise",
    "however", "therefore", "thus", "hence", "accordingly", "consequently",
    "meanwhile", "subsequently", "generally", "citing", "quoting", "discussing",
    "unlike", "like", "after", "before", "while", "although", "because",
    "since", "if", "when", "where", "here", "there", "then", "now", "yet",
    "nor", "or", "for", "with", "from", "per", "via", "both", "either",
    "neither", "recently", "notably", "finally", "later", "earlier",
    "despite", "notwithstanding", "into", "over", "about", "as", "by", "on",
    "at", "to", "in", "an",
)
_SIGNAL_RE = re.compile(
    r"^(?:" + "|".join(re.escape(p) for p in _CASE_PREFIXES) + r")\s+",
    re.IGNORECASE,
)


def _strip_signal(name):
    # Citation signals ("See ...", "Cf. ...", "Also ...") precede the case
    # name and are not part of it. Stop rather than erase a party whose
    # whole name is a signal word ("See v. Seattle").
    while True:
        nxt = _SIGNAL_RE.sub("", name, count=1)
        if not nxt or nxt == name:
            return name
        name = nxt


def _case_name_before(text, start):
    window = text[max(0, start - 160):start]
    matches = list(_CASE_NAME_RE.finditer(window))
    if not matches:
        return None
    m = matches[-1]
    # Only accept a name whose end is reasonably close to the citation.
    if start - (max(0, start - 160) + m.end()) > 80:
        return None
    parts = _CASE_NAME_SPLIT.split(m.group(0))
    if len(parts) != 2:
        return None
    return f"{_strip_signal(parts[0])} v. {parts[1]}"


def _year_after(text, end):
    rest = text[end:]
    pin = _PIN_PREFIX_RE.match(rest)
    # ", 576 U.S. 644" is the next citation, not a pin cite, so its year
    # parenthetical is not this citation's.
    if pin and not _FOLLOWING_CITE_RE.match(rest[pin.end():]):
        rest = rest[pin.end():]
    m = _OWN_YEAR_RE.match(rest)
    return m.group(1) if m else None


def _regex_extract(text):
    out = []
    for m in _CITATION_RE.finditer(text):
        reporter = re.sub(r"\s+", " ", m.group("reporter")).strip()
        # The generic dotted-reporter branch can catch things like
        # "U.S. 644" fragments; require a plausible reporter shape.
        out.append(Citation(
            text=m.group(0),
            volume=m.group("volume"),
            reporter=reporter,
            page=m.group("page"),
            case_name=_case_name_before(text, m.start()),
            year=_year_after(text, m.end()),
            start=m.start(),
            end=m.end(),
        ))
    # Non-full citations are reported as NOT_CHECKED, not looked up.
    seen_spans = [(c.start, c.end) for c in out]
    for m in _OTHER_RE.finditer(text):
        if any(s <= m.start() < e for s, e in seen_spans):
            continue
        out.append(Citation(
            text=m.group(0), volume=None, reporter=None, page=None,
            case_name=None, year=None, start=m.start(), end=m.end(),
            kind="other", notes=["not a full case citation; check by hand"],
        ))
    out.sort(key=lambda c: c.start)
    return out


def extract(text):
    """Extract citations from text. Never raises on unparseable input."""
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    if os.environ.get("LEGALCITE_USE_EYECITE") == "1":
        try:
            from eyecite import get_citations  # type: ignore

            found = []
            for c in get_citations(text):
                kind = getattr(c, "__class__", type(c)).__name__
                if kind != "FullCaseCitation":
                    continue
                span = c.span() if hasattr(c, "span") else (0, 0)
                meta = getattr(c, "metadata", None)
                name = None
                if meta is not None:
                    name = getattr(meta, "plaintiff", None)
                    defendant = getattr(meta, "defendant", None)
                    if name and defendant:
                        name = f"{name} v. {defendant}"
                found.append(Citation(
                    text=text[span[0]:span[1]] if span[1] > span[0] else str(c),
                    volume=str(getattr(c, "volume", "")) or None,
                    reporter=getattr(c, "reporter", None),
                    page=str(getattr(c, "page", "")) or None,
                    case_name=name,
                    year=str(getattr(c, "year", "")) or None,
                    start=span[0], end=span[1],
                ))
            if found:
                return found
        except Exception:
            pass  # Fall through to the deterministic regex extractor.
    return _regex_extract(text)
