from app.llm_client import generate_structured
from app.schemas import JobRequirements

EXTRACTION_PROMPT = """You extract candidate requirements from a job description for resume matching.

Rules:
- Create one requirement per distinct skill, technology, qualification or kind of experience.
- "name" must be short, as it would appear on a resume: "Python", "RAG", "Docker", "Stakeholder communication". Never a full sentence.
- Use the bare technology name without extra words: "RAG" not "RAG pipelines", "Python" not "Python programming", "AWS" not "AWS services".
- Split combined items: "Python and SQL" becomes two requirements.
- When the job accepts alternatives ("AWS, Azure or GCP"), create one requirement with name "AWS" and alternatives ["Azure", "GCP"].
- category: "technical" for languages, frameworks, tools, platforms and techniques; "domain" for industry knowledge; "soft_skill"; "qualification" for degrees and certifications; "experience" for years or kinds of experience.
- importance: "nice_to_have" when the text says preferred, desirable, bonus, a plus or similar; otherwise "must_have".
- Technologies named in the responsibilities count as requirements.
- source_quote must be copied exactly from the job description.
- Do not include benefits, company information, or anything the job description does not state.

JOB DESCRIPTION:
{job_description}
"""

def extract_requirements(job_description: str) -> JobRequirements:
    prompt = EXTRACTION_PROMPT.format(job_description=job_description)
    return generate_structured(prompt, JobRequirements)

def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())

def verify_quotes(job: JobRequirements, job_description: str) -> list[dict]:
    jd = normalize_text(job_description)
    return [
        {**requirement.model_dump(), "quote_verified": normalize_text(requirement.source_quote) in jd}
        for requirement in job.requirements
    ]