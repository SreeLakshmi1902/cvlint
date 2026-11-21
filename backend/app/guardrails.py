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