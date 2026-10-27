"""Case-name normalization and comparison.

Normalization (per brief): lowercase, strip punctuation, drop
``et al.``, ``v.``/``vs.``, ``Inc.``, ``LLC``, ``Corp.``, ``Co.``,
``the``; expand common Bluebook abbreviations.
"""

import re
import string

EXPANSIONS = {
    "dep't": "department",
    "dept": "department",
    "ass'n": "association",
    "comm'n": "commission",
    "int'l": "international",
    "nat'l": "national",
    "bros": "brothers",
    "co": "company",
}

DROP_TOKENS = {
    "v", "vs", "versus", "et", "al", "inc", "llc", "corp", "co", "the",
    "and", "of", "a", "an",
}


def normalize_name(name):
    """Return (normalized_string, token_set) for a case name."""
    if not name:
        return "", set()
    text = name.lower()
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    tokens = []
    for raw in re.split(r"\s+", text):
        token = raw.strip(string.punctuation + " ")
        if not token:
            continue
        token = EXPANSIONS.get(token, token)
        if token in DROP_TOKENS:
            continue
        # Strip a trailing possessive / punctuation remnant.
        token = token.strip("'")
        if token:
            tokens.append(token)
    return " ".join(tokens), set(tokens)


def distinctive_overlap(tokens_a, tokens_b):
    """True if any non-stopword token is shared.

    Used only as a guard against MISMATCH (downgrade to CITED), never as
    a standalone reason to VERIFY: a shared surname is not identity.
    """
    return bool(tokens_a & tokens_b)


def _fallback_token_set_ratio(a, b):
    """Pure-Python approximation of rapidfuzz token_set_ratio.

    Sorts unique tokens and compares the resulting strings with
    difflib. Exact matches give 100; disjoint token sets give 0.
    Documented fallback: scores may differ slightly from rapidfuzz.
    """
    import difflib

    if not a and not b:
        return 100.0
    if not a or not b:
        return 0.0
    if a == b:
        return 100.0
    tokens_a = sorted(set(a.split()))
    tokens_b = sorted(set(b.split()))
    common = sorted(set(tokens_a) & set(tokens_b))
    if not common:
        return 0.0
    s_common = " ".join(common)
    s_a = " ".join(tokens_a)
    s_b = " ".join(tokens_b)
    ratios = [
        difflib.SequenceMatcher(None, s_common, s_a).ratio(),
        difflib.SequenceMatcher(None, s_common, s_b).ratio(),
        difflib.SequenceMatcher(None, s_a, s_b).ratio(),
    ]
    return max(ratios) * 100.0


def token_set_ratio(a, b):
    """Best available token-set similarity, 0-100."""
    try:
        from rapidfuzz.fuzz import token_set_ratio as _rapid  # type: ignore

        return float(_rapid(a, b))
    except Exception:
        return _fallback_token_set_ratio(a, b)


def compare_names(name_in_text, cluster_name):
    """Return (score 0-100, has_distinctive_overlap bool)."""
    norm_a, tokens_a = normalize_name(name_in_text)
    norm_b, tokens_b = normalize_name(cluster_name)
    if not norm_a or not norm_b:
        return 0.0, False
    return token_set_ratio(norm_a, norm_b), distinctive_overlap(tokens_a, tokens_b)
