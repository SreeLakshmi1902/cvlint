from docx import Document

def extract_docx_text(file_path: str) -> str:
    document = Document(file_path)
    text = ""
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"
    return text

def extract_sections(text: str):
    section_headers = {
        "education", 
        "professional experience", 
        "technical skills", 
        "projects",
        "certifications"
    }
    sections = {}
    current_section = "header"
    sections[current_section] = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        normalized_line = line.lower()
        if normalized_line in section_headers:
            current_section = normalized_line
            sections[current_section] = []
        else:
            sections[current_section].append(line)
    return sections

def extract_skills(sections):
    skills_text = ""
    if "technical skills" in sections:
        skills_text = " ".join(sections["technical skills"])
    skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
    return skills