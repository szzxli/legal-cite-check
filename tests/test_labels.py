from legalcite.labels import label_from_api, weaker
from legalcite.names import compare_names


def _label(status, name, matches):
    label, score, best, _notes = label_from_api(status, name, matches, compare_names)
    return label, score


def test_status_mapping():
    assert _label(404, "A v. B", [])[0] == "NOT_FOUND"
    assert _label(400, "A v. B", [])[0] == "INVALID_REPORTER"
    assert _label(429, "A v. B", [])[0] == "RATE_LIMITED"
    assert _label(300, "A v. B", [{"case_name": "A v. B"}])[0] == "AMBIGUOUS"
    assert _label(None, "A v. B", [])[0] == "NOT_CHECKED"
    assert _label(500, "A v. B", [])[0] == "NOT_CHECKED"


def test_name_fixtures():
    assert _label(200, "Obergefell v. Hodges",
                  [{"case_name": "Obergefell v. Hodges"}])[0] == "VERIFIED"
    assert _label(200, "Dep't of Education v. Smith",
                  [{"case_name": "Department of Education v. Smith"}])[0] == "VERIFIED"
    assert _label(200, "Taylor v. Reed",
                  [{"case_name": "Taylor v. Reid, Commissioner"}])[0] == "CITED"
    assert _label(200, "Hunt v. Smith",
                  [{"case_name": "Bargo v. Bargo"}])[0] == "MISMATCH"
    # Shared surname alone must not verify, and must not mismatch either.
    assert _label(200, "Smith v. Jones",
                  [{"case_name": "Smith v. Johnson"}])[0] == "CITED"
    # Bare cite: exists, name not compared.
    assert _label(200, None, [{"case_name": "Obergefell v. Hodges"}])[0] == "CITED"


def test_only_downgrade_property():
    # Removing name evidence (exact match -> no name) never upgrades.
    verified, _ = _label(200, "Obergefell v. Hodges", [{"case_name": "Obergefell v. Hodges"}])
    cited, _ = _label(200, None, [{"case_name": "Obergefell v. Hodges"}])
    assert verified == "VERIFIED"
    assert weaker(verified, cited) == "CITED"
    assert weaker("CITED", "VERIFIED") == "CITED"
    assert weaker("VERIFIED", "VERIFIED") == "VERIFIED"
    # Missing evidence never becomes a problem label.
    for status in (None, 500, 429):
        assert _label(status, "A v. B", [])[0] in ("NOT_CHECKED", "RATE_LIMITED")
