from app.llm_client import generate_structured
from app.schemas import JobRequirements

EXTRACTION_PROMPT = """You extract candidate requirements from a job description for resume matching.

Rules:
- Create one requirement per distinct skill, technology, qualification or kind of experience.
- "name" must be short, as it would appear on a resume: "Python", "RAG", "Docker", "Communication". Never a full sentence.
- Use the bare technology name without extra words: "RAG" not "RAG pipelines", "Python" not "Python programming", "AWS" not "AWS services".
- When the job accepts alternatives ("AWS, Azure or GCP"), create one requirement with name "AWS" and alternatives ["Azure", "GCP"].
- "and" or a list without "or" means each item is required separately: "Docker and Kubernetes" becomes two requirements. Only "or" creates alternatives.
- Items listed under a heading such as "Nice to have", "Preferred" or "Bonus" are nice_to_have, even if the line itself does not say so.
- If a line states years of experience with a skill ("2+ years of Python"), set min_years on that skill's requirement (2) and do not create a separate requirement for the years.
- Named technologies, tools and techniques are always separate requirements, even in one phrase: "building RAG pipelines and working with vector databases" gives "RAG" and "Vector databases". Only general practices or qualities listed together stay as one requirement ("testing, security and maintainability"). Do not create a requirement that repeats another one.
- category: "technical" for languages, frameworks, tools, platforms and techniques; "domain" for industry knowledge; "soft_skill"; "qualification" for degrees and certifications; "experience" for years or kinds of experience.
- importance: "nice_to_have" when the text says preferred, desirable, bonus, a plus or similar; otherwise "must_have".
- Take requirements mainly from sections that describe the candidate ("Requirements", "What you'll bring", "About you"). From responsibilities, add only named technologies or tools that are not already listed.
- Never use a generic word on its own as a requirement name, such as "software", "secure" or "controls".
- source_quote must be copied exactly from the job description.
- Do not include benefits, company information, or anything the job description does not state.

JOB DESCRIPTION:
{job_description}
"""

def extract_requirements(job_description: str) -> JobRequirements:
    prompt = EXTRACTION_PROMPT.format(job_description=job_description)
    return generate_structured(prompt, JobRequirements, label="extract_requirements")

CHARACTER_MAP = str.maketrans({
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-", "\u2212": "-",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u00a0": " ",
})

def normalize_text(text: str) -> str:
    return " ".join(text.translate(CHARACTER_MAP).lower().split())

def verify_quotes(job: JobRequirements, job_description: str) -> list[dict]:
    jd = normalize_text(job_description)
    return [
        {**requirement.model_dump(), "quote_verified": normalize_text(requirement.source_quote) in jd}
        for requirement in job.requirements
    ]