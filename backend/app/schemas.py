from pydantic import BaseModel, Field
from typing import Literal
    
class CritiquePoint(BaseModel):
    point: str
    evidence_ids: list[str] = Field(max_length=2)

class CompactRecommendation(BaseModel):
    priority: int
    action: str
    why: str

class CompactCritique(BaseModel):
    overall_match: Literal["strong", "moderate", "weak", "insufficient"]
    summary: str
    strengths: list[CritiquePoint] = Field(max_length=3)
    weak_areas: list[CritiquePoint] = Field(max_length=3)
    recommendations: list[CompactRecommendation] = Field(min_length=3, max_length=3)
    
class Requirement(BaseModel):
    name: str
    alternatives: list[str] = Field(default_factory=list)
    category: Literal["technical", "domain", "soft_skill", "qualification", "experience"]
    importance: Literal["must_have", "nice_to_have"]
    source_quote: str

class JobRequirements(BaseModel):
    job_title: str
    requirements: list[Requirement]