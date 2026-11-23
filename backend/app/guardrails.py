import re

from app.skill_matcher import appears_in_text, text_forms

CLAIM_WORDS = re.compile(r"\b(add|adding|list|listing|include|including|mention|highlight|highlighting|emphasi[sz]e|claim)\b")
LEARN_WORDS = re.compile(r"\b(build|building|learn|learning|create|develop|complete|take|enrol|enroll|practi[sc]e|project|course|certification|study)\b")

def missing_skill_forms(requirements: list[dict]) -> dict[str, set[str]]:
    forms = {}
    for r in requirements:
        if r["verdict"] == "missing":
            for option in [r["name"], *r.get("alternatives", [])]:
                forms[option] = text_forms(option)
    return forms

def check_recommendations(recommendations: list[dict], requirements: list[dict]) -> tuple[list[dict], list[str]]:
    forms_by_skill = missing_skill_forms(requirements)
    kept, notes = [], []
    for rec in recommendations:
        text = f"{rec['action']} {rec['why']}".lower()
        mentioned = [skill for skill, forms in forms_by_skill.items()
                     if any(appears_in_text(form, text) for form in forms)]
        if mentioned and CLAIM_WORDS.search(text) and not LEARN_WORDS.search(text):
            notes.append(f"Removed a recommendation to add or highlight missing skills "
                         f"({', '.join(mentioned)}): {rec['action']}")
            continue
        kept.append(rec)
    return kept, notes

def validate_citations(requirement: dict, shown_ids: set[str]) -> dict:
    valid = [e for e in requirement["verdict_evidence"] if e in shown_ids]
    invalid = [e for e in requirement["verdict_evidence"] if e not in shown_ids]
    verdict = requirement["verdict"]
    notes = list(requirement.get("guardrail_notes", []))
    if invalid:
        notes.append(f"Removed citations that were not shown to the model: {', '.join(invalid)}.")
    if verdict in ("met", "partial") and not valid:
        verdict = "unverified"
        notes.append("The verdict had no valid evidence, so it is marked unverified.")
    return {**requirement, "verdict": verdict, "verdict_evidence": valid, "guardrail_notes": notes}

def enforce_keyword_consistency(requirement: dict) -> dict:
    if requirement["status"] == "missing" and requirement["verdict"] == "met":
        notes = list(requirement.get("guardrail_notes", []))
        notes.append("The skill does not appear anywhere in the resume, so 'met' was downgraded to 'partial'.")
        return {**requirement, "verdict": "partial", "guardrail_notes": notes}
    return requirement

def apply_verdict_guardrails(requirements: list[dict], shown_ids: set[str]) -> list[dict]:
    return [enforce_keyword_consistency(validate_citations(r, shown_ids)) for r in requirements]