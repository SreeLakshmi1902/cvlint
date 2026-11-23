from app.llm_client import generate_structured
from app.schemas import CritiqueSummary

def build_evidence_block(chunks: list[dict]) -> str:
    block = ""
    for chunk in chunks:
        context = f" ({chunk['context']})" if chunk["context"] else ""
        block += f"[{chunk['id']}] {chunk['section']}{context}: {chunk['text']}\n"
    return block

SUMMARY_PROMPT = """You are a technical recruiter. A resume has already been checked against each job requirement. The verdicts below are final and were verified against resume evidence.

JOB TITLE: {job_title}

VERDICTS:
{verdicts}

Write:
- overall_match: strong, moderate, weak or insufficient.
- summary: 2 sentences that agree with the verdicts.
- recommendations: the 3 most useful actions, priorities 1 to 3. action and why are one sentence each.

Rules:
- Do not contradict the verdicts. A "met" requirement is a strength, never a gap.
- For a "missing" requirement, recommend learning it or building a project that uses it. Never recommend adding, listing or highlighting a skill the candidate does not have.
- Prioritise must-have requirements over nice-to-have ones.
"""

MAX_RECOMMENDATIONS = 3

def build_verdict_lines(requirements: list[dict]) -> str:
    return "\n".join(
        f"- {r['name']} ({r['importance'].replace('_', ' ')}): {r['verdict']}. {r['verdict_reason']}"
        for r in requirements
    )

def derive_points(requirements: list[dict]) -> tuple[list[dict], list[dict]]:
    strengths, weak_areas = [], []
    for r in requirements:
        if r["verdict"] == "met":
            strengths.append({"point": f"{r['name']}: {r['verdict_reason']}",
                              "evidence_ids": r["verdict_evidence"]})
        else:
            weak_areas.append({"point": f"{r['name']} ({r['verdict'].replace('_', ' ')}): {r['verdict_reason']}",
                               "evidence_ids": r["verdict_evidence"]})
    return strengths, weak_areas

def generate_critique(job_title: str, requirements: list[dict]) -> dict:
    prompt = SUMMARY_PROMPT.format(job_title=job_title, verdicts=build_verdict_lines(requirements))
    summary = generate_structured(prompt, CritiqueSummary, label="generate_critique").model_dump()
    strengths, weak_areas = derive_points(requirements)
    return {
        "overall_match": summary["overall_match"],
        "summary": summary["summary"],
        "strengths": strengths,
        "weak_areas": weak_areas,
        "recommendations": summary["recommendations"][:MAX_RECOMMENDATIONS],
    }