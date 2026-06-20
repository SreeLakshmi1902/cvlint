def create_resume_chunks(sections: dict) -> list:
    chunks = []

    for section_name, lines in sections.items():
        if section_name == "header":
            continue

        section_text = " ".join(lines)

        if section_text.strip():
            chunks.append({
                "section": section_name,
                "text": section_text
            })

    return chunks