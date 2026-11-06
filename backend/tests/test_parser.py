import pytest
from docx import Document
from app.chunker import create_bullet_chunks
from app.parser import build_sections, extract_docx_lines, extract_skill_list, strip_bullet

@pytest.fixture
def resume_path(tmp_path):
    doc = Document()
    doc.add_heading("JANE DOE", level=1)
    doc.add_paragraph("0400 000 000 | jane@example.com | LinkedIn")
    doc.add_paragraph(
        "Software engineer with three years of experience building backend services "
        "and integrating large language models into products."
    )
    doc.add_heading("PROFESSIONAL EXPERIENCE", level=2)
    doc.add_paragraph("Backend Engineer | Acme Corp 2022 - 2024")
    doc.add_paragraph("\u2022 Built REST APIs in Python and FastAPI")
    doc.add_paragraph("\u2022 Deployed services with Docker")
    doc.add_heading("TECHNICAL SKILLS", level=2)
    doc.add_paragraph("FRONTEND")
    doc.add_paragraph("\u2022 React.js, HTML, CSS")
    doc.add_paragraph("Languages: Python, Java")
    path = tmp_path / "resume.docx"
    doc.save(path)
    return path

@pytest.fixture
def sections(resume_path):
    return build_sections(extract_docx_lines(str(resume_path)))

@pytest.mark.parametrize("text, expected", [
    ("\u2022 Built APIs", ("Built APIs", True)),
    ("1. Designed systems", ("Designed systems", True)),
    ("a) Reviewed code", ("Reviewed code", True)),
    ("3.5 years of experience", ("3.5 years of experience", False)),
    ("$100k budget", ("$100k budget", False)),
    ("(Team Project)", ("(Team Project)", False)),
])
def test_strip_bullet(text, expected):
    assert strip_bullet(text) == expected

def test_typed_bullets_are_detected_and_stripped(resume_path):
    lines = extract_docx_lines(str(resume_path))
    assert {"text": "Deployed services with Docker", "is_bullet": True, "style": "normal"} in lines

def test_sections_are_detected_by_name(sections):
    assert {"header", "summary", "experience", "skills"} <= set(sections)

def test_summary_is_moved_out_of_the_header(sections):
    assert [line["text"] for line in sections["header"]] == [
        "JANE DOE", "0400 000 000 | jane@example.com | LinkedIn",
    ]
    assert sections["summary"][0]["text"].startswith("Software engineer")

def test_skills_skip_category_labels_and_prefixes(sections):
    assert extract_skill_list(sections) == ["React.js", "HTML", "CSS", "Python", "Java"]

def test_chunks_keep_their_role_and_skip_contact_details(sections):
    chunks = create_bullet_chunks(sections)
    docker = next(chunk for chunk in chunks if "Docker" in chunk["text"])
    assert docker["context"] == "Backend Engineer | Acme Corp 2022 - 2024"
    assert len({chunk["id"] for chunk in chunks}) == len(chunks)
    assert not any("@" in chunk["text"] for chunk in chunks)

def test_word_list_style_bullets_are_detected(tmp_path):
    doc = Document()
    doc.add_paragraph("Built APIs", style="List Bullet")
    path = tmp_path / "styled.docx"
    doc.save(path)
    assert extract_docx_lines(str(path))[0]["is_bullet"] is True