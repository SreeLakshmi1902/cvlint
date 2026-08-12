from pydantic import BaseModel
from typing import List

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
    overall_match: str
    summary: str
    strengths: List[Strength]
    missing_skills: List[MissingSkill]
    ats_issues: List[ATSIssues]
    recommendations: List[Recommendation]