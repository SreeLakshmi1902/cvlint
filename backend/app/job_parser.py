def extract_job_skills(job_description: str):
    skills = [
        "Python",
        "FastAPI",
        "Docker",
        "AWS",
        "Machine Learning",
        "Deep Learning",
        "SQL",
        "React"
    ]
    found_skills = []
    for skill in skills:
        if skill.lower() in job_description.lower():
            found_skills.append(skill)
    return found_skills

def compare_skills(resume_skills: list, job_skills: list):
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    matched_skills = []
    missing_skills = []
    for skill in job_skills:
        if skill.lower() in resume_skills_lower:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
    if len(job_skills) == 0:
        score = 0
    else:
        score = round((len(matched_skills) / len(job_skills)) * 100)
    return matched_skills, missing_skills, score