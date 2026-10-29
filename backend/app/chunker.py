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

def create_bullet_chunks(sections: dict[str, list[dict]]) -> list[dict]:
    chunks = []
    for section, lines in sections.items():
        if section == "header":
            continue

        has_bullets = any(line["is_bullet"] for line in lines)
        context = ""
        counter = 0

        for line in lines:
            if has_bullets and not line["is_bullet"] and section != "summary":
                context = line["text"]
                continue

            counter += 1
            text = line["text"]
            chunks.append({
                "id": f"{section}_{counter}",
                "section": section,
                "context": context,
                "text": text,
                "search_text": f"{context}: {text}" if context else text,
            })
    return chunks