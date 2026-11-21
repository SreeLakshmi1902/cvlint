from app.guardrails import apply_verdict_guardrails, enforce_keyword_consistency, validate_citations

SHOWN = {"experience_1", "experience_4"}

def make(verdict, evidence, status="matched"):
    return {"name": "x", "status": status, "verdict": verdict, "verdict_evidence": evidence}

def test_citations_not_shown_to_the_model_are_removed():
    result = validate_citations(make("met", ["experience_1", "projects_9"]), SHOWN)
    assert result["verdict_evidence"] == ["experience_1"]
    assert result["verdict"] == "met"
    assert "projects_9" in result["guardrail_notes"][0]

def test_met_without_any_valid_evidence_becomes_unverified():
    result = validate_citations(make("met", ["projects_9"]), SHOWN)
    assert result["verdict"] == "unverified"

def test_missing_verdict_without_evidence_is_fine():
    result = validate_citations(make("missing", []), SHOWN)
    assert result["verdict"] == "missing"
    assert result["guardrail_notes"] == []

def test_met_for_a_keyword_missing_skill_is_downgraded():
    result = enforce_keyword_consistency(make("met", ["experience_1"], status="missing"))
    assert result["verdict"] == "partial"
    assert result["guardrail_notes"]

def test_matched_and_met_is_unchanged():
    requirement = make("met", ["experience_1"])
    assert apply_verdict_guardrails([requirement], SHOWN)[0]["verdict"] == "met"