from legalcite.names import compare_names, normalize_name


def test_normalization_drops_v_and_entities():
    text, tokens = normalize_name("Smith v. Jones, Inc.")
    assert text == "smith jones"
    assert "inc" not in tokens


def test_abbreviation_expansion():
    a, _ = normalize_name("Dep't of Education v. Smith")
    b, _ = normalize_name("Department of Education v. Smith")
    assert a == b


def test_exact_match_scores_100():
    score, overlap = compare_names("Obergefell v. Hodges", "Obergefell v. Hodges")
    assert score == 100.0
    assert overlap is True


def test_partial_match_is_in_between():
    score, _ = compare_names("Taylor v. Reed", "Taylor v. Reid, Commissioner")
    assert 40 < score < 85, score


def test_clear_mismatch_scores_low_without_overlap():
    score, overlap = compare_names("Hunt v. Smith", "Bargo v. Bargo")
    assert score <= 40, score
    assert overlap is False


def test_shared_surname_alone_is_not_identity():
    # Distinctive overlap is True, but the score must not be forced to 100.
    score, overlap = compare_names("Smith v. Jones", "Smith v. Johnson")
    assert overlap is True
    assert score < 100.0, score
