import app.evidence as evidence

CHUNKS = [
    {"id": "summary_1", "section": "summary"},
    {"id": "experience_1", "section": "experience"},
    {"id": "experience_2", "section": "experience"},
    {"id": "education_1", "section": "education"},
]

def fake_search(query, chunks, top_k):
    return chunks[:top_k]

def test_verified_quote_is_the_query():
    requirement = {"name": "Python", "source_quote": "2+ years of Python", "quote_verified": True}
    assert evidence.requirement_query(requirement) == "2+ years of Python"

def test_name_is_the_query_when_quote_not_verified():
    requirement = {"name": "Python", "source_quote": "invented text", "quote_verified": False}
    assert evidence.requirement_query(requirement) == "Python"

def test_each_requirement_gets_its_own_search(monkeypatch):
    queries = []

    def recording_search(query, chunks, top_k):
        queries.append(query)
        return chunks[:top_k]

    monkeypatch.setattr(evidence, "hybrid_search", recording_search)
    requirements = [
        {"name": "Python", "source_quote": "Python", "quote_verified": True},
        {"name": "Docker", "source_quote": "Docker", "quote_verified": True},
    ]
    results = evidence.retrieve_evidence(requirements, CHUNKS, per_requirement=2)
    assert queries == ["Python", "Docker"]
    assert results[0]["candidate_ids"] == ["summary_1", "experience_1"]

def test_skipped_sections_are_never_evidence(monkeypatch):
    monkeypatch.setattr(evidence, "hybrid_search", fake_search)
    requirements = [{"name": "Python", "source_quote": "Python", "quote_verified": True}]
    results = evidence.retrieve_evidence(requirements, CHUNKS, per_requirement=2,
                                         skip_sections=("summary",))
    assert results[0]["candidate_ids"] == ["experience_1", "experience_2"]

def test_collected_evidence_has_each_bullet_once_in_resume_order():
    requirements = [
        {"candidate_ids": ["experience_2", "summary_1"]},
        {"candidate_ids": ["summary_1", "education_1"]},
    ]
    collected = evidence.collect_evidence(requirements, CHUNKS)
    assert [chunk["id"] for chunk in collected] == ["summary_1", "experience_2", "education_1"]