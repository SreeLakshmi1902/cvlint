from app.llm_client import generate_structured
from app.schemas import CompactCritique, CritiqueSummary

OVERVIEW_LINES = 3

def build_overview(sections: dict[str, list[dict]]) -> str:
    overview = ""
    for name, lines in sections.items():
        if name == "header":
            continue
        texts = [line["text"] for line in lines]
        summary = " | ".join(texts[:OVERVIEW_LINES]) if texts else "Missing or empty section"
        overview += f"SECTION: {name}\nSTATUS: {'present' if texts else 'missing'}\nSUMMARY: {summary}\n\n"
    return overview

def build_evidence_block(chunks: list[dict]) -> str:
    block = ""
    for chunk in chunks:
        context = f" ({chunk['context']})" if chunk["context"] else ""
        block += f"[{chunk['id']}] {chunk['section']}{context}: {chunk['text']}\n"
    return block

STATUS_LABELS = {"matched": "matched", "missing": "missing", "needs_review": "needs judgment"}

COMPACT_CRITIQUE_PROMPT = """You are a technical recruiter reviewing a resume against a job's requirements.

JOB TITLE: {job_title}

REQUIREMENTS (status was decided by exact keyword matching):
{requirements}

RESUME OVERVIEW:
{overview}
RESUME BULLETS (each has an ID in square brackets):
{bullets}
Write a short critique:
- overall_match: strong, moderate, weak or insufficient.
- summary: 2 sentences.
- strengths: up to 3. Each point is one sentence. evidence_ids lists 1-2 bullet IDs that support it, written without brackets, e.g. experience_3. 
- weak_areas: up to 3, for requirements marked "needs judgment" or with thin evidence. One sentence each, citing bullet IDs if any.
- recommendations: exactly 3, priorities 1 to 3. action and why are one sentence each.

Rules:
- Use only bullet IDs shown above.
- Requirements marked "missing" are not on the resume. Never say the candidate has them. To address one, recommend learning it or building a project with it, never adding the keyword.
- Do not invent skills, experience or projects.
- Prefer experience and project bullets over the summary.
"""

def build_requirements_block(requirements: list[dict]) -> str:
    lines = []
    for r in requirements:
        name = " or ".join([r["name"], *r.get("alternatives", [])])
        importance = r["importance"].replace("_", " ")
        lines.append(f"- {name} ({r['category']}, {importance}): {STATUS_LABELS[r['status']]}")
    return "\n".join(lines)

def build_compact_prompt(job_title: str, match_result: dict,
                         evidence_chunks: list[dict], sections: dict) -> str:
    return COMPACT_CRITIQUE_PROMPT.format(
        job_title=job_title,
        requirements=build_requirements_block(match_result["requirements"]),
        overview=build_overview(sections),
        bullets=build_evidence_block(evidence_chunks),
    )

def clean_evidence_ids(critique: dict) -> dict:
    for section in ("strengths", "weak_areas"):
        for item in critique[section]:
            item["evidence_ids"] = [eid.strip().strip("[]") for eid in item["evidence_ids"]]
    return critique

def generate_compact_critique(job_title: str, match_result: dict,
                              evidence_chunks: list[dict], sections: dict) -> dict:
    prompt = build_compact_prompt(job_title, match_result, evidence_chunks, sections)
    critique = generate_structured(prompt, CompactCritique, label="generate_compact_critique").model_dump()
    return clean_evidence_ids(critique)




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