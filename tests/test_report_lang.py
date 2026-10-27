"""v2: --lang translates report headings only; disclaimer stays English."""
from legalcite import DISCLAIMER
from legalcite.report import to_html, to_markdown


def _report():
    return {"summary": {"total": 1, "VERIFIED": 0, "CITED": 0, "AMBIGUOUS": 0,
                        "MISMATCH": 0, "NOT_FOUND": 0, "INVALID_REPORTER": 0,
                        "RATE_LIMITED": 0, "NOT_CHECKED": 1},
            "citations": [{"index": 1, "label": "NOT_CHECKED", "text": "347 U.S. 483",
                            "case_name_in_text": "Brown v. Board of Education",
                            "manual_check_url": "https://example.invalid/"}]}


def test_markdown_headings_es_zh():
    assert "## Resumen" in to_markdown(_report(), lang="es")
    assert "## \u6458\u8981" in to_markdown(_report(), lang="zh")
    assert "## Summary" in to_markdown(_report(), lang="en")


def test_disclaimer_stays_english_authoritative():
    for lang in ("en", "es", "zh"):
        assert DISCLAIMER in to_markdown(_report(), lang=lang)
        assert DISCLAIMER in to_html(_report(), lang=lang)


def test_html_total_translated():
    assert "Citas totales: 1" in to_html(_report(), lang="es")
