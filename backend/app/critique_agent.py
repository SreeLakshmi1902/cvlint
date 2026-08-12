import json 
from app.llm_client import generate_response
from app.schemas import ResumeCritique

def summarize_section(section_name: str, section_text: str, max_lines: int = 3):
    if not section_text:
        return "Missing or empty section"
    lines = [line.strip() for line in section_text if line.strip()]
    selected_lines = lines[:max_lines]
    return " | ".join(selected_lines)

def build_resume_overview(sections:dict):
    resume_overview = ""
    for section_name, section_text in sections.items():
        status = "present" if section_text else "missing"
        summary = summarize_section(section_name, section_text)
        resume_overview += f"SECTION: {section_name}\n"
        resume_overview += f"STATUS: {status}\n"
        resume_overview += f"SUMMARY: {summary}\n\n"        
    return resume_overview

def generate_critique(
    job_description: str,
    matched_skills: list,
    missing_skills: list,
    hybrid_results: list,
    sections: dict
):
    resume_overview = build_resume_overview(sections)
    resume_context = ""
    for result in hybrid_results:
        resume_context += f"\nSECTION: {result.get('section','unknown')}\n"
        resume_context += f"CONTENT: {result.get('text', '')}\n"
    prompt = f"""
    You are an experienced technical recruiter and ATS resume reviewer.
    Review the resume against the job description.
    
    IMPORTANT: 
    You are seeing 
    1. A compact overview of all resume sections
    2. Selected relevant resume chunks 
    
    Use the resume overview to understand what sections exist.
    Use the relevant resume chunks as detailed evidence.
    Do not say a section is missing unless the resume overview says it is missing.
    Do not invent skills, experience, projects, companies or certifications.
    
    JOB DESCRIPTION:
    {job_description}

    MATCHED SKILLS:
    {matched_skills}

    MISSING SKILLS:
    {missing_skills}
    
    RESUME OVERVIEW:
    {resume_overview}

    RELEVANT RESUME SECTIONS:
    {resume_context}
    
    Evaluate the resume in this order:

    1. Assess the overall match qualitatively as strong, moderate, weak, or insufficient. Do not provide a numerical percentage or score.
    2. Identify strengths using evidence from the resume overview or relevant resume sections.
    3. Identify missing skills and weak areas.
    4. Identify ATS or keyword issues.
    5. Give the three highest-priority recommendations that would most improve the resume's match to the job description.

    Rules:
    - Support each strength with specific resume evidence.
    - Do not repeat the same issue in multiple sections.
    - Do not recommend adding a skill unless the candidate genuinely has that skill or can demonstrate it through a project.
    - If something cannot be determined from the provided information, say that it cannot be determined.
    - Keep the critique concise and practical.
    - Treat required or strongly preferred job-description terms that are absent from the resume as keyword gaps.
    - Do not say there are no ATS issues when important job keywords are missing.
    - Base every conclusion only on the provided resume information.
    - If evidence is not present, state that it could not be found rather than assuming it does not exist.
    - The summary must contain 2 to 3 concise sentences explaining the overall match.
    - If required job-description skills are missing from the resume, include them as ATS keyword issues.
    - Never advise the candidate to claim experience they do not have.
    - Recommend learning, building a project, or adding existing evidence when a required skill is missing.
    - Do not leave summary, strengths, missing_skills, ats_issues, or recommendations empty when relevant evidence or gaps are provided.
    - Be detailed enough that each strength, issue, and recommendation is understandable on its own.
    - For each strength, explain why it matters and cite specific resume evidence.
    - For each missing skill, explain why it matters for this job.
    - For each ATS issue, explain the impact and how to fix it.
    - For each recommendation, explain both why it matters and what concrete action the candidate should take.
    - Do not identify certifications, degrees, years of experience, or other requirements as missing unless they are explicitly required or strongly preferred in the job description.
    - Distinguish between a missing skill and a missing certification. A missing technology or skill does not imply that a certification is required.
    
    Return ONLY valid JSON in this exact structure:
    
    {{
        "overall_match": "moderate",
        "summary": "",
        "strengths": [
            {{
            "title": "",
            "explanation": "",
            "evidence": ""
            }}
        ],
        "missing_skills": [
            {{
            "skill": "",
            "why_it_matters": "",
            "evidence": ""
            }}
        ],
        "ats_issues": [
            {{
            "issue": "",
            "impact": "",
            "fix": ""
            }}
        ],
        "recommendations": [
            {{
            "priority": 1,
            "recommendation": "",
            "why": "",
            "how_to_improve": ""
            }}
        ]
    }}
    
    JSON rules: 
    - Do not include markdown.
    - Do not include text outside the JSON.
    - Use double quotes for all keys and string values.
    - Return exactly three recommendations. 
    """

    response = generate_response(prompt)
    
    try: 
        critique_data = json.loads(response, strict=False)
        validated_critique = ResumeCritique(**critique_data)
        return validated_critique.model_dump()
    
    except (json.JSONDecodeError, ValueError) as error:
        return{
            "error": "The model did not return valid structured output.",
            "details": str(error),
            "raw_response": response
        }