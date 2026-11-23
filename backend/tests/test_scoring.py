from app.scoring import match_band, verdict_score

def req(verdict, importance="must_have"):
    return {"verdict": verdict, "importance": importance}

LABEL_01 = [
    req("partial"), req("missing"), req("missing"), req("missing"), req("met"),
    req("met", "nice_to_have"), req("missing", "nice_to_have"), req("met", "nice_to_have"),
]

def test_label_01_scores_38_percent_and_weak():
    result = verdict_score(LABEL_01)
    assert result["score"] == 38
    assert result["overall_match"] == "weak"
    assert result["counts"]["met"] == 3

def test_not_judged_is_left_out_of_the_score_but_counted():
    result = verdict_score([req("met"), req("not_judged")])
    assert result["score"] == 100
    assert result["counts"]["not_judged"] == 1

def test_bands_use_the_highest_threshold_reached():
    assert match_band(75) == "strong"
    assert match_band(74) == "moderate"
    assert match_band(24) == "insufficient"
    assert match_band(None) is None