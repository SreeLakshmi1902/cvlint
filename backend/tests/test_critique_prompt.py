from app.critique_agent import build_compact_prompt

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