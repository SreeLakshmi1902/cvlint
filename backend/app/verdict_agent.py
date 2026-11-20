from app.critique_agent import build_evidence_block

MAX_VERDICT_EVIDENCE = 3

VERDICT_PROMPT = """You judge whether a resume meets each job requirement, using only the resume bullets provided.

RESUME BULLETS (each has an ID in square brackets):
{bullets}
REQUIREMENTS (each lists the bullet IDs most likely to contain evidence):
{requirements}

For every requirement, return one verdict:
- requirement_id: exactly as given, e.g. req_1.
- verdict: "met" if the bullets clearly show it; "partial" if they show only part of it (for example less experience than required, or a related but different skill); "missing" if no bullet shows it.
- evidence_ids: the bullet IDs that support the verdict, written without brackets. Empty for "missing".
- reason: one sentence explaining the verdict.

Rules:
- Judge only from the bullets. Do not assume skills that are not written.
- A bullet must actually show the requirement; a similar-sounding word is not enough.
- For years of experience, use the dates shown with each role.
- The summary is the candidate's own claim; prefer experience, project and education bullets.
"""

def build_requirement_lines(requirements: list[dict]) -> str:
    lines = []
    for number, r in enumerate(requirements, start=1):
        importance = r["importance"].replace("_", " ")
        candidates = ", ".join(r["candidate_ids"])
        lines.append(f'- req_{number}: {r["name"]} ({importance}): "{r["source_quote"]}" | candidates: {candidates}')
    return "\n".join(lines)

def build_verdict_prompt(requirements: list[dict], evidence_chunks: list[dict]) -> str:
    return VERDICT_PROMPT.format(
        bullets=build_evidence_block(evidence_chunks),
        requirements=build_requirement_lines(requirements),
    )

def clean_id(raw: str) -> str:
    return raw.strip().strip("[]")

def attach_verdicts(report: dict, requirements: list[dict]) -> list[dict]:
    by_id = {clean_id(v["requirement_id"]): v for v in report["verdicts"]}
    results = []
    for number, requirement in enumerate(requirements, start=1):
        verdict = by_id.get(f"req_{number}")
        if verdict is None:
            results.append({**requirement, "verdict": "not_judged", "verdict_evidence": [],
                            "verdict_reason": "The model did not return a verdict for this requirement."})
            continue
        evidence = list(dict.fromkeys(clean_id(e) for e in verdict["evidence_ids"]))[:MAX_VERDICT_EVIDENCE]
        results.append({**requirement, "verdict": verdict["verdict"], "verdict_evidence": evidence,
                        "verdict_reason": verdict["reason"]})
    return results