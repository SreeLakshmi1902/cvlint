import re

ALIASES = {
    "react.js": "react", "reactjs": "react", "react js": "react",
    "node": "node.js", "nodejs": "node.js",
    "js": "javascript", "ts": "typescript",
    "large language models": "llms", "large language model": "llms", "llm": "llms",
    "natural language processing": "nlp",
    "retrieval augmented generation": "rag", "retrieval-augmented generation": "rag",
    "generative ai": "genai", "gen ai": "genai",
    "ml": "machine learning",
    "scikit learn": "scikit-learn", "sklearn": "scikit-learn",
    "amazon web services": "aws", "microsoft azure": "azure",
    "google cloud platform": "gcp", "google cloud": "gcp",
    "postgres": "postgresql", "k8s": "kubernetes",
    "rest api": "rest apis", "restful apis": "rest apis", "restful api": "rest apis",
    "ci cd": "ci/cd", "cicd": "ci/cd",
    "oop": "object-oriented programming",
}

IMPLIES = {
    "mysql": ["sql"], "postgresql": ["sql"], "sqlite": ["sql"], "sql server": ["sql"],
    "pytorch": ["deep learning"], "tensorflow": ["deep learning"], "keras": ["deep learning"],
    "spring boot": ["java", "spring"],
    "fastapi": ["python"], "django": ["python"], "flask": ["python"],
    "llms": ["genai"],
}

GENERIC_WORDS = {"pipeline", "pipelines", "experience", "skills", "framework", "frameworks"}

def strip_generic_words(term: str) -> str:
    words = term.split()
    while len(words) > 1 and words[-1] in GENERIC_WORDS:
        words.pop()
    return " ".join(words)

def canonical_forms(term: str) -> set[str]:
    term = re.sub(r"\s+", " ", term.lower()).strip().rstrip(".")
    variants = {term, strip_generic_words(term)}
    inner = re.search(r"\(([^)]+)\)", term)
    if inner:
        variants.add(re.sub(r"\s*\([^)]*\)", "", term).strip())
        variants.add(inner.group(1).strip())
    return {ALIASES.get(variant, variant) for variant in variants if variant}

def add_implications(skills: set[str]) -> set[str]:
    expanded = set(skills)
    for skill in skills:
        expanded.update(IMPLIES.get(skill, []))
    return expanded

def build_resume_skill_set(resume_skills: list[str]) -> set[str]:
    skills = set()
    for skill in resume_skills:
        skills |= canonical_forms(skill)
    return add_implications(skills)

KEYWORD_CHECKABLE = {"technical"}
IMPORTANCE_WEIGHT = {"must_have": 2, "nice_to_have": 1}
MIN_TEXT_MATCH_LENGTH = 3

def text_forms(term: str) -> set[str]:
    forms = canonical_forms(term)
    forms |= {alias for alias, canonical in ALIASES.items() if canonical in forms}
    return forms

def appears_in_text(form: str, text: str) -> bool:
    if len(form) < MIN_TEXT_MATCH_LENGTH:
        return False
    return re.search(rf"(?<!\w){re.escape(form)}(?!\w)", text) is not None

def find_match(requirement: dict, skill_set: set[str], resume_text: str) -> str | None:
    options = [requirement["name"], *requirement.get("alternatives", [])]
    for option in options:
        if canonical_forms(option) & skill_set:
            return option
        if any(appears_in_text(form, resume_text) for form in text_forms(option)):
            return option
    return None

def match_requirements(requirements: list[dict], resume_skills: list[str], resume_text: str) -> dict:
    skill_set = build_resume_skill_set(resume_skills)
    text = resume_text.lower()

    results = []
    for requirement in requirements:
        matched_as = find_match(requirement, skill_set, text)
        if matched_as:
            status = "matched"
        elif requirement["category"] in KEYWORD_CHECKABLE:
            status = "missing"
        else:
            status = "needs_review"
        results.append({**requirement, "status": status, "matched_as": matched_as})

    checkable = [r for r in results if r["category"] in KEYWORD_CHECKABLE]
    total = sum(IMPORTANCE_WEIGHT[r["importance"]] for r in checkable)
    earned = sum(IMPORTANCE_WEIGHT[r["importance"]] for r in checkable if r["status"] == "matched")

    return {
        "requirements": results,
        "technical_coverage": round(100 * earned / total) if total else None,
        "matched": [r["name"] for r in results if r["status"] == "matched"],
        "missing": [r["name"] for r in results if r["status"] == "missing"],
        "needs_review": [r["name"] for r in results if r["status"] == "needs_review"],
    }