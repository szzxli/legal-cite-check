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


def test_year_not_borrowed_from_next_citation():
    # The second citation's "(1954)" sits well inside the old 60-character
    # lookahead. It belongs to Brown, not to Smith, which has no year.
    text = "Smith v. Jones, 123 F.3d 456. Also Brown v. Board of Education, 347 U.S. 483 (1954)."
    found = [c for c in extract(text) if c.kind == "full"]
    assert len(found) == 2
    assert found[0].text == "123 F.3d 456"
    assert found[0].case_name == "Smith v. Jones"
    assert found[0].year is None
    assert found[1].case_name == "Brown v. Board of Education"
    assert found[1].year == "1954"
    followed = [c for c in extract("See 347 U.S. 483, 576 U.S. 644 (2015).") if c.kind == "full"]
    assert followed[0].year is None
    assert followed[1].year == "2015"


def test_signal_and_transition_prefixes():
    samples = [
        ("Also Brown v. Board of Education, 347 U.S. 483 (1954).", "Brown v. Board of Education"),
        ("Again Roe v. Wade, 410 U.S. 113 (1973).", "Roe v. Wade"),
        ("But Smith v. Jones, 123 F.3d 456 (2020).", "Smith v. Jones"),
        ("Accord Miranda v. Arizona, 384 U.S. 436 (1966).", "Miranda v. Arizona"),
        ("See also Brown v. Board of Education, 347 U.S. 483 (1954).", "Brown v. Board of Education"),
        ("Cf. Roe v. Wade, 410 U.S. 113 (1973).", "Roe v. Wade"),
        ("Under Brown v. Board of Education, 347 U.S. 483 (1954).", "Brown v. Board of Education"),
        ("And United States v. Nixon, 418 U.S. 683 (1974).", "United States v. Nixon"),
    ]
    for text, name in samples:
        found = [c for c in extract(text) if c.kind == "full"]
        assert found[0].case_name == name, (text, found[0].case_name)


def test_case_name_and_year_guards():
    normal = [c for c in extract("Obergefell v. Hodges, 576 U.S. 644 (2015).") if c.kind == "full"]
    assert normal[0].case_name == "Obergefell v. Hodges"
    assert normal[0].year == "2015"
    pin = [c for c in extract("Obergefell v. Hodges, 576 U.S. 644, 650 (2015).") if c.kind == "full"]
    assert pin[0].year == "2015"
    court = [c for c in extract("Smith v. Jones, 123 F.3d 456 (9th Cir. 2020).") if c.kind == "full"]
    assert court[0].case_name == "Smith v. Jones"
    assert court[0].year == "2020"
    court_pin = [c for c in extract("Hunt v. Smith, 670 S.W.2d 248, 250 (Ky. App. 1984).") if c.kind == "full"]
    assert court_pin[0].year == "1984"
    united = [c for c in extract("United States v. Nixon, 418 U.S. 683 (1974).") if c.kind == "full"]
    assert united[0].case_name == "United States v. Nixon"
    assert united[0].year == "1974"
    board = [c for c in extract("Board of Regents v. Roth, 408 U.S. 564 (1972).") if c.kind == "full"]
    assert board[0].case_name == "Board of Regents v. Roth"
    assert board[0].year == "1972"
    # Prefix words that are only a prefix of a real party name must stay.
    indiana = [c for c in extract("Indiana v. Edwards, 554 U.S. 164 (2008).") if c.kind == "full"]
    assert indiana[0].case_name == "Indiana v. Edwards"
    butz = [c for c in extract("Butz v. Economou, 438 U.S. 478 (1978).") if c.kind == "full"]
    assert butz[0].case_name == "Butz v. Economou"
    see_party = [c for c in extract("See v. City of Seattle, 100 P.2d 200 (1940).") if c.kind == "full"]
    assert see_party[0].case_name == "See v. City of Seattle"
    assert see_party[0].year == "1940"


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
