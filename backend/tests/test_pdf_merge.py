from app.parser import merge_visual_lines


def visual(text, x0=36, x1=550, size=10.0, starts_bold=False, ends_bold=False):
    return {"text": text, "x0": x0, "x1": x1, "size": size, "starts_bold": starts_bold, "ends_bold": ends_bold}


def texts(lines):
    return [line["text"] for line in lines]


def test_wrapped_lines_are_joined():
    lines = merge_visual_lines([
        visual("Software engineer with experience building"),
        visual("backend services.", x1=200),
    ])
    assert texts(lines) == ["Software engineer with experience building backend services."]


def test_a_short_line_ends_its_paragraph():
    lines = merge_visual_lines([
        visual("Languages: Python, Java", x1=200),
        visual("Databases: MySQL"),
    ])
    assert texts(lines) == ["Languages: Python, Java", "Databases: MySQL"]


def test_bullet_continuations_join_but_new_bullets_start_new_lines():
    lines = merge_visual_lines([
        visual("\u2022 Built REST APIs in Python and FastAPI for", x0=55),
        visual("internal tools.", x0=74, x1=150),
        visual("\u2022 Deployed services with Docker", x0=55, x1=300),
    ])
    assert texts(lines) == ["Built REST APIs in Python and FastAPI for internal tools.", "Deployed services with Docker"]
    assert all(line["is_bullet"] for line in lines)


def test_a_line_starting_further_left_is_not_joined():
    lines = merge_visual_lines([
        visual("0400 000 000 | jane@example.com | LinkedIn", x0=100, x1=500),
        visual("Software engineer with experience building", x0=36),
    ])
    assert len(lines) == 2


def test_a_change_in_boldness_starts_a_new_line():
    lines = merge_visual_lines([
        visual("Co-facilitated a university hackathon with senior stakeholders"),
        visual("Associate Engineer | Acme Corp", starts_bold=True, ends_bold=True, x1=300),
    ])
    assert len(lines) == 2


def test_larger_text_becomes_a_heading():
    lines = merge_visual_lines([
        visual("TECHNICAL SKILLS", size=12.0, starts_bold=True, ends_bold=True, x1=125),
        visual("Languages: Python, Java", x1=200),
        visual("Databases: MySQL", x1=150),
        visual("A full-width line that shows where the right margin is"),
    ])
    assert [line["style"] for line in lines] == ["heading", "normal", "normal", "normal"]