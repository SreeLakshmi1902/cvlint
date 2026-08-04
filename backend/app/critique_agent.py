from app.llm_client import generate_response

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
    
    Give a clear and useful critique of the resume.
    Mention:
    - how well the resume matches the job 
    - strengths
    - missing or weak areas
    - ATS/keyword issues
    - practical recommendations for improvement
    """
    
    response = generate_response(prompt)
    return response