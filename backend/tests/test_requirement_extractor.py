from app.requirement_extractor import verify_quotes
from app.schemas import JobRequirements, Requirement

JD = """Requirements:
- 2+ years of professional experience with Python
- Hands-on experience with AWS, Azure or GCP"""

def make_job(quote):
    requirement = Requirement(name="Python", category="technical", importance="must_have", source_quote=quote)
    return JobRequirements(job_title="AI Engineer", requirements=[requirement])

def test_exact_quote_is_verified():
    result = verify_quotes(make_job("professional experience with Python"), JD)
    assert result[0]["quote_verified"] is True

def test_invented_quote_is_not_verified():
    result = verify_quotes(make_job("expert in Rust and Go"), JD)
    assert result[0]["quote_verified"] is False

def test_case_and_spacing_differences_are_ignored():
    result = verify_quotes(make_job("PROFESSIONAL   experience with python"), JD)
    assert result[0]["quote_verified"] is True