from app.llm_client import generate_structured
from app.schemas import ResumeCritique, CompactCritique
        
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

def generate_evidence_critique(job_description: str, match_result: dict,
                               evidence_chunks: list[dict], sections: dict) -> dict:
    prompt = f"""You are an experienced technical recruiter and ATS resume reviewer.
    Review the resume against the job description.

    You are given:
    1. A compact overview of all resume sections
    2. Relevant resume bullets, each with an ID in square brackets
    3. Requirements extracted from the job description, grouped by keyword-match status

    JOB DESCRIPTION:
    {job_description}

    MATCHED REQUIREMENTS:
    {match_result["matched"]}

    MISSING TECHNICAL REQUIREMENTS:
    {match_result["missing"]}

    REQUIREMENTS TO JUDGE FROM THE EVIDENCE (keyword matching could not decide these):
    {match_result["needs_review"]}

    RESUME OVERVIEW:
    {build_overview(sections)}

    RELEVANT RESUME BULLETS:
    {build_evidence_block(evidence_chunks)}

    Evaluate the resume in this order:
    1. Assess the overall match as strong, moderate, weak, or insufficient. Do not give a number.
    2. Identify strengths, supported by resume evidence.
    3. Identify missing skills and weak areas.
    4. Identify ATS or keyword issues.
    5. Give the three highest-priority recommendations.

    Rules:
    - In every "evidence" field, quote the relevant resume text and include its bullet ID in square brackets, e.g. [experience_5].
    - Judge the "requirements to judge from the evidence" using the resume bullets and overview.
    - Do not say a section is missing unless the overview says it is missing.
    - Do not invent skills, experience, projects, companies or certifications.
    - Base every conclusion only on the provided resume information. If evidence is not present, say it could not be found.
    - Never advise the candidate to claim experience they do not have. When a required skill is missing, recommend learning it, building a project, or adding existing evidence.
    - Treat missing required job-description terms as ATS keyword issues.
    - Do not list certifications, degrees or years of experience as missing unless the job description explicitly requires them.
    - Do not repeat the same issue in multiple sections.
    - The summary must be 2 to 3 concise sentences explaining the overall match.
    - For each strength, explain why it matters. For each missing skill, explain why it matters for this job. For each ATS issue, explain the impact and the fix. For each recommendation, explain why it matters and the concrete action to take.
    - Return exactly three recommendations, with priorities 1, 2 and 3.
    - Prefer evidence from experience and project bullets. Use the summary only when no other evidence exists, because the summary is the candidate's own claim.
    - Only recommend adding a keyword to the resume if the evidence shows the candidate already has that skill. For skills with no evidence, recommend building a project that uses them instead.
    """
    return generate_structured(prompt, ResumeCritique, label="generate_evidence_critique").model_dump()


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