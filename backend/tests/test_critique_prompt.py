from app.critique_agent import build_verdict_lines, derive_points

MATCH_RESULT = {"requirements": [
    {"name": "Python", "alternatives": [], "category": "technical",
     "importance": "must_have", "status": "matched"},
    {"name": "AWS", "alternatives": ["Azure"], "category": "technical",
     "importance": "nice_to_have", "status": "missing"},
    {"name": "Communication", "alternatives": [], "category": "soft_skill",
     "importance": "must_have", "status": "needs_review"},
]}

VERDICTS = [
    {"name": "Docker", "importance": "nice_to_have", "verdict": "met",
     "verdict_reason": "Containerised ML code.", "verdict_evidence": ["experience_1"]},
    {"name": "Python", "importance": "must_have", "verdict": "partial",
     "verdict_reason": "Only 6 months professional.", "verdict_evidence": ["experience_1"]},
    {"name": "RAG", "importance": "must_have", "verdict": "missing",
     "verdict_reason": "No RAG work.", "verdict_evidence": []},
]

def test_met_requirements_become_strengths_and_others_weak_areas():
    strengths, weak_areas = derive_points(VERDICTS)
    assert [s["point"] for s in strengths] == ["Docker: Containerised ML code."]
    assert weak_areas[0]["point"] == "Python (partial): Only 6 months professional."
    assert weak_areas[1]["evidence_ids"] == []

def test_verdict_lines_give_the_model_each_verdict_and_reason():
    lines = build_verdict_lines(VERDICTS).splitlines()
    assert lines[1] == "- Python (must have): partial. Only 6 months professional."