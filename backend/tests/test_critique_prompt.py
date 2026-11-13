from app.critique_agent import build_compact_prompt
from app.critique_agent import clean_evidence_ids

MATCH_RESULT = {"requirements": [
    {"name": "Python", "alternatives": [], "category": "technical",
     "importance": "must_have", "status": "matched"},
    {"name": "AWS", "alternatives": ["Azure"], "category": "technical",
     "importance": "nice_to_have", "status": "missing"},
    {"name": "Communication", "alternatives": [], "category": "soft_skill",
     "importance": "must_have", "status": "needs_review"},
]}

def test_each_requirement_has_one_line_with_its_status():
    prompt = build_compact_prompt("AI Engineer", MATCH_RESULT, [], {})
    assert "- Python (technical, must have): matched" in prompt
    assert "- AWS or Azure (technical, nice to have): missing" in prompt
    assert "- Communication (soft_skill, must have): needs judgment" in prompt

def test_prompt_lines_are_not_indented():
    prompt = build_compact_prompt("AI Engineer", MATCH_RESULT, [], {})
    assert not any(line.startswith("    ") for line in prompt.splitlines())
    
def test_brackets_are_stripped_from_evidence_ids():
    critique = {
        "strengths": [{"point": "x", "evidence_ids": ["[education_2]", "experience_1"]}],
        "weak_areas": [{"point": "y", "evidence_ids": []}],
    }
    cleaned = clean_evidence_ids(critique)
    assert cleaned["strengths"][0]["evidence_ids"] == ["education_2", "experience_1"]
    assert cleaned["weak_areas"][0]["evidence_ids"] == []