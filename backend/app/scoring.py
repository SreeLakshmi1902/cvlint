IMPORTANCE_WEIGHT = {"must_have": 2, "nice_to_have": 1}
VERDICT_CREDIT = {"met": 1.0, "partial": 0.5, "missing": 0.0, "unverified": 0.0}
MATCH_BANDS = [(75, "strong"), (50, "moderate"), (25, "weak"), (0, "insufficient")]
VERDICTS = ("met", "partial", "missing", "unverified", "not_judged")

def match_band(score: int | None) -> str | None:
    if score is None:
        return None
    for threshold, band in MATCH_BANDS:
        if score >= threshold:
            return band

def verdict_score(requirements: list[dict]) -> dict:
    scored = [r for r in requirements if r["verdict"] in VERDICT_CREDIT]
    total = sum(IMPORTANCE_WEIGHT[r["importance"]] for r in scored)
    earned = sum(IMPORTANCE_WEIGHT[r["importance"]] * VERDICT_CREDIT[r["verdict"]] for r in scored)
    score = round(100 * earned / total) if total else None
    counts = {v: sum(1 for r in requirements if r["verdict"] == v) for v in VERDICTS}
    return {"score": score, "overall_match": match_band(score), "counts": counts}