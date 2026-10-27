from pathlib import Path

from legalcite import DISCLAIMER

ROOT = Path(__file__).resolve().parent.parent


def test_web_makes_no_api_calls():
    for name in ("app.js", "extract.js"):
        src = (ROOT / "web" / name).read_text(encoding="utf-8")
        assert "fetch(" not in src, name
        assert "XMLHttpRequest" not in src, name


def test_web_disclaimer_present_and_no_close_button():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    assert DISCLAIMER in html
    assert "dismiss" not in html.lower()
    assert "goatcounter" in html.lower()


def test_no_forbidden_words_in_labels():
    from legalcite.labels import LABELS
    joined = " ".join(LABELS).lower()
    for word in ("fabricated", "fake", "hallucinated"):
        assert word not in joined
