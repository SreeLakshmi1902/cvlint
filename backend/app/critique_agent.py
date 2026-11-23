from app.llm_client import generate_structured
from app.schemas import CritiqueSummary
from app.guardrails import check_recommendations

def build_evidence_block(chunks: list[dict]) -> str:
    block = ""
    for chunk in chunks:
        context = f" ({chunk['context']})" if chunk["context"] else ""
        block += f"[{chunk['id']}] {chunk['section']}{context}: {chunk['text']}\n"
    return block

SUMMARY_PROMPT = """You are a technical recruiter. A resume has already been checked against each job requirement. The verdicts below are final and were verified against resume evidence.

JOB TITLE: {job_title}
OVERALL MATCH (computed from the verdicts): {overall_match} ({score}%)

VERDICTS:
{verdicts}

Write:
- summary: 2 sentences that agree with the verdicts.
- recommendations: the 3 most useful actions, priorities 1 to 3. action and why are one sentence each.

Rules:
- Do not contradict the verdicts. A "met" requirement is a strength, never a gap.
- Describe a "partial" requirement as partly met, not as missing.
- Each recommendation must be a concrete action the candidate can complete in the next few months, such as learning a missing skill through a project or course, or making existing evidence clearer.
- For a "missing" requirement, recommend learning it or building a project that uses it. Never recommend adding, listing or highlighting a skill the candidate does not have.
- Do not recommend gaining years of experience, changing jobs, or work on requirements that are already met.
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

def generate_critique(job_title: str, requirements: list[dict], score: dict) -> dict:
    prompt = SUMMARY_PROMPT.format(job_title=job_title, overall_match=score["overall_match"], score=score["score"],verdicts=build_verdict_lines(requirements))
    summary = generate_structured(prompt, CritiqueSummary, label="generate_critique").model_dump()
    strengths, weak_areas = derive_points(requirements)
    recommendations, recommendation_notes = check_recommendations(summary["recommendations"], requirements)
    recommendations = recommendations[:MAX_RECOMMENDATIONS]
    
    for priority, rec in enumerate(recommendations, start=1):
        rec["priority"] = priority
        
    return {
        "overall_match": score["overall_match"],
        "summary": summary["summary"],
        "strengths": strengths,
        "weak_areas": weak_areas,
        "recommendations": recommendations,
        "recommendation_notes": recommendation_notes
    }