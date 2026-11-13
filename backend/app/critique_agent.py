from app.llm_client import generate_structured
from app.schemas import CompactCritique

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