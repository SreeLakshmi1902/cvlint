from app.parser import (extract_docx_text, extract_sections)

resume_path = "Resume.docx"

resume_text = extract_docx_text(resume_path)

sections = extract_sections(resume_text)

for section_name, content in sections.items():
    print("\n")
    print("=" * 50)
    print(section_name)
    print("=" * 50)
    
    for line in content:
        print(line)