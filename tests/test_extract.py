from legalcite.extract import extract


SAMPLES = [
    ("Obergefell v. Hodges, 576 U.S. 644 (2015)", "576 U.S. 644", "Obergefell v. Hodges"),
    ("Brown v. Board of Education, 347 U.S. 483 (1954)", "347 U.S. 483", "Brown v. Board of Education"),
    ("Marbury v. Madison, 5 U.S. 137 (1803)", "5 U.S. 137", "Marbury v. Madison"),
    ("Miranda v. Arizona, 384 U.S. 436 (1966)", "384 U.S. 436", "Miranda v. Arizona"),
    ("Citizens United v. FEC, 558 U.S. 310 (2010)", "558 U.S. 310", "Citizens United v. FEC"),
    ("Roe v. Wade, 410 U.S. 113 (1973)", "410 U.S. 113", "Roe v. Wade"),
    ("Obergefell v. Hodges, 135 S. Ct. 2584 (2015)", "135 S. Ct. 2584", "Obergefell v. Hodges"),
    ("Hunt v. Smith, 670 S.W.2d 248 (Ky. App. 1984)", "670 S.W.2d 248", "Hunt v. Smith"),
    ("Bargo v. Bargo, 616 S.W.3d 389 (Ky. App. 2020)", "616 S.W.3d 389", "Bargo v. Bargo"),
    ("Roberts v. Hensley, 422 S.W.3d 727 (Ky. App. 2013)", "422 S.W.3d 727", "Roberts v. Hensley"),
    ("Mpala v. Segarra, 715 F. App'x 84", "715 F. App'x 84", "Mpala v. Segarra"),
    ("LinkCo, Inc. v. Naoyuki Akikusa, 357 F. App'x 180", "357 F. App'x 180", "LinkCo, Inc. v. Naoyuki Akikusa"),
    ("Smith v. Jones, 123 F.3d 456 (2020)", "123 F.3d 456", "Smith v. Jones"),
    ("Smith v. Jones, 123 F.2d 456 (1990)", "123 F.2d 456", "Smith v. Jones"),
    ("Smith v. Jones, 123 F. Supp. 3d 456 (2020)", "123 F. Supp. 3d 456", "Smith v. Jones"),
    ("Smith v. Jones, 123 F. Supp. 2d 456 (2005)", "123 F. Supp. 2d 456", "Smith v. Jones"),
    ("Smith v. Jones, 123 N.E.3d 456 (2020)", "123 N.E.3d 456", "Smith v. Jones"),
    ("Smith v. Jones, 123 N.E.2d 456 (1995)", "123 N.E.2d 456", "Smith v. Jones"),
    ("Smith v. Jones, 123 P.3d 456 (2020)", "123 P.3d 456", "Smith v. Jones"),
    ("Smith v. Jones, 123 So. 3d 456 (2020)", "123 So. 3d 456", "Smith v. Jones"),
    ("Smith v. Jones, 123 Cal. Rptr. 3d 456 (2020)", "123 Cal. Rptr. 3d 456", "Smith v. Jones"),
]


def test_extraction_fixtures():
    for text, cite, name in SAMPLES:
        found = [c for c in extract(text) if c.kind == "full"]
        assert len(found) == 1, (text, found)
        assert found[0].text == cite, (text, found[0])
        if name is not None:
            assert found[0].case_name == name, (text, found[0].case_name)


def test_citation_signal_not_part_of_case_name():
    found = [c for c in extract("See Brown v. Board of Education, 347 U.S. 483 (1954).") if c.kind == "full"]
    assert found[0].case_name == "Brown v. Board of Education"
    found = [c for c in extract("Cf. Obergefell v. Hodges, 576 U.S. 644 (2015).") if c.kind == "full"]
    assert found[0].case_name == "Obergefell v. Hodges"


def test_year_extracted():
    found = [c for c in extract("Obergefell v. Hodges, 576 U.S. 644 (2015)") if c.kind == "full"]
    assert found[0].year == "2015"


def test_bare_cite_has_no_name():
    found = [c for c in extract("See 576 U.S. 644 for the rule.") if c.kind == "full"]
    assert found[0].case_name is None


def test_id_and_supra_are_not_checked():
    found = extract("See id. at 5; supra note 3; and 576 U.S. 644.")
    kinds = [c.kind for c in found]
    assert "other" in kinds
    assert [c for c in found if c.kind == "full"][0].text == "576 U.S. 644"


def test_empty_text():
    assert extract("") == []
    assert extract("No citations here at all.") == []
