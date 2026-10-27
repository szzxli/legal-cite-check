"""Label set and the only-downgrade rule.

Strength order (strongest first): VERIFIED > CITED > AMBIGUOUS.
Problem labels (MISMATCH, NOT_FOUND, INVALID_REPORTER) require positive
evidence from the CourtListener API. Missing evidence (rate limit, network
error, parse doubt) yields RATE_LIMITED / NOT_CHECKED, never a problem
label. Uncertainty therefore only ever moves a label toward a weaker claim.

Safety note (deliberate deviation from a literal reading of the brief):
a shared distinctive token (e.g. a common surname) does NOT upgrade a
citation to VERIFIED. It only blocks MISMATCH, downgrading it to CITED.
A shared surname alone cannot verify identity.
"""

LABELS = (
    "VERIFIED",
    "CITED",
    "AMBIGUOUS",
    "MISMATCH",
    "NOT_FOUND",
    "INVALID_REPORTER",
    "RATE_LIMITED",
    "NOT_CHECKED",
)

NEXT_ACTION = {
    "VERIFIED": "Still read it: this does not mean it supports your point or is good law.",
    "CITED": "Open the link and confirm the case name and holding.",
    "AMBIGUOUS": "Open the candidates and pick the one you meant; add the case name.",
    "MISMATCH": "Likely a wrong volume/page or wrong case; find the correct cite.",
    "NOT_FOUND": "Find the case in an official reporter or another database before relying on it; if you can't find it anywhere, remove it.",
    "INVALID_REPORTER": "Check the abbreviation; the cite may be mistyped or invalid.",
    "RATE_LIMITED": "Re-run later.",
    "NOT_CHECKED": "Check by hand using the links.",
}

_MEANING = {
    "VERIFIED": "Found in CourtListener and the case name matches.",
    "CITED": "Found in CourtListener; name not compared or only partly matches.",
    "AMBIGUOUS": "This cite matches more than one case.",
    "MISMATCH": "A case exists at this cite, but it is a different case from the one named.",
    "NOT_FOUND": "Valid citation format, but CourtListener has no case at this cite.",
    "INVALID_REPORTER": "The reporter abbreviation is not a recognized reporter.",
    "RATE_LIMITED": "Not checked: the lookup service asked us to slow down.",
    "NOT_CHECKED": "Not checked (statute, id./supra, short cite, network error, browser mode).",
}

# Weaker = larger number. Problem labels are not on this scale: they are
# only assigned on positive API evidence, never by downgrading.
_STRENGTH = {"VERIFIED": 0, "CITED": 1, "AMBIGUOUS": 2}


def meaning(label):
    return _MEANING[label]


def weaker(a, b):
    """Return the weaker of two existence labels (never stronger)."""
    if a not in _STRENGTH:
        return a
    if b not in _STRENGTH:
        return b
    return a if _STRENGTH[a] >= _STRENGTH[b] else b


def label_from_api(api_status, case_name_in_text, matches, similarity_fn):
    """Map a CourtListener per-citation status + name comparison to a label.

    api_status: 200 / 300 / 404 / 400 / 429 / None (network/other).
    matches: list of dicts with at least "case_name".
    similarity_fn: (a, b) -> (score 0-100, has_distinctive_overlap bool).
    Returns (label, score_or_None, best_match_or_None, notes list).
    """
    notes = []
    if api_status == 429:
        return "RATE_LIMITED", None, None, notes
    if api_status == 404:
        return "NOT_FOUND", None, None, notes
    if api_status == 400:
        return "INVALID_REPORTER", None, None, notes
    if api_status == 300:
        best = matches[0] if matches else None
        return "AMBIGUOUS", None, best, notes
    if api_status == 200:
        if not matches:
            return "CITED", None, None, ["exists; no cluster returned to compare"]
        if not case_name_in_text:
            return "CITED", None, matches[0], ["exists; name not compared (bare cite)"]
        best_score, best_match, best_overlap = -1, None, False
        for m in matches:
            score, overlap = similarity_fn(case_name_in_text, m.get("case_name") or "")
            if score > best_score:
                best_score, best_match, best_overlap = score, m, overlap
        if best_score >= 85:
            return "VERIFIED", best_score, best_match, notes
        if best_score <= 40 and not best_overlap:
            return "MISMATCH", best_score, best_match, notes
        return "CITED", best_score, best_match, ["name only partly matches; check by hand"]
    # Any other status, including None (network / 5xx / parse failure):
    # missing evidence must never become a problem label.
    return "NOT_CHECKED", None, None, ["lookup did not return a usable status"]
