from app.skill_matcher import canonical_forms, match_requirements

def req(name, category="technical", importance="must_have", alternatives=None):
    return {"name": name, "category": category, "importance": importance, "alternatives": alternatives or []}

RESUME_SKILLS = ["React.js", "MySQL", "Large Language Models (LLMs)", "PyTorch", "Java", "Docker"]
RESUME_TEXT = "developed rest apis using java, spring boot and mysql. built the frontend with react.js."

def test_aliases_map_to_one_standard_name():
    assert canonical_forms("React.js") == {"react"}
    assert canonical_forms("ReactJS") == {"react"}

def test_brackets_give_both_full_name_and_abbreviation():
    assert "llms" in canonical_forms("Large Language Models (LLMs)")

def test_generic_trailing_words_are_stripped():
    assert "rag" in canonical_forms("RAG pipelines")

def test_aliases_and_implications_count_as_matches():
    result = match_requirements([req("React"), req("SQL"), req("LLM"), req("Deep Learning")], RESUME_SKILLS, RESUME_TEXT)
    assert result["matched"] == ["React", "SQL", "LLM", "Deep Learning"]

def test_unknown_technical_skill_is_missing():
    result = match_requirements([req("Kubernetes")], RESUME_SKILLS, RESUME_TEXT)
    assert result["missing"] == ["Kubernetes"]

def test_alternative_satisfies_requirement():
    result = match_requirements([req("AWS", alternatives=["Azure", "Docker"])], RESUME_SKILLS, RESUME_TEXT)
    assert result["requirements"][0]["matched_as"] == "Docker"

def test_soft_skills_need_review_instead_of_missing():
    result = match_requirements([req("Communication", category="soft_skill")], RESUME_SKILLS, RESUME_TEXT)
    assert result["needs_review"] == ["Communication"]
    assert result["missing"] == []

def test_short_skill_names_do_not_match_ordinary_words():
    result = match_requirements([req("Go")], [], "we go to great lengths to test our code.")
    assert result["missing"] == ["Go"]

def test_coverage_weights_must_haves_double():
    result = match_requirements([req("Java"), req("Kubernetes", importance="nice_to_have")], RESUME_SKILLS, RESUME_TEXT)
    assert result["technical_coverage"] == 67

def test_coverage_is_none_without_technical_requirements():
    result = match_requirements([req("Communication", category="soft_skill")], RESUME_SKILLS, RESUME_TEXT)
    assert result["technical_coverage"] is None