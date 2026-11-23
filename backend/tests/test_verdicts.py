from app.verdict_agent import attach_verdicts, build_requirement_lines

REQUIREMENTS = [
    {"name": "Python", "importance": "must_have", "source_quote": "2+ years of Python",
     "candidate_ids": ["summary_1", "experience_1"]},
    {"name": "RAG", "importance": "must_have", "source_quote": "Experience building RAG",
     "candidate_ids": ["experience_8"]},
]

def test_each_requirement_gets_a_numbered_line_with_its_candidates():
    lines = build_requirement_lines(REQUIREMENTS).splitlines()
    assert lines[0] == '- req_1: Python (must have): "2+ years of Python" | candidates: summary_1, experience_1'
    assert lines[1].startswith("- req_2: RAG")

def test_verdicts_are_matched_to_requirements_by_id():
    report = {"verdicts": [
        {"requirement_id": "req_2", "verdict": "missing", "evidence_ids": [], "reason": "No RAG work."},
        {"requirement_id": "req_1", "verdict": "partial", "evidence_ids": ["experience_1"], "reason": "Under 2 years."},
    ]}
    results = attach_verdicts(report, REQUIREMENTS)
    assert results[0]["verdict"] == "partial"
    assert results[1]["verdict"] == "missing"

def test_evidence_is_cleaned_deduplicated_and_capped():
    report = {"verdicts": [{"requirement_id": "[req_1]", "verdict": "met", "reason": "x",
                            "evidence_ids": ["[a]", "a", "b", "c", "d"]}]}
    results = attach_verdicts(report, REQUIREMENTS[:1])
    assert results[0]["verdict_evidence"] == ["a", "b", "c"]

def test_requirement_without_a_verdict_is_marked_not_judged():
    report = {"verdicts": [{"requirement_id": "req_1", "verdict": "met", "evidence_ids": [], "reason": "x"}]}
    results = attach_verdicts(report, REQUIREMENTS)
    assert results[1]["verdict"] == "not_judged"
    
def test_min_years_is_shown_to_the_verdict_model():
    requirement = {**REQUIREMENTS[0], "min_years": 2.0}
    line = build_requirement_lines([requirement])
    assert "(must have, at least 2 years)" in line