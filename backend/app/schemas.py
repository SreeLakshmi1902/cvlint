from pydantic import BaseModel, Field
from typing import List, Literal

class Strength(BaseModel):
    title:str
    explanation: str
    evidence: str

class MissingSkill(BaseModel):
    skill:str
    why_it_matters:str
    evidence: str
    
class ATSIssues(BaseModel):
    issue:str
    impact: str
    fix: str
    
class Recommendation(BaseModel):
    priority: int
    recommendation:str
    why:str
    how_to_improve: str
    
class ResumeCritique(BaseModel):
    overall_match: Literal["strong", "moderate", "weak", "insufficient"]
    summary: str
    strengths: List[Strength]
    missing_skills: List[MissingSkill]
    ats_issues: List[ATSIssues]
    recommendations: List[Recommendation] = Field(min_length=3, max_length=3)
    
class Requirement(BaseModel):
    name: str
    alternatives: list[str] = Field(default_factory=list)
    category: Literal["technical", "domain", "soft_skill", "qualification", "experience"]
    importance: Literal["must_have", "nice_to_have"]
    source_quote: str

class JobRequirements(BaseModel):
    job_title: str
    requirements: list[Requirement]